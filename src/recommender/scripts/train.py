import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, classification_report
from imblearn.over_sampling import SMOTE
import joblib
import os

# Paths
# DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TRAIN_CSV = os.path.join(DATA_DIR, "train.csv")
BREED_CSV = os.path.join(DATA_DIR, "breed_labels.csv")
COLOR_CSV = os.path.join(DATA_DIR, "color_labels.csv")
STATE_CSV = os.path.join(DATA_DIR, "state_labels.csv")

MODEL_OUT = os.path.join(os.path.dirname(__file__), "knn_model.pkl")
FEAT_OUT = os.path.join(os.path.dirname(__file__), "pet_features.pkl")
SCALER_OUT = os.path.join(os.path.dirname(__file__), "scaler.pkl")

def load_labels():
    breeds = pd.read_csv(BREED_CSV)
    colors = pd.read_csv(COLOR_CSV)
    states = pd.read_csv(STATE_CSV)
    breed_map = dict(zip(breeds["BreedID"], breeds["BreedName"]))
    color_map = dict(zip(colors["ColorID"], colors["ColorName"]))
    state_map = dict(zip(states["StateID"], states["StateName"]))
    return breed_map, color_map, state_map


def preprocess(df):
    df = df.copy()

    # Species, size, fur, health
    df["species_dog"] = (df["Type"] == 1).astype(int)
    df["species_cat"] = (df["Type"] == 2).astype(int)
    df["size_small"] = (df["MaturitySize"] == 1).astype(int)
    df["size_medium"] = (df["MaturitySize"] == 2).astype(int)
    df["size_large"] = (df["MaturitySize"] == 3).astype(int)
    df["size_xlarge"] = (df["MaturitySize"] == 4).astype(int)
    df["fur_short"] = (df["FurLength"] == 1).astype(int)
    df["fur_medium"] = (df["FurLength"] == 2).astype(int)
    df["fur_long"] = (df["FurLength"] == 3).astype(int)
    df["vaccinated"] = (df["Vaccinated"] == 1).astype(int)
    df["dewormed"] = (df["Dewormed"] == 1).astype(int)
    df["sterilized"] = (df["Sterilized"] == 1).astype(int)
    df["healthy"] = (df["Health"] == 1).astype(int)

    # Numeric features
    numeric_feats = ["Age", "Fee", "Quantity", "PhotoAmt", "VideoAmt"]
    df[numeric_feats] = df[numeric_feats].fillna(0).astype(float)

    # Description keywords
    def keyword_flag(desc, keyword):
        return int(keyword in str(desc).lower())
    df["desc_playful"] = df["Description"].apply(lambda d: keyword_flag(d, "playful"))
    df["desc_calm"] = df["Description"].apply(lambda d: keyword_flag(d, "calm"))
    df["desc_friendly"] = df["Description"].apply(lambda d: keyword_flag(d, "friendly"))

    # One-hot encode categorical columns
    cat_cols = ['Breed1', 'Breed2', 'Color1', 'Color2', 'Color3', 'State']
    df[cat_cols] = df[cat_cols].astype(str)
    df = pd.get_dummies(df, columns=cat_cols, dummy_na=True)

    # Final X and y
    X = df.select_dtypes(include=[np.number]).values
    y = df["AdoptionSpeed"].astype(int).values
    feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    return X, y, feature_cols



def build_pet_index(df, breed_map, color_map, state_map):
    pet_index = {}
    for i, row in df.iterrows():
        pet_index[i] = {
            "PetID": row["PetID"],
            "Name": row.get("Name"),
            "Species": "Dog" if row["Type"] == 1 else "Cat",
            "Breed1": breed_map.get(row["Breed1"], None),
            "Breed2": breed_map.get(row["Breed2"], None),
            "Age": row.get("Age"),
            "Color1": color_map.get(row["Color1"], None),
            "Color2": color_map.get(row["Color2"], None),
            "Color3": color_map.get(row["Color3"], None),
            "State": state_map.get(row["State"], None),
            "Description": row.get("Description"),
        }
    return pet_index


def main():
    if not os.path.exists(TRAIN_CSV):
        print("Dataset not found:", TRAIN_CSV)
        return

    df = pd.read_csv(TRAIN_CSV)
    breed_map, color_map, state_map = load_labels()

    X, y, feature_cols = preprocess(df)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Feature scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)


    # Balance classes using SMOTE
    sm = SMOTE(random_state=42)
    X_train_res, y_train_res = sm.fit_resample(X_train_scaled, y_train)

    
    # Fit KNN classifier
    knn = KNeighborsClassifier(n_neighbors=10, metric="euclidean")
    knn.fit(X_train_res, y_train_res)

    # Predictions
    y_pred = knn.predict(X_test_scaled)

    # Metrics
    acc = accuracy_score(y_test, y_pred)

    prec_w = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec_w = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1_w = f1_score(y_test, y_pred, average="weighted")

    prec_m = precision_score(y_test, y_pred, average="macro", zero_division=0)
    rec_m = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1_m = f1_score(y_test, y_pred, average="macro")

    cm = confusion_matrix(y_test, y_pred)

    print("Training finished")
    print(f"Accuracy: {acc:.4f}\n")

    print("Weighted metrics:")
    print(f"  Precision (weighted): {prec_w:.4f}")
    print(f"  Recall (weighted):    {rec_w:.4f}")
    print(f"  F1-score (weighted):  {f1_w:.4f}\n")

    print("Macro metrics:")
    print(f"  Precision (macro): {prec_m:.4f}")
    print(f"  Recall (macro):    {rec_m:.4f}")
    print(f"  F1-score (macro):  {f1_m:.4f}\n")

    print("Confusion Matrix:\n", cm)
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Pet metadata index
    pet_index = build_pet_index(df, breed_map, color_map, state_map)
    features = {"columns": feature_cols, "pet_index": pet_index}

    joblib.dump(knn, MODEL_OUT)
    joblib.dump(features, FEAT_OUT)
    joblib.dump(scaler, SCALER_OUT)

    print("\nModel saved to", MODEL_OUT)
    print("Features saved to", FEAT_OUT)
    print("Scaler saved to", SCALER_OUT)


if __name__ == "__main__":
    main()
