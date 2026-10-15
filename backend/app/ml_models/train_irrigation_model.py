import joblib
import pandas as pd

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_FILE = (
    BASE_DIR
    / "dataset"
    / "irrigation_training_data.csv"
)

MODEL_DIR = (
    BASE_DIR
    / "app"
    / "ml_models"
)

MODEL_FILE = (
    MODEL_DIR
    / "irrigation_model.pkl"
)

SCALER_FILE = (
    MODEL_DIR
    / "irrigation_scaler.pkl"
)


# =========================================================
# FEATURES
# =========================================================
# The trained Random Forest uses 12 numerical features.
#
# crop_type itself is represented through crop_water_factor.
# =========================================================

FEATURE_COLUMNS = [

    "soil_moisture",

    "humidity",

    "temperature",

    "rainfall",

    "soil_temperature",

    "wind_speed",

    "rain_forecast",

    "nitrogen",

    "phosphorus",

    "potassium",

    "crop_water_factor",

]


TARGET_COLUMN = (
    "irrigation_recommendation"
)


# =========================================================
# TRAIN MODEL
# =========================================================

def train_irrigation_model():

    print()
    print(
        "============================================================"
    )
    print(
        "IRRIGATION MODEL TRAINING"
    )
    print(
        "============================================================"
    )

    # -----------------------------------------------------
    # Check dataset
    # -----------------------------------------------------

    if not DATASET_FILE.exists():

        raise FileNotFoundError(
            f"Irrigation dataset not found: {DATASET_FILE}"
        )

    print()
    print(
        f"Loading dataset: {DATASET_FILE}"
    )

    df = pd.read_csv(
        DATASET_FILE
    )

    print(
        f"Dataset rows: {len(df)}"
    )

    print(
        f"Dataset columns: {len(df.columns)}"
    )

    # -----------------------------------------------------
    # Verify required columns
    # -----------------------------------------------------

    required_columns = (
        FEATURE_COLUMNS
        + [TARGET_COLUMN]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    # -----------------------------------------------------
    # Remove invalid rows
    # -----------------------------------------------------

    df = df.dropna(
        subset=required_columns
    ).copy()

    print(
        f"Valid rows: {len(df)}"
    )

    # -----------------------------------------------------
    # Features and target
    # -----------------------------------------------------

    X = df[
        FEATURE_COLUMNS
    ].copy()

    y = df[
        TARGET_COLUMN
    ].astype(str)

    # Make sure all model inputs are numeric

    X = X.astype(float)

    # -----------------------------------------------------
    # Display target distribution
    # -----------------------------------------------------

    print()
    print(
        "Recommendation distribution:"
    )

    print(
        y.value_counts()
    )

    # -----------------------------------------------------
    # Train / test split
    # -----------------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y,
        )
    )

    print()
    print(
        f"Training samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    # -----------------------------------------------------
    # Scaling
    # -----------------------------------------------------

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(
        X_train
    )

    X_test_scaled = scaler.transform(
        X_test
    )

    # -----------------------------------------------------
    # Random Forest
    # -----------------------------------------------------

    print()
    print(
        "Training Random Forest..."
    )

    model = RandomForestClassifier(

        n_estimators=300,

        random_state=42,

        n_jobs=-1,

        class_weight="balanced",

    )

    model.fit(
        X_train_scaled,
        y_train
    )

    # -----------------------------------------------------
    # Evaluation
    # -----------------------------------------------------

    predictions = model.predict(
        X_test_scaled
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print()
    print(
        "============================================================"
    )

    print(
        "MODEL EVALUATION"
    )

    print(
        "============================================================"
    )

    print(
        f"Accuracy: {accuracy:.4f}"
    )

    print(
        f"Accuracy: {accuracy * 100:.2f}%"
    )

    print()
    print(
        "Classification Report:"
    )

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    # -----------------------------------------------------
    # Model classes
    # -----------------------------------------------------

    print(
        "Model classes:"
    )

    print(
        list(model.classes_)
    )

    # -----------------------------------------------------
    # Create model directory
    # -----------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Save model
    # -----------------------------------------------------

    joblib.dump(
        model,
        MODEL_FILE
    )

    # -----------------------------------------------------
    # Save scaler
    # -----------------------------------------------------

    joblib.dump(
        scaler,
        SCALER_FILE
    )

    print()
    print(
        "============================================================"
    )

    print(
        "MODEL SAVED"
    )

    print(
        "============================================================"
    )

    print(
        f"Model : {MODEL_FILE}"
    )

    print(
        f"Scaler: {SCALER_FILE}"
    )

    print()

    return (
        model,
        scaler,
        accuracy
    )


# =========================================================
# MAIN
# =========================================================

def main():

    model, scaler, accuracy = (
        train_irrigation_model()
    )

    print()
    print(
        "============================================================"
    )

    print(
        "IRRIGATION MODEL TRAINING COMPLETE"
    )

    print(
        "============================================================"
    )

    print(
        f"Final accuracy: {accuracy * 100:.2f}%"
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()