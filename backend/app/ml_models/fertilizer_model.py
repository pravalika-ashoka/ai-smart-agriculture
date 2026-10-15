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

MODEL_DIR = (
    BASE_DIR /
    "saved_models"
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
# FEATURE NAMES
# =========================================================

FEATURE_NAMES = [

    "nitrogen",

    "phosphorus",

    "potassium",

    "moisture",

    "temperature"

]


# =========================================================
# CACHED MODEL
# =========================================================

_FERTILIZER_MODEL = None


# =========================================================
# PREPARE FERTILIZER DATA
# =========================================================

def prepare_fertilizer_data():

    dataset = load_fertilizer_data()


    # -----------------------------------------------------
    # CHECK DATASET
    # -----------------------------------------------------

    if dataset is None or dataset.empty:

        raise ValueError(
            "Fertilizer dataset is empty."
        )


    # -----------------------------------------------------
    # REQUIRED COLUMNS
    # -----------------------------------------------------

    required_columns = [

        "nitrogen",

        "phosphorus",

        "potassium",

        "moisture",

        "temperature",

        "recommended_fertilizer"

    ]


    # -----------------------------------------------------
    # CHECK MISSING COLUMNS
    # -----------------------------------------------------

    missing_columns = [

        column

        for column in required_columns

        if column not in dataset.columns

    ]


    if missing_columns:

        raise ValueError(

            "Fertilizer dataset is missing columns: "
            + ", ".join(missing_columns)

        )


    # -----------------------------------------------------
    # COPY DATASET
    # -----------------------------------------------------

    dataset = dataset.copy()


    # -----------------------------------------------------
    # CONVERT NUMERIC FEATURES
    # -----------------------------------------------------

    for column in FEATURE_NAMES:

        dataset[column] = pd.to_numeric(

            dataset[column],

            errors="coerce"

        )


    # -----------------------------------------------------
    # CLEAN FERTILIZER LABELS
    # -----------------------------------------------------

    dataset[
        "recommended_fertilizer"
    ] = (

        dataset[
            "recommended_fertilizer"
        ]

        .astype(str)

        .str.strip()

    )


    # -----------------------------------------------------
    # REMOVE INVALID NUMERIC ROWS
    # -----------------------------------------------------

    dataset = dataset.dropna(

        subset=FEATURE_NAMES

    )


    # -----------------------------------------------------
    # REMOVE EMPTY LABELS
    # -----------------------------------------------------

    dataset = dataset[

        dataset[
            "recommended_fertilizer"
        ].str.len() > 0

    ]


    # -----------------------------------------------------
    # REMOVE INVALID NUMERIC VALUES
    # -----------------------------------------------------

    dataset = dataset[

        np.isfinite(

            dataset[
                FEATURE_NAMES
            ].to_numpy()

        ).all(axis=1)

    ]


    # -----------------------------------------------------
    # VALIDATE RECORD COUNT
    # -----------------------------------------------------

    if len(dataset) < 2:

        raise ValueError(

            "Not enough valid fertilizer "
            "dataset records."

        )


    # -----------------------------------------------------
    # INPUT FEATURES
    # -----------------------------------------------------

    X = (

        dataset[
            FEATURE_NAMES
        ]

        .astype(float)

    )


    # -----------------------------------------------------
    # TARGET
    # -----------------------------------------------------

    y = dataset[
        "recommended_fertilizer"
    ]


    # -----------------------------------------------------
    # VALIDATE CLASSES
    # -----------------------------------------------------

    if y.nunique() < 2:

        raise ValueError(

            "Fertilizer dataset must contain "
            "at least two different fertilizer classes."

        )


    return X, y


# =========================================================
# TRAIN FERTILIZER MODEL
# =========================================================

def train_fertilizer_model():

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    X, y = prepare_fertilizer_data()


    # -----------------------------------------------------
    # CHECK CLASS DISTRIBUTION
    # -----------------------------------------------------

    class_counts = y.value_counts()

    use_stratify = (
        class_counts.min() >= 2
    )


    # -----------------------------------------------------
    # TRAIN / TEST SPLIT
    # -----------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.25,

        random_state=42,

        stratify=y if use_stratify else None

    )


    # -----------------------------------------------------
    # RANDOM FOREST
    # -----------------------------------------------------

    model = RandomForestClassifier(

        n_estimators=100,

        random_state=42,

        class_weight="balanced",

        min_samples_leaf=1,

        n_jobs=-1

    )


    # -----------------------------------------------------
    # TRAINING INFORMATION
    # -----------------------------------------------------

    print()

    print("=" * 60)

    print(
        "TRAINING FERTILIZER RANDOM FOREST MODEL"
    )

    print("=" * 60)

    print(
        f"Training records : {len(X_train)}"
    )

    print(
        f"Testing records  : {len(X_test)}"
    )

    print(
        f"Features         : {len(FEATURE_NAMES)}"
    )

    print(
        f"Classes          : {y.nunique()}"
    )

    print()


    # -----------------------------------------------------
    # TRAIN
    # -----------------------------------------------------

    model.fit(

        X_train,

        y_train

    )


    # -----------------------------------------------------
    # PREDICTION
    # -----------------------------------------------------

    predictions = model.predict(

        X_test

    )


    # -----------------------------------------------------
    # ACCURACY
    # -----------------------------------------------------

    accuracy = accuracy_score(

        y_test,

        predictions

    )


    # -----------------------------------------------------
    # CREATE MODEL DIRECTORY
    # -----------------------------------------------------

    MODEL_DIR.mkdir(

        parents=True,

        exist_ok=True

    )


    # -----------------------------------------------------
    # SAVE MODEL
    # -----------------------------------------------------

    joblib.dump(

        model,

        MODEL_PATH,

        compress=3

    )


    # -----------------------------------------------------
    # SAVE METADATA
    # -----------------------------------------------------

    metadata = {

        "model":
            "Random Forest Classifier",

        "accuracy":
            float(accuracy),

        "accuracy_percent":
            round(
                accuracy * 100,
                2
            ),

        "dataset_records":
            int(len(X)),

        "training_records":
            int(len(X_train)),

        "testing_records":
            int(len(X_test)),

        "features":
            FEATURE_NAMES,

        "feature_count":
            len(FEATURE_NAMES),

        "classes":
            sorted(
                y.unique().tolist()
            ),

        "class_count":
            int(y.nunique()),

        "n_estimators":
            100,

        "random_state":
            42

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


    # -----------------------------------------------------
    # UPDATE CACHE
    # -----------------------------------------------------

    global _FERTILIZER_MODEL

    _FERTILIZER_MODEL = model


    # -----------------------------------------------------
    # TRAINING INFORMATION
    # -----------------------------------------------------

    print("=" * 60)

    print(
        "FERTILIZER MODEL TRAINED"
    )

    print("=" * 60)

    print(
        f"Dataset records : {len(X)}"
    )

    print(
        f"Training records: {len(X_train)}"
    )

    print(
        f"Testing records : {len(X_test)}"
    )

    print(
        f"Features        : {len(FEATURE_NAMES)}"
    )

    print(
        f"Classes         : {len(y.unique())}"
    )

    print(
        f"Accuracy        : {accuracy * 100:.2f}%"
    )

    print(
        f"Model saved     : {MODEL_PATH}"
    )

    print(
        f"Metadata saved  : {METADATA_PATH}"
    )

    print("=" * 60)

    print()


    return model, accuracy


# =========================================================
# LOAD SAVED MODEL
# =========================================================

def load_fertilizer_model():

    global _FERTILIZER_MODEL


    # -----------------------------------------------------
    # RETURN CACHED MODEL
    # -----------------------------------------------------

    if _FERTILIZER_MODEL is not None:

        return _FERTILIZER_MODEL


    # -----------------------------------------------------
    # CHECK MODEL FILE
    # -----------------------------------------------------

    if not MODEL_PATH.exists():

        raise FileNotFoundError(

            "Saved fertilizer model not found: "
            f"{MODEL_PATH}. "
            "Train the fertilizer model locally "
            "before starting the application."

        )


    # -----------------------------------------------------
    # LOAD MODEL
    # -----------------------------------------------------

    try:

        print(
            "Loading fertilizer model..."
        )


        _FERTILIZER_MODEL = joblib.load(

            MODEL_PATH

        )


        # -------------------------------------------------
        # BASIC MODEL VALIDATION
        # -------------------------------------------------

        if not hasattr(

            _FERTILIZER_MODEL,

            "predict"

        ):

            raise ValueError(

                "Saved fertilizer file is not "
                "a valid prediction model."

            )


        print(
            "Fertilizer model loaded successfully."
        )


        return _FERTILIZER_MODEL


    except Exception as error:

        print(
            "Unable to load fertilizer model."
        )

        print(
            f"Reason: {error}"
        )


        raise RuntimeError(

            "Fertilizer model could not be loaded."

        ) from error


# =========================================================
# LOAD MODEL ACCURACY
# =========================================================

def load_fertilizer_accuracy():

    # -----------------------------------------------------
    # CHECK METADATA
    # -----------------------------------------------------

    if not METADATA_PATH.exists():

        return 0.0


    try:

        with open(

            METADATA_PATH,

            "r",

            encoding="utf-8"

        ) as file:

            metadata = json.load(file)


        return float(

            metadata.get(

                "accuracy",

                0.0

            )

        )


    except Exception as error:

        print(

            "Unable to load fertilizer metadata:",

            error

        )

        return 0.0


# =========================================================
# PREDICT FERTILIZER
# =========================================================

def predict_fertilizer(features):

    # -----------------------------------------------------
    # CONVERT INPUT TO NUMPY ARRAY
    # -----------------------------------------------------

    try:

        features = np.asarray(

            features,

            dtype=np.float32

        )

    except Exception as error:

        raise ValueError(

            "Fertilizer input must contain "
            "numeric values."

        ) from error


    # -----------------------------------------------------
    # MAKE 2D
    # -----------------------------------------------------

    if features.ndim == 1:

        features = features.reshape(

            1,

            -1

        )


    # -----------------------------------------------------
    # VALIDATE DIMENSIONS
    # -----------------------------------------------------

    if features.ndim != 2:

        raise ValueError(

            "Fertilizer input must contain "
            "one or more rows of features."

        )


    # -----------------------------------------------------
    # VALIDATE FEATURE COUNT
    # -----------------------------------------------------

    expected_features = len(

        FEATURE_NAMES

    )

    received_features = features.shape[1]


    if received_features != expected_features:

        raise ValueError(

            f"Expected "
            f"{expected_features} "
            f"fertilizer features "
            f"({', '.join(FEATURE_NAMES)}), "
            f"but received "
            f"{received_features}."

        )


    # -----------------------------------------------------
    # VALIDATE NUMERIC VALUES
    # -----------------------------------------------------

    if not np.all(

        np.isfinite(features)

    ):

        raise ValueError(

            "Fertilizer input contains "
            "invalid numeric values."

        )


    # -----------------------------------------------------
    # CREATE DATAFRAME
    # -----------------------------------------------------

    features_df = pd.DataFrame(

        features,

        columns=FEATURE_NAMES

    )


    # -----------------------------------------------------
    # LOAD MODEL
    # -----------------------------------------------------

    model = load_fertilizer_model()


    # -----------------------------------------------------
    # PREDICTION
    # -----------------------------------------------------

    try:

        prediction = model.predict(

            features_df

        )[0]


    except Exception as error:

        print(

            "Fertilizer model prediction error:",
            error

        )


        raise RuntimeError(

            "Unable to make fertilizer prediction."

        ) from error


    # -----------------------------------------------------
    # MODEL ACCURACY
    # -----------------------------------------------------

    accuracy = load_fertilizer_accuracy()


    # -----------------------------------------------------
    # CONFIDENCE
    # -----------------------------------------------------

    confidence = 0.0


    if hasattr(

        model,

        "predict_proba"

    ):

        try:

            probabilities = model.predict_proba(

                features_df

            )[0]


            if len(probabilities) > 0:

                confidence = (

                    float(

                        np.max(probabilities)

                    ) * 100

                )


        except Exception as error:

            print(

                "Unable to calculate fertilizer "
                "prediction confidence:",

                error

            )


    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {

        "fertilizer":

            str(prediction),

        "accuracy":

            round(

                accuracy * 100,

                2

            ),

        "confidence":

            round(

                confidence,

                2

            )

    }