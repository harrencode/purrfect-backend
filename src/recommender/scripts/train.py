import os
import joblib
import numpy as np
import pandas as pd

from typing import Optional, Dict, Tuple, List, Any

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    classification_report,
)

# Optional: SMOTE for imbalanced classes 
try:
    from imblearn.over_sampling import SMOTE  # type: ignore
    _HAS_SMOTE = True
except Exception:
    SMOTE = None  # type: ignore
    _HAS_SMOTE = False



# Paths 


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TRAIN_CSV = os.path.join(DATA_DIR, "train.csv")

BREED_CSV = os.path.join(DATA_DIR, "breed_labels.csv")
COLOR_CSV = os.path.join(DATA_DIR, "color_labels.csv")
STATE_CSV = os.path.join(DATA_DIR, "state_labels.csv")

# Artifacts must land in the scripts/ folder because model.py loads them from scripts/
MODEL_OUT = os.path.join(os.path.dirname(__file__), "knn_model.pkl")
FEAT_OUT = os.path.join(os.path.dirname(__file__), "pet_features.pkl")
SCALER_OUT = os.path.join(os.path.dirname(__file__), "scaler.pkl")



# Feature schema: 
FEATURE_COLS = [
    # one-hot species
    "species_dog",
    "species_cat",
    # one-hot size
    "size_small",
    "size_medium",
    "size_large",
    "size_xlarge",
    # one-hot temperament keywords
    "desc_calm",
    "desc_friendly",
    "desc_playful",
    # numeric
    "Age",
    "Fee",
    "Quantity",
    "PhotoAmt",
    "VideoAmt",
]

REQUIRED_INPUT_COLS = [
    "PetID",
    "Type",
    "MaturitySize",
    "Age",
    "Fee",
    "Quantity",
    "PhotoAmt",
    "VideoAmt",
    "Description",
    "AdoptionSpeed",
]


def _safe_read_map(path: str, key_col: str, val_col: str) -> Dict[Any, Any]:
    if not os.path.exists(path):
        return {}
    df = pd.read_csv(path)
    if key_col not in df.columns or val_col not in df.columns:
        return {}
    return dict(zip(df[key_col], df[val_col]))


def load_label_maps() -> Tuple[Dict[Any, Any], Dict[Any, Any], Dict[Any, Any]]:
    breed_map = _safe_read_map(BREED_CSV, "BreedID", "BreedName")
    color_map = _safe_read_map(COLOR_CSV, "ColorID", "ColorName")
    state_map = _safe_read_map(STATE_CSV, "StateID", "StateName")
    return breed_map, color_map, state_map


def infer_temperament_from_description(desc: Any) -> Optional[str]:
    
    d = str(desc or "").lower()
    
    if "playful" in d:
        return "playful"
    if "friendly" in d:
        return "friendly"
    if "calm" in d:
        return "calm"
    return None


def _size_str(maturity_size: Any) -> Optional[str]:
    try:
        ms = int(float(maturity_size))
    except Exception:
        return None
    return {1: "small", 2: "medium", 3: "large", 4: "xlarge"}.get(ms)


def _species_str(pet_type: Any) -> Optional[str]:
    try:
        t = int(float(pet_type))
    except Exception:
        return None
    if t == 1:
        return "Dog"
    if t == 2:
        return "Cat"
    return None


def preprocess(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str], pd.DataFrame]:
    
    df = df.copy()

    missing = [c for c in REQUIRED_INPUT_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            "train.csv is missing required columns: "
            + ", ".join(missing)
            + "\nMinimum required columns are:\n  "
            + ", ".join(REQUIRED_INPUT_COLS)
        )

    # Numeric cleanup
    for c in ["Age", "Fee", "Quantity", "PhotoAmt", "VideoAmt"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).astype(float)

    # One-hot: species
    t = pd.to_numeric(df["Type"], errors="coerce").fillna(0).astype(int)
    df["species_dog"] = (t == 1).astype(int)
    df["species_cat"] = (t == 2).astype(int)

    # One-hot: size
    ms = pd.to_numeric(df["MaturitySize"], errors="coerce").fillna(0).astype(int)
    df["size_small"] = (ms == 1).astype(int)
    df["size_medium"] = (ms == 2).astype(int)
    df["size_large"] = (ms == 3).astype(int)
    df["size_xlarge"] = (ms == 4).astype(int)

    # Derive temperament & encode to desc_*
    df["Temperament"] = df["Description"].apply(infer_temperament_from_description)
    for tag in ["calm", "friendly", "playful"]:
        df["desc_" + tag] = (df["Temperament"] == tag).astype(int)

    X = df[FEATURE_COLS].values.astype(float)
    y = pd.to_numeric(df["AdoptionSpeed"], errors="coerce").fillna(0).astype(int).values
    return X, y, FEATURE_COLS, df


def build_pet_index(
    df: pd.DataFrame,
    breed_map: Optional[Dict[Any, Any]] = None,
    color_map: Optional[Dict[Any, Any]] = None,
    state_map: Optional[Dict[Any, Any]] = None,
) -> Dict[int, Dict[str, Any]]:
    
    breed_map = breed_map or {}
    color_map = color_map or {}
    state_map = state_map or {}

    def _maybe_map(m: Dict[Any, Any], v: Any) -> Any:
        try:
            iv = int(float(v))
        except Exception:
            return v
        return m.get(iv, v)

    pet_index: Dict[int, Dict[str, Any]] = {}
    for i, row in df.iterrows():
        desc = row.get("Description")
        temp = infer_temperament_from_description(desc)

        pet_index[int(i)] = {
            "PetID": row.get("PetID"),
            "Name": row.get("Name"),
            "Species": _species_str(row.get("Type")),
            "Size": _size_str(row.get("MaturitySize")),
            "Temperament": temp,
            # numeric features 
            "Age": float(row.get("Age") or 0),
            "Fee": float(row.get("Fee") or 0),
            "Quantity": float(row.get("Quantity") or 0),
            "PhotoAmt": float(row.get("PhotoAmt") or 0),
            "VideoAmt": float(row.get("VideoAmt") or 0),
            # extra metadata (optional)
            "Breed1": _maybe_map(breed_map, row.get("Breed1")),
            "Breed2": _maybe_map(breed_map, row.get("Breed2")),
            "Color1": _maybe_map(color_map, row.get("Color1")),
            "Color2": _maybe_map(color_map, row.get("Color2")),
            "Color3": _maybe_map(color_map, row.get("Color3")),
            "State": _maybe_map(state_map, row.get("State")),
            "Description": desc,
        }
    return pet_index


def _safe_train_test_split(
    X: np.ndarray, y: np.ndarray, test_size: float = 0.2, random_state: int = 42
) -> Tuple[np.ndarray, Optional[np.ndarray], np.ndarray, Optional[np.ndarray]]:
    
    n = len(y)
    classes = np.unique(y)
    n_classes = len(classes)

    if n < 5 or n_classes < 2:
        return X, None, y, None  

    # Stratified split needs test set
    min_test_needed = n_classes
    est_test = int(np.ceil(test_size * n))
    if est_test < min_test_needed:
        test_size = min(0.5, max(test_size, float(min_test_needed) / float(n)))

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        return X_train, X_test, y_train, y_test
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=None
        )
        return X_train, X_test, y_train, y_test


def maybe_apply_smote(X_train_scaled: np.ndarray, y_train: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
   
    if not _HAS_SMOTE:
        return X_train_scaled, y_train

    vc = pd.Series(y_train).value_counts()
    if len(vc) < 2:
        return X_train_scaled, y_train

    min_count = int(vc.min())
    # SMOTE requires k_neighbors < min_count
    if min_count < 3:
        return X_train_scaled, y_train

    k_neighbors = min(5, min_count - 1)
    try:
        sm = SMOTE(random_state=42, k_neighbors=k_neighbors)
        X_res, y_res = sm.fit_resample(X_train_scaled, y_train)
        return X_res, y_res
    except Exception:
        return X_train_scaled, y_train


def main():
    if not os.path.exists(TRAIN_CSV):
        print("Dataset not found:", TRAIN_CSV)
        print("Expected path: data/train.csv (relative to scripts/)")
        return

    df = pd.read_csv(TRAIN_CSV)

    
    X_raw, y, feature_cols, df_feat = preprocess(df)

    # Train/test split 
    X_train_raw, X_test_raw, y_train, y_test = _safe_train_test_split(X_raw, y, test_size=0.2, random_state=42)

    # Scale using ONLY train data 
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_raw)
    X_test_scaled = scaler.transform(X_test_raw) if X_test_raw is not None else None

    # Optional SMOTE
    X_train_final, y_train_final = maybe_apply_smote(X_train_scaled, y_train)

    # Fit KNN classifier 
    n_neighbors = min(10, len(X_train_final))
    n_neighbors = max(1, int(n_neighbors))
    knn = KNeighborsClassifier(n_neighbors=n_neighbors, metric="euclidean")
    knn.fit(X_train_final, y_train_final)

    # Evaluate 
    if X_test_scaled is not None and y_test is not None and len(y_test) > 0:
        y_pred = knn.predict(X_test_scaled)

        acc = accuracy_score(y_test, y_pred)
        prec_w = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec_w = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1_w = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        print("Training finished")
        print("Accuracy: {:.4f}\n".format(acc))
        print("Weighted metrics:")
        print("  Precision (weighted): {:.4f}".format(prec_w))
        print("  Recall (weighted):    {:.4f}".format(rec_w))
        print("  F1-score (weighted):  {:.4f}\n".format(f1_w))

        print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
        print("\nClassification Report:\n", classification_report(y_test, y_pred))
    else:
        print("Training finished (no held-out test set; dataset is small).")

    
    breed_map, color_map, state_map = load_label_maps()

    # Pet metadata index 
    pet_index = build_pet_index(df_feat, breed_map, color_map, state_map)

    features = {
        "columns": feature_cols,  
        "pet_index": pet_index,    
    }

    joblib.dump(knn, MODEL_OUT)
    joblib.dump(features, FEAT_OUT)
    joblib.dump(scaler, SCALER_OUT)

    print("\nArtifacts saved:")
    print("  Model:   ", MODEL_OUT)
    print("  Features:", FEAT_OUT)
    print("  Scaler:  ", SCALER_OUT)
    print("\nFeature columns:\n  " + ", ".join(feature_cols))


if __name__ == "__main__":
    main()
