from pathlib import Path
import shutil
import numpy as np
import pandas as pd


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "fertilizer_data.csv"

BACKUP_FILE = (
    BASE_DIR /
    "fertilizer_data_backup_12_records.csv"
)

OUTPUT_FILE = BASE_DIR / "fertilizer_data.csv"

TARGET_RECORDS = 50000

RANDOM_SEED = 42


# =========================================================
# FERTILIZER PROFILES
# =========================================================

PROFILES = {

    "Urea": {

        "weight": 0.20,

        "n_range": (10, 45),

        "p_range": (5, 35),

        "k_range": (10, 50),

        "moisture_range": (15, 55),

        "temp_range": (20, 40),

        "advice":
            "Nitrogen is relatively low. Urea can be applied "
            "to improve nitrogen availability and support "
            "vegetative growth."

    },


    "DAP": {

        "weight": 0.17,

        "n_range": (15, 55),

        "p_range": (25, 65),

        "k_range": (15, 55),

        "moisture_range": (20, 60),

        "temp_range": (18, 38),

        "advice":
            "DAP provides nitrogen and phosphorus. It can "
            "support root development and improve nutrient "
            "availability."

    },


    "NPK 10-10-10": {

        "weight": 0.17,

        "n_range": (45, 75),

        "p_range": (30, 60),

        "k_range": (35, 65),

        "moisture_range": (30, 65),

        "temp_range": (18, 35),

        "advice":
            "A balanced NPK fertilizer is recommended to "
            "maintain nitrogen, phosphorus, and potassium "
            "levels."

    },


    "NPK 10-26-26": {

        "weight": 0.15,

        "n_range": (35, 65),

        "p_range": (50, 85),

        "k_range": (50, 85),

        "moisture_range": (25, 65),

        "temp_range": (18, 35),

        "advice":
            "This fertilizer is higher in phosphorus and "
            "potassium and can support root development "
            "and overall crop growth."

    },


    "NPK 20-20-20": {

        "weight": 0.16,

        "n_range": (60, 95),

        "p_range": (55, 90),

        "k_range": (55, 90),

        "moisture_range": (30, 70),

        "temp_range": (18, 35),

        "advice":
            "A balanced higher-strength NPK fertilizer is "
            "recommended when nitrogen, phosphorus, and "
            "potassium requirements are relatively high."

    },


    "Potassium Sulphate": {

        "weight": 0.15,

        "n_range": (40, 85),

        "p_range": (20, 65),

        "k_range": (70, 100),

        "moisture_range": (25, 70),

        "temp_range": (18, 38),

        "advice":
            "Potassium sulphate can support potassium "
            "requirements and improve plant strength and "
            "crop quality. Avoid unnecessary application "
            "when potassium is already sufficient."

    }

}


# =========================================================
# COLUMNS
# =========================================================

COLUMNS = [

    "nitrogen",

    "phosphorus",

    "potassium",

    "moisture",

    "temperature",

    "recommended_fertilizer",

    "advice"

]


# =========================================================
# HELPERS
# =========================================================

def sample_int(
    rng,
    low,
    high
):

    return int(
        round(
            rng.uniform(
                low,
                high
            )
        )
    )


def sample_float(
    rng,
    low,
    high
):

    return round(
        float(
            rng.uniform(
                low,
                high
            )
        ),
        1
    )


def generate_row(
    rng,
    fertilizer
):

    profile = PROFILES[
        fertilizer
    ]

    return {

        "nitrogen":
            sample_int(
                rng,
                *profile["n_range"]
            ),

        "phosphorus":
            sample_int(
                rng,
                *profile["p_range"]
            ),

        "potassium":
            sample_int(
                rng,
                *profile["k_range"]
            ),

        "moisture":
            sample_int(
                rng,
                *profile["moisture_range"]
            ),

        "temperature":
            sample_int(
                rng,
                *profile["temp_range"]
            ),

        "recommended_fertilizer":
            fertilizer,

        "advice":
            profile["advice"]

    }


# =========================================================
# MAIN
# =========================================================

def main():

    rng = np.random.default_rng(
        RANDOM_SEED
    )


    # -----------------------------------------------------
    # Check existing dataset
    # -----------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )


    original = pd.read_csv(
        INPUT_FILE
    )


    # -----------------------------------------------------
    # Validate columns
    # -----------------------------------------------------

    missing = [

        column

        for column in COLUMNS

        if column not in original.columns

    ]


    if missing:

        raise ValueError(
            f"Missing required columns: {missing}"
        )


    # -----------------------------------------------------
    # Backup original dataset
    # -----------------------------------------------------

    shutil.copy2(
        INPUT_FILE,
        BACKUP_FILE
    )


    print(
        f"Backup created: {BACKUP_FILE}"
    )


    # -----------------------------------------------------
    # Keep original records
    # -----------------------------------------------------

    original = original[
        COLUMNS
    ].copy()


    original_count = len(
        original
    )


    remaining = (
        TARGET_RECORDS -
        original_count
    )


    if remaining < 0:

        raise ValueError(
            "Existing dataset already contains "
            "more records than the target."
        )


    # -----------------------------------------------------
    # Fertilizer classes
    # -----------------------------------------------------

    fertilizers = list(
        PROFILES.keys()
    )


    weights = np.array(

        [
            PROFILES[
                fertilizer
            ]["weight"]

            for fertilizer in fertilizers
        ],

        dtype=float

    )


    weights = (
        weights /
        weights.sum()
    )


    # -----------------------------------------------------
    # Generate labels
    # -----------------------------------------------------

    labels = rng.choice(

        fertilizers,

        size=remaining,

        p=weights

    )


    # -----------------------------------------------------
    # Generate records
    # -----------------------------------------------------

    generated_rows = [

        generate_row(
            rng,
            fertilizer
        )

        for fertilizer in labels

    ]


    generated = pd.DataFrame(

        generated_rows,

        columns=COLUMNS

    )


    # -----------------------------------------------------
    # Combine original + generated data
    # -----------------------------------------------------

    final_df = pd.concat(

        [
            original,
            generated
        ],

        ignore_index=True

    )


    # -----------------------------------------------------
    # Shuffle dataset
    # -----------------------------------------------------

    final_df = final_df.sample(

        frac=1,

        random_state=RANDOM_SEED

    ).reset_index(
        drop=True
    )


    # -----------------------------------------------------
    # Validate record count
    # -----------------------------------------------------

    if len(final_df) != TARGET_RECORDS:

        raise RuntimeError(

            f"Expected {TARGET_RECORDS} records, "
            f"got {len(final_df)}."

        )


    # -----------------------------------------------------
    # Validate columns
    # -----------------------------------------------------

    if list(
        final_df.columns
    ) != COLUMNS:

        raise RuntimeError(
            "Final column order is incorrect."
        )


    # -----------------------------------------------------
    # Save dataset
    # -----------------------------------------------------

    final_df.to_csv(

        OUTPUT_FILE,

        index=False

    )


    # =====================================================
    # REPORT
    # =====================================================

    print()
    print("=" * 60)
    print(
        "FERTILIZER DATASET UPDATED SUCCESSFULLY"
    )
    print("=" * 60)

    print()

    print(
        f"Original records : {original_count}"
    )

    print(
        f"Generated records: {remaining}"
    )

    print(
        f"Final records    : {len(final_df)}"
    )

    print()

    print(
        "Fertilizer class distribution:"
    )

    print(
        final_df[
            "recommended_fertilizer"
        ].value_counts()
    )

    print()

    print(
        "Feature ranges:"
    )

    print(

        final_df[
            [
                "nitrogen",
                "phosphorus",
                "potassium",
                "moisture",
                "temperature"
            ]
        ].describe().loc[
            [
                "min",
                "max"
            ]
        ]

    )

    print()

    print(
        f"Backup : {BACKUP_FILE}"
    )

    print(
        f"Dataset: {OUTPUT_FILE}"
    )

    print("=" * 60)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()