import json
from pathlib import Path

import joblib

from app.ml_models.fertilizer_model import (
    train_fertilizer_model
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = (
    BASE_DIR /
    "saved_models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_PATH = (
    MODEL_DIR /
    "fertilizer_random_forest.pkl"
)

METADATA_PATH = (
    MODEL_DIR /
    "fertilizer_model_metadata.json"
)


# =========================================================
# TRAIN MODEL
# =========================================================

print()
print("=" * 60)
print("TRAINING FERTILIZER RANDOM FOREST MODEL")
print("=" * 60)
print()

model, accuracy = train_fertilizer_model()


# =========================================================
# SAVE MODEL
# =========================================================

joblib.dump(
    model,
    MODEL_PATH
)


# =========================================================
# SAVE METADATA
# =========================================================

metadata = {

    "model": "RandomForestClassifier",

    "dataset": "fertilizer_data.csv",

    "records": 50000,

    "features": [

        "nitrogen",

        "phosphorus",

        "potassium",

        "moisture",

        "temperature"

    ],

    "target": "recommended_fertilizer",

    "accuracy": round(
        float(accuracy) * 100,
        2
    ),

    "n_estimators": 200,

    "random_state": 42

}


with open(
    METADATA_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        metadata,
        file,
        indent=4
    )


# =========================================================
# RESULT
# =========================================================

print()
print("=" * 60)
print("FERTILIZER MODEL TRAINING COMPLETE")
print("=" * 60)

print()

print(
    f"Accuracy : "
    f"{metadata['accuracy']}%"
)

print()

print(
    f"Model saved to:"
)

print(
    MODEL_PATH
)

print()

print(
    f"Metadata saved to:"
)

print(
    METADATA_PATH
)

print()

print("=" * 60)