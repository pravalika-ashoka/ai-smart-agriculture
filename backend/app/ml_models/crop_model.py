from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from app.services.dataset_service import load_crop_data


# =========================================================
# MODEL CONFIGURATION
# =========================================================

FEATURE_COLUMNS = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "temperature",
    "humidity",
    "rainfall",
]

TARGET_COLUMN = "crop"


# =========================================================
# MODEL PATH
# =========================================================

MODEL_DIR = (
    Path(__file__).resolve().parent
    / "saved_models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_PATH = (
    MODEL_DIR
    / "crop_random_forest.pkl"
)


# =========================================================
# CACHED MODEL
# =========================================================

_CROP_MODEL = None


# =========================================================
# TRAIN MODEL
# =========================================================

def train_crop_model():

    """
    Train the Random Forest crop recommendation model.

    IMPORTANT:
    This function should be executed locally.

    The generated crop_random_forest.pkl
    should then be deployed to Render.
    """

    dataset = load_crop_data()

    if dataset is None or dataset.empty:
        raise ValueError(
            "Crop dataset is empty."
        )

    # =====================================================
    # REQUIRED COLUMNS
    # =====================================================

    required_columns = (
        FEATURE_COLUMNS
        + [TARGET_COLUMN]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in dataset.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing columns in crop dataset: "
            + ", ".join(missing_columns)
        )

    dataset = dataset.copy()

    # =====================================================
    # NUMERIC CONVERSION
    # =====================================================

    for column in FEATURE_COLUMNS:

        dataset[column] = pd.to_numeric(
            dataset[column],
            errors="coerce"
        )

    # =====================================================
    # CLEAN CROP LABELS
    # =====================================================

    dataset[TARGET_COLUMN] = (
        dataset[TARGET_COLUMN]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # =====================================================
    # REMOVE INVALID RECORDS
    # =====================================================

    dataset = dataset.dropna(
        subset=FEATURE_COLUMNS + [TARGET_COLUMN]
    )

    dataset = dataset[
        dataset[TARGET_COLUMN] != ""
    ]

    if dataset.empty:
        raise ValueError(
            "No valid crop records available."
        )

    # =====================================================
    # FEATURES / TARGET
    # =====================================================

    X = dataset[
        FEATURE_COLUMNS
    ]

    y = dataset[
        TARGET_COLUMN
    ]

    # =====================================================
    # TRAIN / TEST SPLIT
    # =====================================================

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    # =====================================================
    # RANDOM FOREST
    # =====================================================
    #
    # Reduced model size for deployment.
    #
    # 75 trees
    # max_depth=20
    #
    # This keeps the model lighter than an unlimited-depth
    # forest while retaining good classification ability.
    # =====================================================

    model = RandomForestClassifier(
    n_estimators=40,
    max_depth=18,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=1,
    class_weight="balanced",
    )

    # =====================================================
    # TRAIN
    # =====================================================

    model.fit(
        X_train,
        y_train
    )

    # =====================================================
    # EVALUATE
    # =====================================================

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    # =====================================================
    # MODEL INFORMATION
    # =====================================================

    model_data = {

        "model":
            model,

        "features":
            FEATURE_COLUMNS,

        "accuracy":
            float(accuracy),

        "dataset_records":
            int(len(dataset)),

        "crop_classes":
            sorted(
                y.unique().tolist()
            )

    }

    # =====================================================
    # SAVE MODEL
    # =====================================================

    joblib.dump(

        model_data,

        MODEL_PATH,

        compress=3

    )

    # =====================================================
    # OUTPUT
    # =====================================================

    print()
    print("=" * 60)
    print("CROP MODEL TRAINED")
    print("=" * 60)

    print(
        f"Dataset records : {len(dataset)}"
    )

    print(
        f"Features        : {len(FEATURE_COLUMNS)}"
    )

    print(
        f"Crop classes    : {len(y.unique())}"
    )

    print(
        f"Accuracy        : {accuracy * 100:.2f}%"
    )

    print(
        f"Model saved     : {MODEL_PATH}"
    )

    print("=" * 60)

    return model_data


# =========================================================
# LOAD MODEL
# =========================================================

def load_crop_model():

    """
    Load the trained crop model once.

    The model is NOT trained automatically.

    This is important for Render because training a
    50,000-record Random Forest during a web request
    can consume significant RAM.
    """

    global _CROP_MODEL

    # =====================================================
    # RETURN CACHED MODEL
    # =====================================================

    if _CROP_MODEL is not None:
        return _CROP_MODEL

    # =====================================================
    # CHECK MODEL FILE
    # =====================================================

    if not MODEL_PATH.exists():

        raise FileNotFoundError(

            f"Crop model not found: {MODEL_PATH}. "

            "Train the model locally and deploy "
            "crop_random_forest.pkl."

        )

    # =====================================================
    # LOAD
    # =====================================================

    try:

        print(
            "Loading crop model..."
        )

        model_data = joblib.load(
            MODEL_PATH
        )

        # =================================================
        # VALIDATE MODEL PACKAGE
        # =================================================

        if not isinstance(
            model_data,
            dict
        ):
            raise ValueError(
                "Invalid crop model format."
            )

        if "model" not in model_data:
            raise ValueError(
                "Crop model package does not contain 'model'."
            )

        if "features" not in model_data:
            raise ValueError(
                "Crop model package does not contain 'features'."
            )

        if "crop_classes" not in model_data:
            raise ValueError(
                "Crop model package does not contain 'crop_classes'."
            )

        model = model_data["model"]

        # =================================================
        # FEATURE VALIDATION
        # =================================================

        saved_features = model_data["features"]

        if saved_features != FEATURE_COLUMNS:

            raise ValueError(

                "Crop model feature mismatch. "

                f"Expected: {FEATURE_COLUMNS}. "

                f"Found: {saved_features}."

            )

        # =================================================
        # CACHE
        # =================================================

        _CROP_MODEL = model_data

        print(
            "Crop model loaded successfully."
        )

        print(
            f"Dataset records: "
            f"{model_data.get('dataset_records', 0)}"
        )

        print(
            f"Crop classes: "
            f"{len(model_data.get('crop_classes', []))}"
        )

        print(
            f"Accuracy: "
            f"{model_data.get('accuracy', 0) * 100:.2f}%"
        )

        return _CROP_MODEL

    except FileNotFoundError:
        raise

    except Exception as error:

        print(
            "Unable to load crop model."
        )

        print(
            f"Reason: {error}"
        )

        raise RuntimeError(

            f"Crop model could not be loaded: {error}"

        ) from error


# =========================================================
# PREDICT CROP
# =========================================================

def predict_crop(features):

    """
    Predict the most suitable crop.

    Expected order:

    1. nitrogen
    2. phosphorus
    3. potassium
    4. temperature
    5. humidity
    6. rainfall
    """

    # =====================================================
    # CONVERT INPUT
    # =====================================================

    features = np.asarray(
        features,
        dtype=np.float32
    )

    # =====================================================
    # HANDLE 2D INPUT
    # =====================================================

    if features.ndim == 2:

        if features.shape[0] != 1:

            raise ValueError(
                "Crop prediction expects "
                "one input record."
            )

        features = features[0]

    # =====================================================
    # DIMENSION VALIDATION
    # =====================================================

    if features.ndim != 1:

        raise ValueError(
            "Crop prediction input must "
            "be a one-dimensional feature list."
        )

    if len(features) != len(
        FEATURE_COLUMNS
    ):

        raise ValueError(

            "Crop prediction requires exactly "
            "7 features: "
            "nitrogen, phosphorus, potassium, "
            "temperature, humidity, ph, rainfall"

        )

    # =====================================================
    # NUMERIC VALIDATION
    # =====================================================

    if not np.all(
        np.isfinite(features)
    ):

        raise ValueError(
            "Crop prediction contains "
            "invalid numeric values."
        )

    # =====================================================
    # LOAD MODEL
    # =====================================================

    model_data = load_crop_model()

    model = model_data["model"]

    # =====================================================
    # DATAFRAME
    # =====================================================

    input_data = pd.DataFrame(

        [features],

        columns=FEATURE_COLUMNS

    )

    # =====================================================
    # PREDICTION
    # =====================================================

    prediction = model.predict(
        input_data
    )[0]

    # =====================================================
    # PROBABILITIES
    # =====================================================

    probabilities = model.predict_proba(
        input_data
    )[0]

    best_index = int(
        np.argmax(probabilities)
    )

    confidence = float(
        probabilities[best_index]
    )

    # =====================================================
    # RESULT
    # =====================================================

    return {

        "recommended_crop":
            str(
                prediction
            ).strip().lower(),

        "confidence":
            round(
                confidence * 100,
                2
            ),

        "model":
            "Random Forest",

        "dataset_records":
            model_data.get(
                "dataset_records",
                0
            ),

        "crop_classes":
            len(
                model.classes_
            ),

        "accuracy":
            round(
                model_data.get(
                    "accuracy",
                    0
                ) * 100,
                2
            )

    }