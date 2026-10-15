import os

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from app.services.dataset_service import load_soil_data


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "saved_models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "soil_random_forest.pkl"
)

ACCURACY_PATH = os.path.join(
    MODEL_DIR,
    "soil_model_accuracy.txt"
)


# =========================================================
# FEATURES
# =========================================================

FEATURES = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "moisture",
    "temperature"
]

TARGET = "soil_health"


# =========================================================
# CACHED MODEL
# =========================================================

_SOIL_MODEL = None


# =========================================================
# TRAIN SOIL MODEL
# =========================================================

def train_soil_model():

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Load dataset
    # -----------------------------------------------------

    df = load_soil_data()

    if df is None or df.empty:

        raise ValueError(
            "Soil dataset is empty."
        )

    # -----------------------------------------------------
    # Validate columns
    # -----------------------------------------------------

    required_columns = (
        FEATURES + [TARGET]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Soil dataset is missing columns: "
            + ", ".join(missing_columns)
        )

    # -----------------------------------------------------
    # Keep only required columns
    # -----------------------------------------------------

    df = df[
        required_columns
    ].copy()

    # -----------------------------------------------------
    # Convert numerical columns
    # -----------------------------------------------------

    for column in FEATURES:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Clean target
    # -----------------------------------------------------

    df[TARGET] = (
        df[TARGET]
        .astype(str)
        .str.strip()
    )

    # -----------------------------------------------------
    # Remove invalid records
    # -----------------------------------------------------

    df = df.dropna(
        subset=FEATURES + [TARGET]
    )

    df = df[
        df[TARGET] != ""
    ]

    if df.empty:

        raise ValueError(
            "No valid soil records available."
        )

    # -----------------------------------------------------
    # Features and target
    # -----------------------------------------------------

    X = df[
        FEATURES
    ].astype(float)

    y = df[
        TARGET
    ]

    # -----------------------------------------------------
    # Validate classes
    # -----------------------------------------------------

    if y.nunique() < 2:

        raise ValueError(
            "Soil dataset must contain "
            "at least two soil health classes."
        )

    # -----------------------------------------------------
    # Train/test split
    # -----------------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    # -----------------------------------------------------
    # MEMORY-OPTIMIZED RANDOM FOREST
    # -----------------------------------------------------
    #
    # Compared with the previous 300-tree model,
    # this uses fewer trees and limits tree depth.
    #
    # This significantly reduces RAM usage on Render.
    #
    # -----------------------------------------------------

    model = RandomForestClassifier(

        n_estimators=40,

        max_depth=12,

        min_samples_split=2,

        min_samples_leaf=2,

        random_state=42,

        class_weight="balanced",

        n_jobs=1
    )

    # -----------------------------------------------------
    # Train
    # -----------------------------------------------------

    model.fit(
        X_train,
        y_train
    )

    # -----------------------------------------------------
    # Test
    # -----------------------------------------------------

    y_pred = model.predict(
        X_test
    )

    # -----------------------------------------------------
    # Accuracy
    # -----------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    # -----------------------------------------------------
    # Save model
    # -----------------------------------------------------

    joblib.dump(
        model,
        MODEL_PATH,
        compress=3
    )

    # -----------------------------------------------------
    # Save accuracy
    # -----------------------------------------------------

    with open(
        ACCURACY_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            str(float(accuracy))
        )

    # -----------------------------------------------------
    # Console output
    # -----------------------------------------------------

    print()
    print("=" * 55)
    print("SOIL MODEL TRAINED")
    print("=" * 55)

    print(
        f"Dataset records : {len(df)}"
    )

    print(
        f"Features        : {len(FEATURES)}"
    )

    print(
        f"Classes         : {sorted(y.unique().tolist())}"
    )

    print(
        f"Accuracy        : {accuracy * 100:.2f}%"
    )

    print(
        f"Model saved     : {MODEL_PATH}"
    )

    print(
        f"Accuracy saved  : {ACCURACY_PATH}"
    )

    print("=" * 55)

    return model, accuracy


# =========================================================
# LOAD SAVED MODEL
# =========================================================

def load_soil_model():

    global _SOIL_MODEL

    # -----------------------------------------------------
    # Return cached model
    # -----------------------------------------------------

    if _SOIL_MODEL is not None:

        return _SOIL_MODEL

    # -----------------------------------------------------
    # Model must already exist
    # -----------------------------------------------------

    if not os.path.exists(
        MODEL_PATH
    ):

        raise FileNotFoundError(

            "Saved soil model not found: "
            + MODEL_PATH

        )

    # -----------------------------------------------------
    # Load model once
    # -----------------------------------------------------

    try:

        print(
            "Loading soil model..."
        )

        _SOIL_MODEL = joblib.load(
            MODEL_PATH
        )

        print(
            "Soil model loaded successfully."
        )

        return _SOIL_MODEL

    except Exception as error:

        print(
            "Unable to load soil model."
        )

        print(
            f"Reason: {error}"
        )

        raise RuntimeError(
            "Soil model could not be loaded."
        ) from error


# =========================================================
# LOAD SAVED ACCURACY
# =========================================================

def load_soil_accuracy():

    # -----------------------------------------------------
    # Accuracy file does not exist
    # -----------------------------------------------------

    if not os.path.exists(
        ACCURACY_PATH
    ):

        return 0.0

    # -----------------------------------------------------
    # Read accuracy
    # -----------------------------------------------------

    try:

        with open(
            ACCURACY_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            accuracy = float(
                file.read().strip()
            )

        return accuracy

    except Exception as error:

        print(
            "Unable to read soil model accuracy."
        )

        print(
            f"Reason: {error}"
        )

        return 0.0


# =========================================================
# PREDICT SOIL HEALTH
# =========================================================

def predict_soil(features):

    # -----------------------------------------------------
    # Load cached model
    # -----------------------------------------------------

    model = load_soil_model()

    # -----------------------------------------------------
    # Validate input
    # -----------------------------------------------------

    if features is None:

        raise ValueError(
            "Soil feature data cannot be empty."
        )

    if len(features) == 0:

        raise ValueError(
            "Soil feature data cannot be empty."
        )

    # -----------------------------------------------------
    # Convert input to NumPy array
    # -----------------------------------------------------

    try:

        features_array = np.asarray(
            features,
            dtype=float
        )

    except Exception as error:

        raise ValueError(
            "Soil feature data must contain "
            "valid numeric values."
        ) from error

    # -----------------------------------------------------
    # Make sure input is 2D
    # -----------------------------------------------------

    if features_array.ndim == 1:

        features_array = (
            features_array.reshape(
                1,
                -1
            )
        )

    # -----------------------------------------------------
    # Validate dimensions
    # -----------------------------------------------------

    if features_array.ndim != 2:

        raise ValueError(
            "Soil feature data must be a "
            "2-dimensional array."
        )

    # -----------------------------------------------------
    # Only one prediction is expected
    # -----------------------------------------------------

    if features_array.shape[0] != 1:

        raise ValueError(
            "Soil prediction expects exactly "
            "one input record."
        )

    # -----------------------------------------------------
    # Validate feature count
    # -----------------------------------------------------

    if features_array.shape[1] != len(FEATURES):

        raise ValueError(

            f"Expected {len(FEATURES)} features, "

            f"received {features_array.shape[1]}."

        )

    # -----------------------------------------------------
    # Validate numeric values
    # -----------------------------------------------------

    if not np.all(
        np.isfinite(features_array)
    ):

        raise ValueError(
            "Soil prediction contains "
            "invalid numeric values."
        )

    # -----------------------------------------------------
    # Create DataFrame
    #
    # Using the original feature names prevents
    # sklearn feature-name warnings.
    # -----------------------------------------------------

    input_data = pd.DataFrame(
        features_array,
        columns=FEATURES
    )

    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    prediction = model.predict(
        input_data
    )

    soil_health = str(
        prediction[0]
    ).strip()

    # -----------------------------------------------------
    # Prediction probabilities
    # -----------------------------------------------------

    probabilities_array = (
        model.predict_proba(
            input_data
        )[0]
    )

    probabilities = {}

    for class_name, probability in zip(

        model.classes_,

        probabilities_array

    ):

        probabilities[
            str(class_name)
        ] = round(

            float(probability) * 100,

            2

        )

    # -----------------------------------------------------
    # Confidence
    # -----------------------------------------------------

    confidence = (
        float(
            np.max(
                probabilities_array
            )
        ) * 100
    )

    # -----------------------------------------------------
    # Load saved accuracy
    #
    # IMPORTANT:
    #
    # We DO NOT load the 50,000-row dataset here.
    # We DO NOT run train_test_split here.
    # We DO NOT predict the complete test dataset here.
    #
    # This saves RAM and CPU on Render.
    # -----------------------------------------------------

    accuracy = load_soil_accuracy()

    # -----------------------------------------------------
    # Return result
    #
    # "model" is intentionally returned because your
    # soil API sends it to generate_explanation().
    #
    # The API removes it before returning JSON.
    # -----------------------------------------------------

    return {

        "soil_health":
            soil_health,

        "accuracy":
            round(
                float(accuracy),
                4
            ),

        "confidence":
            round(
                confidence,
                2
            ),

        "probabilities":
            probabilities,

        "model":
            model
    }