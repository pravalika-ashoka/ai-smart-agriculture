import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path("backend/dataset/crop_data.csv")
OUTPUT_FILE = Path("backend/dataset/crop_data_50000.csv")

TARGET_ROWS = 50000
RANDOM_SEED = 42

rng = np.random.default_rng(RANDOM_SEED)


# ============================================================
# REQUIRED SCHEMA
# ============================================================

COLUMNS = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "rainfall",
    "label",
]


# ============================================================
# CROP PROFILES
#
# min / max ranges used to create realistic variation.
# ============================================================

CROP_PROFILES = {

    "rice": {
        "N": (60, 110),
        "P": (35, 70),
        "K": (35, 50),
        "temperature": (20, 30),
        "humidity": (75, 95),
        "rainfall": (150, 300),
    },

    "maize": {
        "N": (60, 110),
        "P": (35, 70),
        "K": (15, 45),
        "temperature": (18, 30),
        "humidity": (55, 85),
        "rainfall": (50, 150),
    },

    "chickpea": {
        "N": (20, 80),
        "P": (40, 80),
        "K": (20, 45),
        "temperature": (18, 30),
        "humidity": (50, 75),
        "rainfall": (40, 100),
    },

    "kidneybeans": {
        "N": (10, 40),
        "P": (45, 80),
        "K": (15, 35),
        "temperature": (15, 30),
        "humidity": (55, 75),
        "rainfall": (50, 150),
    },

    "pigeonpeas": {
        "N": (10, 50),
        "P": (35, 70),
        "K": (15, 40),
        "temperature": (18, 35),
        "humidity": (45, 75),
        "rainfall": (50, 150),
    },

    "mothbeans": {
        "N": (10, 40),
        "P": (35, 70),
        "K": (15, 35),
        "temperature": (24, 38),
        "humidity": (40, 70),
        "rainfall": (20, 80),
    },

    "mungbean": {
        "N": (10, 40),
        "P": (35, 70),
        "K": (15, 35),
        "temperature": (22, 35),
        "humidity": (55, 85),
        "rainfall": (40, 120),
    },

    "blackgram": {
        "N": (10, 40),
        "P": (35, 70),
        "K": (15, 35),
        "temperature": (22, 35),
        "humidity": (55, 85),
        "rainfall": (50, 150),
    },

    "lentil": {
        "N": (10, 40),
        "P": (35, 70),
        "K": (15, 40),
        "temperature": (18, 30),
        "humidity": (50, 75),
        "rainfall": (30, 100),
    },

    "pomegranate": {
        "N": (10, 40),
        "P": (10, 40),
        "K": (10, 40),
        "temperature": (18, 35),
        "humidity": (40, 70),
        "rainfall": (30, 100),
    },

    "banana": {
        "N": (70, 120),
        "P": (40, 80),
        "K": (40, 60),
        "temperature": (24, 35),
        "humidity": (70, 95),
        "rainfall": (100, 300),
    },

    "mango": {
        "N": (10, 40),
        "P": (10, 40),
        "K": (10, 40),
        "temperature": (24, 35),
        "humidity": (45, 75),
        "rainfall": (40, 150),
    },

    "grapes": {
        "N": (10, 40),
        "P": (10, 40),
        "K": (10, 40),
        "temperature": (18, 35),
        "humidity": (50, 80),
        "rainfall": (40, 120),
    },

    "watermelon": {
        "N": (80, 120),
        "P": (10, 40),
        "K": (10, 40),
        "temperature": (24, 35),
        "humidity": (60, 90),
        "rainfall": (40, 100),
    },

    "muskmelon": {
        "N": (80, 120),
        "P": (10, 40),
        "K": (10, 40),
        "temperature": (24, 35),
        "humidity": (55, 85),
        "rainfall": (20, 80),
    },

    "apple": {
        "N": (10, 40),
        "P": (10, 40),
        "K": (10, 40),
        "temperature": (8, 25),
        "humidity": (50, 80),
        "rainfall": (80, 200),
    },

    "orange": {
        "N": (10, 40),
        "P": (10, 40),
        "K": (10, 40),
        "temperature": (18, 32),
        "humidity": (50, 80),
        "rainfall": (60, 180),
    },

    "papaya": {
        "N": (40, 100),
        "P": (30, 70),
        "K": (30, 60),
        "temperature": (22, 35),
        "humidity": (65, 90),
        "rainfall": (80, 200),
    },

    "coconut": {
        "N": (10, 40),
        "P": (10, 40),
        "K": (10, 40),
        "temperature": (24, 35),
        "humidity": (70, 95),
        "rainfall": (100, 300),
    },

    "cotton": {
        "N": (100, 140),
        "P": (30, 60),
        "K": (30, 60),
        "temperature": (21, 35),
        "humidity": (50, 80),
        "rainfall": (50, 150),
    },

    "jute": {
        "N": (60, 110),
        "P": (30, 70),
        "K": (30, 60),
        "temperature": (24, 35),
        "humidity": (70, 95),
        "rainfall": (150, 300),
    },

    "coffee": {
        "N": (80, 130),
        "P": (20, 60),
        "K": (20, 60),
        "temperature": (18, 30),
        "humidity": (65, 95),
        "rainfall": (100, 300),
    },
}


# ============================================================
# LOAD ORIGINAL DATA
# ============================================================

print("=" * 70)
print("AI SMART AGRICULTURE")
print("CROP DATASET EXPANSION")
print("=" * 70)

df = pd.read_csv(INPUT_FILE)

print(f"\nOriginal records: {len(df):,}")


# ============================================================
# VALIDATE SCHEMA
# ============================================================

if list(df.columns) != COLUMNS:
    raise ValueError(
        f"\nUnexpected columns.\n"
        f"Expected: {COLUMNS}\n"
        f"Found:    {list(df.columns)}"
    )


# ============================================================
# VALIDATE EXISTING CROPS
# ============================================================

existing_crops = sorted(df["label"].unique())
profile_crops = sorted(CROP_PROFILES.keys())

print(f"Existing crop classes: {len(existing_crops)}")
print(existing_crops)

missing_profiles = [
    crop for crop in existing_crops
    if crop not in CROP_PROFILES
]

if missing_profiles:
    raise ValueError(
        f"\nNo profile exists for: {missing_profiles}"
    )


# ============================================================
# CALCULATE BALANCED TARGET COUNTS
# ============================================================

crops = existing_crops
number_of_crops = len(crops)

base_count = TARGET_ROWS // number_of_crops
remainder = TARGET_ROWS % number_of_crops

target_counts = {}

for index, crop in enumerate(crops):

    target_counts[crop] = (
        base_count + 1
        if index < remainder
        else base_count
    )


print("\nTarget distribution:")

for crop in crops:
    print(
        f"{crop:15s} "
        f"{target_counts[crop]:5d}"
    )


# ============================================================
# GENERATE ADDITIONAL DATA
# ============================================================

generated_rows = []

numeric_columns = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "rainfall",
]


for crop in crops:

    crop_original = df[
        df["label"] == crop
    ].copy()

    original_count = len(crop_original)

    target_count = target_counts[crop]

    additional_count = (
        target_count - original_count
    )

    if additional_count <= 0:
        continue

    profile = CROP_PROFILES[crop]

    print(
        f"\nGenerating {additional_count:,} "
        f"records for {crop}..."
    )

    generated = {}

    for column in numeric_columns:

        low, high = profile[column]

        # Uniform base generation
        values = rng.uniform(
            low,
            high,
            additional_count,
        )

        # Blend with distribution from original
        # dataset when enough original data exists.
        original_values = (
            crop_original[column]
            .astype(float)
            .to_numpy()
        )

        if len(original_values) >= 10:

            sampled = rng.choice(
                original_values,
                size=additional_count,
                replace=True,
            )

            values = (
                values * 0.65
                + sampled * 0.35
            )

        values = np.clip(
            values,
            low,
            high,
        )

        generated[column] = values

    generated["label"] = [
        crop
    ] * additional_count

    generated_rows.append(
        pd.DataFrame(generated)
    )


# ============================================================
# COMBINE DATA
# ============================================================

if generated_rows:

    generated_df = pd.concat(
        generated_rows,
        ignore_index=True,
    )

else:

    generated_df = pd.DataFrame(
        columns=COLUMNS
    )


final_df = pd.concat(
    [
        df,
        generated_df,
    ],
    ignore_index=True,
)


# ============================================================
# ROUND VALUES
# ============================================================

final_df["N"] = (
    final_df["N"]
    .round()
    .astype(int)
)

final_df["P"] = (
    final_df["P"]
    .round()
    .astype(int)
)

final_df["K"] = (
    final_df["K"]
    .round()
    .astype(int)
)

final_df["temperature"] = (
    final_df["temperature"]
    .round(6)
)

final_df["humidity"] = (
    final_df["humidity"]
    .round(6)
)

final_df["rainfall"] = (
    final_df["rainfall"]
    .round(6)
)


# ============================================================
# SHUFFLE
# ============================================================

final_df = final_df.sample(
    frac=1,
    random_state=RANDOM_SEED,
).reset_index(drop=True)


# ============================================================
# FINAL VALIDATION
# ============================================================

if len(final_df) != TARGET_ROWS:
    raise ValueError(
        f"Expected {TARGET_ROWS:,} rows, "
        f"got {len(final_df):,}"
    )

if list(final_df.columns) != COLUMNS:
    raise ValueError(
        "Column structure changed."
    )

if final_df.isnull().sum().sum() != 0:
    raise ValueError(
        "Dataset contains missing values."
    )


# ============================================================
# SAVE
# ============================================================

final_df.to_csv(
    OUTPUT_FILE,
    index=False,
)


# ============================================================
# REPORT
# ============================================================

print("\n")
print("=" * 70)
print("DATASET CREATED SUCCESSFULLY")
print("=" * 70)

print(
    f"Total records : {len(final_df):,}"
)

print(
    f"Total crops   : "
    f"{final_df['label'].nunique()}"
)

print(
    f"Columns       : "
    f"{len(final_df.columns)}"
)

print(
    f"Missing values: "
    f"{final_df.isnull().sum().sum()}"
)

print("\nFinal crop distribution:")
print(
    final_df["label"]
    .value_counts()
    .sort_index()
)

print("\nDuplicate rows:")
print(
    final_df.duplicated().sum()
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("=" * 70)