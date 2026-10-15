import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from app.services.dataset_service import load_fertilizer_data


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "saved_models"

MODEL_PATH = MODEL_DIR / "fertilizer_random_forest.pkl"
METADATA_PATH = MODEL_DIR / "fertilizer_model_metadata.json"


# =========================================================
# FEATURES — NO pH
# =========================================================

FEATURE_NAMES = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "moisture",
    "temperature",
]


# =========================================================
# CACHED MODEL
# =========================================================

_FERTILIZER_MODEL = None


# =========================================================
# PREPARE DATA
# =========================================================

def prepare_fertilizer_data():
    dataset = load_fertilizer_data()

    if dataset is None or dataset.empty:
        raise ValueError("Fertilizer dataset is empty.")

    required_columns = FEATURE_NAMES + [
        "recommended_fertilizer"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in dataset.columns
    ]

    if missing_columns:
        raise ValueError(
            "Fertilizer dataset is missing columns: "
            + ", ".join(missing_columns)
        )

    dataset = dataset.copy()

    for column in FEATURE_NAMES:
        dataset[column] = pd.to_numeric(
            dataset[column],
            errors="coerce",
        )

    dataset["recommended_fertilizer"] = (
        dataset["recommended_fertilizer"]
        .astype(str)
        .str.strip()
    )

    dataset = dataset.dropna(
        subset=FEATURE_NAMES
    )

    dataset = dataset[
        dataset["recommended_fertilizer"].str.len() > 0
    ]

    valid_rows = np.isfinite(
        dataset[FEATURE_NAMES].to_numpy(dtype=float)
    ).all(axis=1)

    dataset = dataset.loc[valid_rows]

    if len(dataset) < 2:
        raise ValueError(
            "Not enough valid fertilizer dataset records."
        )

    X = dataset[FEATURE_NAMES].astype(float)

    y = dataset["recommended_fertilizer"]

    if y.nunique() < 2:
        raise ValueError(
            "Fertilizer dataset must contain at least "
            "two different fertilizer classes."
        )

    return X, y


# =========================================================
# TRAIN MODEL
# =========================================================

def train_fertilizer_model():
    global _FERTILIZER_MODEL

    X, y = prepare_fertilizer_data()

    class_counts = y.value_counts()
    use_stratify = class_counts.min() >= 2

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y if use_stratify else None,
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
        min_samples_leaf=1,
        n_jobs=-1,
    )

    print("=" * 60)
    print("TRAINING FERTILIZER RANDOM FOREST MODEL")
    print("=" * 60)
    print(f"Training records: {len(X_train)}")
    print(f"Testing records : {len(X_test)}")
    print(f"Features        : {FEATURE_NAMES}")
    print(f"Classes         : {y.nunique()}")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
        compress=3,
    )

    metadata = {
        "model": "Random Forest Classifier",
        "accuracy": float(accuracy),
        "accuracy_percent": round(accuracy * 100, 2),
        "dataset_records": int(len(X)),
        "training_records": int(len(X_train)),
        "testing_records": int(len(X_test)),
        "features": FEATURE_NAMES,
        "feature_count": len(FEATURE_NAMES),
        "classes": sorted(y.unique().tolist()),
        "class_count": int(y.nunique()),
        "n_estimators": 100,
        "random_state": 42,
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metadata, file, indent=4)

    _FERTILIZER_MODEL = model

    print("=" * 60)
    print("FERTILIZER MODEL TRAINED")
    print(f"Dataset records: {len(X)}")
    print(f"Features       : {len(FEATURE_NAMES)}")
    print(f"Accuracy       : {accuracy * 100:.2f}%")
    print(f"Model saved    : {MODEL_PATH}")
    print("=" * 60)

    return model, accuracy


# =========================================================
# LOAD SAVED MODEL
# =========================================================

def load_fertilizer_model():
    global _FERTILIZER_MODEL

    if _FERTILIZER_MODEL is not None:
        return _FERTILIZER_MODEL

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Saved fertilizer model not found: {MODEL_PATH}. "
            "Train the fertilizer model before starting the application."
        )

    try:
        print("Loading fertilizer model...")

        model = joblib.load(MODEL_PATH)

        if not hasattr(model, "predict"):
            raise ValueError(
                "Saved fertilizer file is not a valid prediction model."
            )

        # Validate the saved model's feature count.
        expected_count = len(FEATURE_NAMES)
        model_count = getattr(
            model,
            "n_features_in_",
            None,
        )

        if model_count is not None and model_count != expected_count:
            raise ValueError(
                f"Saved fertilizer model expects {model_count} features, "
                f"but the application uses {expected_count}. "
                "Retrain the model using the current five-feature dataset."
            )

        # Validate feature names if available.
        model_features = getattr(
            model,
            "feature_names_in_",
            None,
        )

        if model_features is not None:
            if list(model_features) != FEATURE_NAMES:
                raise ValueError(
                    "Saved fertilizer model feature names do not match "
                    "the current five-feature configuration. "
                    "Retrain the model."
                )

        _FERTILIZER_MODEL = model

        print("Fertilizer model loaded successfully.")
        print("Fertilizer features:", FEATURE_NAMES)

        return _FERTILIZER_MODEL

    except Exception as error:
        print("Unable to load fertilizer model.")
        print(f"Reason: {error}")
        raise


# =========================================================
# LOAD MODEL ACCURACY
# =========================================================

def load_fertilizer_accuracy():
    if not METADATA_PATH.exists():
        return 0.0

    try:
        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            metadata = json.load(file)

        return float(metadata.get("accuracy", 0.0))

    except Exception as error:
        print(
            "Unable to load fertilizer metadata:",
            error,
        )
        return 0.0


# =========================================================
# PREDICT FERTILIZER
# =========================================================

def predict_fertilizer(features):
    try:
        features = np.asarray(
            features,
            dtype=np.float64,
        )
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Fertilizer input must contain numeric values."
        ) from error

    if features.ndim == 1:
        features = features.reshape(1, -1)

    if features.ndim != 2:
        raise ValueError(
            "Fertilizer input must contain one or more rows of features."
        )

    expected_count = len(FEATURE_NAMES)

    if features.shape[1] != expected_count:
        raise ValueError(
            f"Expected {expected_count} fertilizer features "
            f"({', '.join(FEATURE_NAMES)}), "
            f"but received {features.shape[1]}."
        )

    if not np.isfinite(features).all():
        raise ValueError(
            "Fertilizer input contains invalid numeric values."
        )

    features_df = pd.DataFrame(
        features,
        columns=FEATURE_NAMES,
    )

    model = load_fertilizer_model()

    try:
        prediction = model.predict(features_df)[0]
    except Exception as error:
        print("Fertilizer model prediction error:", error)
        raise RuntimeError(
            "Unable to make fertilizer prediction."
        ) from error

    accuracy = load_fertilizer_accuracy()
    confidence = 0.0

    if hasattr(model, "predict_proba"):
        try:
            probabilities = model.predict_proba(features_df)[0]

            if len(probabilities) > 0:
                confidence = float(np.max(probabilities)) * 100

        except Exception as error:
            print(
                "Unable to calculate fertilizer prediction confidence:",
                error,
            )

    return {
        "fertilizer": str(prediction),
        "accuracy": round(accuracy * 100, 2),
        "confidence": round(confidence, 2),
    }