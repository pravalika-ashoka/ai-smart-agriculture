import os
import numpy as np
import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset"
)

SOURCE_FILE = os.path.join(
    DATASET_DIR,
    "soil_data.csv"
)

OUTPUT_FILE = os.path.join(
    DATASET_DIR,
    "soil_data_50000.csv"
)

TARGET_RECORDS = 50000

RANDOM_STATE = 42

rng = np.random.default_rng(
    RANDOM_STATE
)


# =========================================================
# LOAD ORIGINAL DATASET
# =========================================================

print("=" * 60)
print("SOIL DATASET GENERATION")
print("=" * 60)

df = pd.read_csv(
    SOURCE_FILE
)

print(
    f"Original records : {len(df)}"
)

print(
    f"Target records   : {TARGET_RECORDS}"
)


# =========================================================
# VALIDATE DATASET
# =========================================================

FEATURES = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "moisture",
    "temperature"
]

TARGET = "soil_health"

required_columns = FEATURES + [TARGET]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {missing_columns}"
    )


df = df[
    required_columns
].dropna().copy()


# =========================================================
# ORIGINAL CLASS DISTRIBUTION
# =========================================================

print()
print("Original class distribution:")
print(
    df[TARGET].value_counts()
)


# =========================================================
# GENERATE ADDITIONAL RECORDS
# =========================================================

additional_records = (
    TARGET_RECORDS - len(df)
)

if additional_records <= 0:

    raise ValueError(
        "The source dataset already contains "
        f"{len(df)} records."
    )


# Keep approximately the same class distribution
class_distribution = (
    df[TARGET]
    .value_counts(
        normalize=True
    )
)


generated_parts = []


for class_name, proportion in (
    class_distribution.items()
):

    class_count = int(
        round(
            additional_records
            * proportion
        )
    )

    class_df = df[
        df[TARGET] == class_name
    ]

    # Randomly select existing rows
    # and create controlled variations.
    indices = rng.integers(
        0,
        len(class_df),
        size=class_count
    )

    generated = (
        class_df
        .iloc[indices]
        .copy()
        .reset_index(drop=True)
    )


    # -----------------------------------------------------
    # Add small realistic variations
    # -----------------------------------------------------

    generated["nitrogen"] += (
        rng.normal(
            0,
            3.0,
            class_count
        )
    )

    generated["phosphorus"] += (
        rng.normal(
            0,
            2.0,
            class_count
        )
    )

    generated["potassium"] += (
        rng.normal(
            0,
            3.0,
            class_count
        )
    )

    generated["moisture"] += (
        rng.normal(
            0,
            1.5,
            class_count
        )
    )

    generated["temperature"] += (
        rng.normal(
            0,
            0.5,
            class_count
        )
    )


    # -----------------------------------------------------
    # Keep values within original ranges
    # -----------------------------------------------------

    generated["nitrogen"] = (
        generated["nitrogen"]
        .clip(10, 150)
    )

    generated["phosphorus"] = (
        generated["phosphorus"]
        .clip(5, 100)
    )

    generated["potassium"] = (
        generated["potassium"]
        .clip(5, 150)
    )

    generated["moisture"] = (
        generated["moisture"]
        .clip(10, 80)
    )

    generated["temperature"] = (
        generated["temperature"]
        .clip(15, 42)
    )


    generated_parts.append(
        generated
    )


# =========================================================
# COMBINE DATA
# =========================================================

generated_df = pd.concat(
    generated_parts,
    ignore_index=True
)


# Make sure we have exactly the requested
# number of additional records.

if len(generated_df) > additional_records:

    generated_df = (
        generated_df
        .sample(
            n=additional_records,
            random_state=RANDOM_STATE
        )
        .reset_index(drop=True)
    )


elif len(generated_df) < additional_records:

    difference = (
        additional_records
        - len(generated_df)
    )

    extra = (
        generated_df
        .sample(
            n=difference,
            replace=True,
            random_state=RANDOM_STATE
        )
        .copy()
    )

    generated_df = pd.concat(
        [
            generated_df,
            extra
        ],
        ignore_index=True
    )


# =========================================================
# FINAL DATASET
# =========================================================

final_df = pd.concat(
    [
        df,
        generated_df
    ],
    ignore_index=True
)


# Shuffle records

final_df = (
    final_df
    .sample(
        frac=1,
        random_state=RANDOM_STATE
    )
    .reset_index(drop=True)
)


# Round numerical values

final_df["nitrogen"] = (
    final_df["nitrogen"].round(2)
)

final_df["phosphorus"] = (
    final_df["phosphorus"].round(2)
)

final_df["potassium"] = (
    final_df["potassium"].round(2)
)

final_df["moisture"] = (
    final_df["moisture"].round(2)
)

final_df["temperature"] = (
    final_df["temperature"].round(2)
)


# =========================================================
# SAVE
# =========================================================

final_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# VERIFICATION
# =========================================================

print()
print("=" * 60)
print("SOIL DATASET CREATED")
print("=" * 60)

print(
    f"Records : {len(final_df)}"
)

print(
    f"Columns : {list(final_df.columns)}"
)

print()
print("Class distribution:")

print(
    final_df[TARGET].value_counts()
)

print()
print(
    "Saved to:"
)

print(
    OUTPUT_FILE
)

print("=" * 60)