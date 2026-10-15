import pandas as pd
from pathlib import Path


# =========================================================
# DATASET PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "dataset"
    / "irrigation_data.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "dataset"
    / "integrated_irrigation_data.csv"
)


# =========================================================
# CROP WATER FACTORS
# =========================================================
# These values must match:
# irrigation_preprocessing.py
# irrigation_model.py
# =========================================================

CROP_WATER_FACTOR = {

    "rice": 1.30,
    "maize": 1.00,
    "chickpea": 0.75,
    "cotton": 1.10,
    "wheat": 0.90,
    "groundnut": 0.85,
    "banana": 1.25,

    "sugarcane": 1.25,
    "tomato": 1.15,
    "potato": 1.05,
    "onion": 0.95,
    "turmeric": 1.00,
    "chilli": 0.95,
    "sorghum": 0.75,
    "millet": 0.65,
    "ragi": 0.70,
    "soybean": 0.90,
    "pigeon_pea": 0.75,
    "okra": 1.00,
    "cabbage": 1.00,
    "carrot": 0.90,
}


# =========================================================
# SUPPORTED CROPS
# =========================================================

CROPS = list(CROP_WATER_FACTOR.keys())


# =========================================================
# CREATE INTEGRATED DATASET
# =========================================================

def create_dataset():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    if df.empty:

        raise ValueError(
            "Input irrigation dataset is empty."
        )


    # =====================================================
    # CROP INFORMATION
    # =====================================================
    # Distribute all 20 crops across the available rows.
    # This keeps the original environmental data while
    # expanding crop coverage.
    # =====================================================

    df["crop_type"] = [
        CROPS[i % len(CROPS)]
        for i in range(len(df))
    ]


    # =====================================================
    # SOIL NUTRIENTS
    # =====================================================

    nitrogen_values = [
        40, 45, 50, 55, 60,
        65, 70, 75, 80, 85,
        90, 95, 100, 105
    ]

    phosphorus_values = [
        20, 22, 25, 28, 30,
        32, 35, 38, 40, 42,
        45, 48, 50, 52
    ]

    potassium_values = [
        30, 32, 35, 38, 40,
        42, 45, 48, 50, 52,
        55, 58, 60, 62
    ]


    df["nitrogen"] = [
        nitrogen_values[i % len(nitrogen_values)]
        for i in range(len(df))
    ]

    df["phosphorus"] = [
        phosphorus_values[i % len(phosphorus_values)]
        for i in range(len(df))
    ]

    df["potassium"] = [
        potassium_values[i % len(potassium_values)]
        for i in range(len(df))
    ]


    # =====================================================
    # CROP WATER FACTOR
    # =====================================================

    df["crop_water_factor"] = (
        df["crop_type"]
        .map(CROP_WATER_FACTOR)
    )


    # =====================================================
    # VALIDATION
    # =====================================================

    if df["crop_water_factor"].isna().any():

        missing = (
            df.loc[
                df["crop_water_factor"].isna(),
                "crop_type"
            ]
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Missing crop water factors for: {missing}"
        )


    # =====================================================
    # FINAL COLUMNS
    # =====================================================

    final_columns = [

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

        "crop_type",
        "crop_water_factor",

        "irrigation_recommendation",
        "advice",
    ]


    missing_columns = [
        column
        for column in final_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )


    df = df[final_columns]


    # =====================================================
    # SAVE
    # =====================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    print()
    print("=" * 60)
    print("INTEGRATED IRRIGATION DATASET CREATED")
    print("=" * 60)

    print()
    print(f"Output: {OUTPUT_FILE}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print()
    print("Crops:")
    print(
        df["crop_type"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print()
    print("Crop water factors:")
    print(
        df[
            ["crop_type", "crop_water_factor"]
        ]
        .drop_duplicates()
        .sort_values("crop_type")
        .to_string(index=False)
    )

    print()
    print("=" * 60)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    create_dataset()