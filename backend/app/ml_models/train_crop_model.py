from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import train_test_split

from app.services.dataset_service import load_crop_data


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = (
    BASE_DIR
    / "app"
    / "ml_models"
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
# FEATURES
# =========================================================

FEATURE_COLUMNS = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "temperature",
    "humidity",
    "rainfall"
]

TARGET_COLUMN = "crop"


# =========================================================
# TRAIN MODEL
# =========================================================

def train_model():

    print("\n========================================")
    print("AI SMART AGRICULTURE")
    print("CROP MODEL TRAINING")
    print("========================================\n")

    # -----------------------------------------------------
    # LOAD DATASET
    # -----------------------------------------------------

    print("Loading crop dataset...")

    dataset = load_crop_data()

    print(f"Original dataset rows: {len(dataset)}")

    print("\nOriginal dataset columns:")
    print(dataset.columns.tolist())

    # -----------------------------------------------------
    # RENAME NEW DATASET COLUMNS
    # -----------------------------------------------------

    column_mapping = {
        "N": "nitrogen",
        "P": "phosphorus",
        "K": "potassium",
        "label": "crop"
    }

    dataset = dataset.rename(
        columns=column_mapping
    )

    print("\nDataset columns after mapping:")
    print(dataset.columns.tolist())

    # -----------------------------------------------------
    # VALIDATE REQUIRED COLUMNS
    # -----------------------------------------------------

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
            "Crop dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    # -----------------------------------------------------
    # CROP DISTRIBUTION
    # -----------------------------------------------------

    print("\n========================================")
    print("CROP DISTRIBUTION")
    print("========================================\n")

    print(
        dataset[TARGET_COLUMN].value_counts()
    )

    print(
        f"\nNumber of crop classes: "
        f"{dataset[TARGET_COLUMN].nunique()}"
    )

    # -----------------------------------------------------
    # CONVERT NUMERICAL FEATURES
    # -----------------------------------------------------

    print("\nPreparing numerical features...")

    for column in FEATURE_COLUMNS:

        dataset[column] = pd.to_numeric(
            dataset[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # CLEAN TARGET
    # -----------------------------------------------------

    dataset[TARGET_COLUMN] = (
        dataset[TARGET_COLUMN]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # -----------------------------------------------------
    # REMOVE INVALID ROWS
    # -----------------------------------------------------

    before_cleaning = len(dataset)

    dataset = dataset.dropna(
        subset=required_columns
    )

    dataset = dataset[
        dataset[TARGET_COLUMN].str.len() > 0
    ]

    dataset = dataset.reset_index(
        drop=True
    )

    removed_rows = (
        before_cleaning
        - len(dataset)
    )

    print(
        f"\nValid dataset rows: {len(dataset)}"
    )

    print(
        f"Invalid rows removed: {removed_rows}"
    )

    # -----------------------------------------------------
    # FEATURES / TARGET
    # -----------------------------------------------------

    X = dataset[
        FEATURE_COLUMNS
    ]

    y = dataset[
        TARGET_COLUMN
    ]

    print("\n========================================")
    print("FEATURES USED BY MODEL")
    print("========================================")

    for index, feature in enumerate(
        FEATURE_COLUMNS
    ):
        print(
            f"{index}: {feature}"
        )

    # -----------------------------------------------------
    # TRAIN / TEST SPLIT
    # -----------------------------------------------------

    print("\nSplitting dataset...")

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    print(
        f"\nTraining samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    # -----------------------------------------------------
    # RANDOM FOREST
    # -----------------------------------------------------

    print("\n========================================")
    print("TRAINING RANDOM FOREST")
    print("========================================\n")

    model = RandomForestClassifier(
        n_estimators=40,
        max_depth=18,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        class_weight="balanced",
        n_jobs=1
    )

    model.fit(
        X_train,
        y_train
    )

    print(
        "\nRandom Forest training completed."
    )

    # -----------------------------------------------------
    # PREDICTION
    # -----------------------------------------------------

    print(
        "\nGenerating predictions..."
    )

    predictions = model.predict(
        X_test
    )

    # -----------------------------------------------------
    # EVALUATION
    # -----------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print("\n========================================")
    print("MODEL EVALUATION")
    print("========================================")

    print(
        f"\nAccuracy: {accuracy:.4f}"
    )

    print(
        f"Accuracy percentage: "
        f"{accuracy * 100:.2f}%"
    )

    # -----------------------------------------------------
    # CLASSIFICATION REPORT
    # -----------------------------------------------------

    print(
        "\nClassification Report:\n"
    )

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    # -----------------------------------------------------
    # CONFUSION MATRIX
    # -----------------------------------------------------

    print(
        "\nConfusion Matrix:\n"
    )

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    # -----------------------------------------------------
    # FEATURE IMPORTANCE
    # -----------------------------------------------------

    print("\n========================================")
    print("FEATURE IMPORTANCE")
    print("========================================\n")

    importance = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "importance": model.feature_importances_
        }
    ).sort_values(
        "importance",
        ascending=False
    )

    print(
        importance.to_string(
            index=False
        )
    )

    # -----------------------------------------------------
    # MODEL INFORMATION
    # -----------------------------------------------------

    crop_classes = sorted(
        y.unique().tolist()
    )

    print("\n========================================")
    print("MODEL INFORMATION")
    print("========================================")

    print(
        f"Dataset records: {len(dataset)}"
    )

    print(
        f"Features: {len(FEATURE_COLUMNS)}"
    )

    print(
        f"Crop classes: {len(crop_classes)}"
    )

    print(
        f"Random Forest trees: "
        f"{model.n_estimators}"
    )

    print(
        f"Maximum tree depth: "
        f"{model.max_depth}"
    )

    print(
        f"Accuracy: "
        f"{accuracy * 100:.2f}%"
    )

    print("\nCrop classes:")

    for crop in crop_classes:
        print(
            f" - {crop}"
        )

    # -----------------------------------------------------
    # MODEL PACKAGE
    # -----------------------------------------------------

    model_package = {
        "model": model,
        "features": FEATURE_COLUMNS,
        "accuracy": float(accuracy),
        "dataset_records": int(len(dataset)),
        "crop_classes": crop_classes
    }

    # -----------------------------------------------------
    # SAVE MODEL
    # -----------------------------------------------------

    print("\n========================================")
    print("SAVING MODEL")
    print("========================================\n")

    joblib.dump(
        model_package,
        MODEL_PATH,
        compress=3
    )

    print(
        f"Model saved to:\n{MODEL_PATH}"
    )

    # -----------------------------------------------------
    # MODEL SIZE
    # -----------------------------------------------------

    if MODEL_PATH.exists():

        model_size_mb = (
            MODEL_PATH.stat().st_size
            / (1024 * 1024)
        )

        print(
            f"\nSaved model size: "
            f"{model_size_mb:.2f} MB"
        )

    # -----------------------------------------------------
    # COMPLETED
    # -----------------------------------------------------

    print("\n========================================")
    print("CROP MODEL TRAINING COMPLETED")
    print("========================================\n")

    return model_package


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    train_model()