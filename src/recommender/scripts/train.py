import os
import joblib
import numpy as np
import pandas as pd

from typing import Dict, List, Any

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TRAIN_CSV = os.path.join(DATA_DIR, "train.csv")

# Artifacts must land in the scripts/ folder because model.py loads them from scripts/
MODEL_OUT = os.path.join(os.path.dirname(__file__), "knn_model.pkl")
FEAT_OUT = os.path.join(os.path.dirname(__file__), "pet_features.pkl")
SCALER_OUT = os.path.join(os.path.dirname(__file__), "scaler.pkl")



# Feature schema: 
FEATURE_COLS = [
    "species_dog",
    "species_cat",
    "species_other",
    "size_small",
    "size_medium",
    "size_large",
    "temperament_calm",
    "temperament_playful",
    "temperament_friendly",
    "temperament_energetic",
    "temperament_gentle",
    "activity_low",
    "activity_moderate",
    "activity_high",
    "age_months",
]

REQUIRED_INPUT_COLS = [
    "pet_id",
    "name",
    "species",
    "age_months",
    "size",
    "temperament",
    "activity_level",
]


def _normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def preprocess(df: pd.DataFrame) -> tuple[np.ndarray, List[str], pd.DataFrame]:
    
    df = df.copy()

    missing = [c for c in REQUIRED_INPUT_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            "train.csv is missing required columns: "
            + ", ".join(missing)
            + "\nMinimum required columns are:\n  "
            + ", ".join(REQUIRED_INPUT_COLS)
        )

    for c in ["age_months"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).astype(float)

    species = df["species"].apply(_normalize)
    df["species_dog"] = (species == "dog").astype(int)
    df["species_cat"] = (species == "cat").astype(int)
    df["species_other"] = (species == "other").astype(int)

    size = df["size"].apply(_normalize)
    for value in ["small", "medium", "large"]:
        df[f"size_{value}"] = (size == value).astype(int)

    temperament = df["temperament"].apply(_normalize)
    for value in ["calm", "playful", "friendly", "energetic", "gentle"]:
        df[f"temperament_{value}"] = (temperament == value).astype(int)

    activity_level = df["activity_level"].apply(_normalize)
    for value in ["low", "moderate", "high"]:
        df[f"activity_{value}"] = (activity_level == value).astype(int)

    X = df[FEATURE_COLS].values.astype(float)
    return X, FEATURE_COLS, df


def build_pet_index(df: pd.DataFrame) -> Dict[int, Dict[str, Any]]:
    pet_index: Dict[int, Dict[str, Any]] = {}
    for i, row in df.iterrows():
        pet_index[int(i)] = {
            "PetID": row.get("pet_id"),
            "Name": row.get("name"),
            "Species": row.get("species"),
            "Size": row.get("size"),
            "Temperament": row.get("temperament"),
            "ActivityLevel": row.get("activity_level"),
            "age_months": float(row.get("age_months") or 0),
            "Breed": row.get("breed"),
            "Gender": row.get("gender"),
            "Color": row.get("color"),
            "Description": row.get("description"),
            "IsAdopted": row.get("is_adopted"),
        }
    return pet_index


def train_from_dataframe(df: pd.DataFrame) -> None:
    X_raw, feature_cols, df_feat = preprocess(df)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    n_neighbors = min(10, len(X_scaled))
    n_neighbors = max(1, int(n_neighbors))
    knn = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean")
    knn.fit(X_scaled)

    pet_index = build_pet_index(df_feat)

    features = {
        "columns": feature_cols,  
        "pet_index": pet_index,    
    }

    joblib.dump(knn, MODEL_OUT)
    joblib.dump(features, FEAT_OUT)
    joblib.dump(scaler, SCALER_OUT)

    print("Training finished")
    print("\nArtifacts saved:")
    print("  Model:   ", MODEL_OUT)
    print("  Features:", FEAT_OUT)
    print("  Scaler:  ", SCALER_OUT)
    print("\nFeature columns:\n  " + ", ".join(feature_cols))


def train_from_csv(csv_path: str = TRAIN_CSV) -> None:
    if not os.path.exists(csv_path):
        print("Dataset not found:", csv_path)
        print("Expected path: data/train.csv (relative to scripts/)")
        return

    train_from_dataframe(pd.read_csv(csv_path))


def main():
    train_from_csv()


if __name__ == "__main__":
    main()
