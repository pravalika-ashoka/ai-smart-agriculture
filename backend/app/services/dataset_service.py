from pathlib import Path
import pandas as pd


# =========================================================
# DATASET DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATASET_DIR = BASE_DIR / "dataset"


# =========================================================
# DATASET PATHS
# =========================================================

# Updated 100,000-record crop dataset
CROP_DATASET = DATASET_DIR / "crop_data_100000.csv"

# 50,000-record soil dataset
SOIL_DATASET = DATASET_DIR / "soil_data_50000.csv"

# Fertilizer dataset
FERTILIZER_DATASET = DATASET_DIR / "fertilizer_data.csv"

# Irrigation dataset
IRRIGATION_DATASET = DATASET_DIR / "irrigation_data.csv"


# =========================================================
# HELPER
# =========================================================

def _load_csv(path: Path) -> pd.DataFrame:

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    return pd.read_csv(path)


# =========================================================
# CROP DATA
# =========================================================

def load_crop_data():

    # Load the updated 100,000-record crop dataset
    data = _load_csv(CROP_DATASET)

    # -----------------------------------------------------
    # Crop dataset column conversion
    #
    # Dataset columns:
    #
    # N, P, K, temperature, humidity, ph, rainfall, label
    #
    # ML model expects:
    #
    # nitrogen, phosphorus, potassium,
    # temperature, humidity, ph, rainfall, crop
    # -----------------------------------------------------

    rename_map = {
        "N": "nitrogen",
        "P": "phosphorus",
        "K": "potassium",
        "label": "crop"
    }

    data = data.rename(
        columns=rename_map
    )

    # -----------------------------------------------------
    # Required columns
    # -----------------------------------------------------

    required_columns = [
        "nitrogen",
        "phosphorus",
        "potassium",
        "temperature",
        "humidity",
        "rainfall",
        "crop"
    ]

    missing = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            "Crop dataset is missing columns: "
            + ", ".join(missing)
        )

    # -----------------------------------------------------
    # Convert numerical columns safely
    # -----------------------------------------------------

    numeric_columns = [
        "nitrogen",
        "phosphorus",
        "potassium",
        "temperature",
        "humidity",
        "rainfall"
    ]

    for column in numeric_columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Clean crop labels
    # -----------------------------------------------------

    data["crop"] = (
        data["crop"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # -----------------------------------------------------
    # Remove invalid rows
    # -----------------------------------------------------

    data = data.dropna(
        subset=required_columns
    )

    # Remove empty crop labels
    data = data[
        data["crop"].str.len() > 0
    ]

    # -----------------------------------------------------
    # Reset index
    # -----------------------------------------------------

    data = data.reset_index(
        drop=True
    )

    return data


# =========================================================
# SOIL DATA
# =========================================================

def load_soil_data():

    data = _load_csv(
        SOIL_DATASET
    )

    # -----------------------------------------------------
    # Required columns
    # -----------------------------------------------------

    required_columns = [
        "nitrogen",
        "phosphorus",
        "potassium",
        "moisture",
        "temperature",
        "soil_health"
    ]

    missing = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            "Soil dataset is missing columns: "
            + ", ".join(missing)
        )

    # -----------------------------------------------------
    # Convert numerical columns safely
    # -----------------------------------------------------

    numeric_columns = [
        "nitrogen",
        "phosphorus",
        "potassium",
        "moisture",
        "temperature"
    ]

    for column in numeric_columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Clean soil health labels
    # -----------------------------------------------------

    data["soil_health"] = (
        data["soil_health"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    # -----------------------------------------------------
    # Remove invalid rows
    # -----------------------------------------------------

    data = data.dropna(
        subset=required_columns
    )

    # -----------------------------------------------------
    # Reset index
    # -----------------------------------------------------

    data = data.reset_index(
        drop=True
    )

    return data


# =========================================================
# FERTILIZER DATA
# =========================================================

def load_fertilizer_data():

    data = _load_csv(
        FERTILIZER_DATASET
    )

    return data


# =========================================================
# IRRIGATION DATA
# =========================================================

def load_irrigation_data():

    data = _load_csv(
        IRRIGATION_DATASET
    )

    return data