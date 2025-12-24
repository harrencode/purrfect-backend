# app/recommender/model.py
import joblib
import numpy as np
import pandas as pd
from typing import List, Dict, Any
import os
from sklearn.neighbors import NearestNeighbors

# Paths to your trained model 
MODEL_PATH = os.path.join(os.path.dirname(__file__), "scripts", "knn_model.pkl")
FEATURES_PATH = os.path.join(os.path.dirname(__file__), "scripts", "pet_features.pkl")


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not trained. Run training script.")
    model = joblib.load(MODEL_PATH)
    features = joblib.load(FEATURES_PATH)
    return model, features


def encode_preference(preference: Dict[str, Any], features_columns: List[str]):
    
    #Encode user preference into same feature vector space as pets.
    
    vec = pd.Series(0, index=features_columns, dtype=float)
    if preference.get("preferred_species"):
        col = f"species_{preference['preferred_species'].lower()}"
        if col in vec.index:
            vec[col] = 1
    if preference.get("preferred_size"):
        col = f"size_{preference['preferred_size'].lower()}"
        if col in vec.index:
            vec[col] = 1
    if preference.get("temperament"):
        col = f"temperament_{preference['temperament'].lower()}"
        if col in vec.index:
            vec[col] = 1
    if preference.get("activity_level"):
        col = f"energy_{preference['activity_level'].lower()}"
        if col in vec.index:
            vec[col] = 1
    return vec.values.reshape(1, -1)


def encode_pet_for_model(pet: Dict[str, Any], features_columns: List[str]):
    
    #Encode a pet dict from your DB into feature vector compatible with model.
    
    vec = pd.Series(0, index=features_columns, dtype=float)

    # species
    if pet.get("Species"):
        col = f"species_{pet['Species'].lower()}"
        if col in vec.index:
            vec[col] = 1

    # size
    if pet.get("Size"):
        col = f"size_{pet['Size'].lower()}"
        if col in vec.index:
            vec[col] = 1

    # temperament
    if pet.get("Temperament"):
        col = f"temperament_{pet['Temperament'].lower()}"
        if col in vec.index:
            vec[col] = 1

    # activity level
    if pet.get("ActivityLevel"):
        col = f"energy_{pet['ActivityLevel'].lower()}"
        if col in vec.index:
            vec[col] = 1

    # numeric features
    for num_feat in ['Age', 'Fee', 'Quantity', 'PhotoAmt', 'VideoAmt']:
        if num_feat in pet and num_feat in vec.index:
            vec[num_feat] = float(pet[num_feat])

    return vec.values


def recommend(preference: Dict[str, Any], pets_in_db: List[Dict[str, Any]], top_k: int = 5):
    
    #Recommend top_k pets based on user preference from pets currently in your DB.
    
    if not pets_in_db:
        return []

    # Load feature columns (from saved model)
    _, features = load_model()
    feature_cols = features["columns"]

    # Encode current DB pets
    X_candidates = [encode_pet_for_model(pet, feature_cols) for pet in pets_in_db]
    candidate_index = {i: pet for i, pet in enumerate(pets_in_db)}

    # Fit NearestNeighbors on current petsj
    nn = NearestNeighbors(n_neighbors=min(top_k, len(X_candidates)))
    nn.fit(X_candidates)

    # Encode user preference
    pref_vec = encode_preference(preference, feature_cols)

    # Get nearest neighbors
    distances, indices = nn.kneighbors(pref_vec)
    return [candidate_index[i] for i in indices[0]]


