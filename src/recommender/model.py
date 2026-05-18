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
        col = f"temperament_{t}"
        if col in vec.index:
            vec[col] = 1

    activity_level = _get(preference, "activity_level", "ActivityLevel")
    if isinstance(activity_level, str):
        level = activity_level.strip().lower()
        col = f"activity_{level}"
        if col in vec.index:
            vec[col] = 1

    min_age = _get(preference, "min_age", "MinAge")
    max_age = _get(preference, "max_age", "MaxAge")
    if min_age is not None and max_age is not None and "age_months" in vec.index:
        vec["age_months"] = (float(min_age) + float(max_age)) / 2.0
    elif min_age is not None and "age_months" in vec.index:
        vec["age_months"] = float(min_age)
    elif max_age is not None and "age_months" in vec.index:
        vec["age_months"] = float(max_age)

    # Backwards compatible numeric aliases.
    for num_feat in ["age_months", "Age"]:
        val = _get(preference, num_feat, num_feat.lower())
        target = "age_months" if num_feat == "Age" else num_feat
        if val is not None and target in vec.index:
            vec[target] = float(val)

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
        col = f"temperament_{t}"
        if col in vec.index:
            vec[col] = 1

    activity_level = _get(pet, "ActivityLevel", "activity_level")
    if isinstance(activity_level, str):
        level = activity_level.strip().lower()
        col = f"activity_{level}"
        if col in vec.index:
            vec[col] = 1

    # Backwards compatible numeric aliases.
    for num_feat in ["age_months", "Age"]:
        val = _get(pet, num_feat, num_feat.lower())
        target = "age_months" if num_feat == "Age" else num_feat
        if val is not None and target in vec.index:
            vec[target] = float(val)

    return vec.values  


def recommend(preference: Dict[str, Any], pets_in_db: List[Dict[str, Any]], top_k: int = 5):
    if not pets_in_db:
        return []

    _, features, scaler = load_model()
    feature_cols = features["columns"]

    # Encode pets
    X_candidates = np.vstack([encode_pet_for_model(p, feature_cols) for p in pets_in_db])  

    pref_vec = encode_preference(preference, feature_cols).copy()
    if "age_months" in feature_cols and not any(
        preference.get(key) is not None for key in ("age_months", "Age", "min_age", "max_age", "MinAge", "MaxAge")
    ):
        age_idx = feature_cols.index("age_months")
        pref_vec[0, age_idx] = scaler.mean_[age_idx]

    
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


#python -m src.recommender.scripts.train