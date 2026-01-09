import joblib
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
import os
from sklearn.neighbors import NearestNeighbors

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")
MODEL_PATH = os.path.join(SCRIPTS_DIR, "knn_model.pkl")
FEATURES_PATH = os.path.join(SCRIPTS_DIR, "pet_features.pkl")
SCALER_PATH = os.path.join(SCRIPTS_DIR, "scaler.pkl")


def load_model() -> Tuple[Any, Dict[str, Any], Any]:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not trained. Run training script.")
    if not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError("Features not found. Run training script.")
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError("Scaler not found. Run training script.")

    model = joblib.load(MODEL_PATH)
    features = joblib.load(FEATURES_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, features, scaler


def _get(pet_or_pref: Dict[str, Any], *keys, default=None):
    
    for k in keys:
        if k in pet_or_pref and pet_or_pref[k] is not None:
            return pet_or_pref[k]
    return default


def encode_preference(preference: Dict[str, Any], features_columns: List[str]) -> np.ndarray:
    
    vec = pd.Series(0.0, index=features_columns, dtype=float)

    species = _get(preference, "preferred_species", "PreferredSpecies")
    if isinstance(species, str):
        s = species.strip().lower()
        if s == "dog" and "species_dog" in vec.index:
            vec["species_dog"] = 1
        elif s == "cat" and "species_cat" in vec.index:
            vec["species_cat"] = 1

    size = _get(preference, "preferred_size", "PreferredSize")
    if isinstance(size, str):
        sz = size.strip().lower()
        col = f"size_{sz}"
        if col in vec.index:
            vec[col] = 1

    
    temperament = _get(preference, "temperament", "Temperament")
    if isinstance(temperament, str):
        t = temperament.strip().lower()
        if t in ("calm", "friendly", "playful"):
            desc_col = f"desc_{t}"
            if desc_col in vec.index:
                vec[desc_col] = 1

    # numeric preferences 
    for num_feat in ["Age", "Fee", "Quantity", "PhotoAmt", "VideoAmt"]:
        val = _get(preference, num_feat, num_feat.lower())
        if val is not None and num_feat in vec.index:
            vec[num_feat] = float(val)

    return vec.values.reshape(1, -1)


def encode_pet_for_model(pet: Dict[str, Any], features_columns: List[str]) -> np.ndarray:
   
    vec = pd.Series(0.0, index=features_columns, dtype=float)

    species = _get(pet, "Species", "species")
    if isinstance(species, str):
        s = species.strip().lower()
        if s == "dog" and "species_dog" in vec.index:
            vec["species_dog"] = 1
        elif s == "cat" and "species_cat" in vec.index:
            vec["species_cat"] = 1

    size = _get(pet, "Size", "size")
    if isinstance(size, str):
        sz = size.strip().lower()
        col = f"size_{sz}"
        if col in vec.index:
            vec[col] = 1

    temperament = _get(pet, "Temperament", "temperament")
    if isinstance(temperament, str):
        t = temperament.strip().lower()
        if t in ("calm", "friendly", "playful"):
            desc_col = f"desc_{t}"
            if desc_col in vec.index:
                vec[desc_col] = 1

    # numeric features 
    for num_feat in ["Age", "Fee", "Quantity", "PhotoAmt", "VideoAmt"]:
        val = _get(pet, num_feat, num_feat.lower())
        if val is not None and num_feat in vec.index:
            vec[num_feat] = float(val)

    return vec.values  


def recommend(preference: Dict[str, Any], pets_in_db: List[Dict[str, Any]], top_k: int = 5):
    if not pets_in_db:
        return []

    _, features, scaler = load_model()
    feature_cols = features["columns"]

    # Encode pets
    X_candidates = np.vstack([encode_pet_for_model(p, feature_cols) for p in pets_in_db])  

    # Encode preference
    pref_vec = encode_preference(preference, feature_cols)  

    
    X_candidates_scaled = scaler.transform(X_candidates)
    pref_scaled = scaler.transform(pref_vec)

    nn = NearestNeighbors(n_neighbors=min(top_k, len(pets_in_db)), metric="euclidean")
    nn.fit(X_candidates_scaled)

    distances, indices = nn.kneighbors(pref_scaled)

    results = []
    for rank, idx in enumerate(indices[0]):
        pet = pets_in_db[idx]
        results.append(pet)

    return results
