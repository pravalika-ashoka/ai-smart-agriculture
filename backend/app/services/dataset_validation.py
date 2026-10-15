import pandas as pd


CROP_REQUIRED_COLUMNS = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "moisture",
    "temperature",
    "rainfall",
    "crop"
]


def validate_crop_dataset(df: pd.DataFrame):

    if df.empty:
        raise ValueError(
            "Crop dataset is empty."
        )

    missing = [
        column
        for column in CROP_REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing crop dataset columns: "
            + ", ".join(missing)
        )

    # Convert numeric fields
    for column in CROP_REQUIRED_COLUMNS[:-1]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Remove invalid records
    df = df.dropna(
        subset=CROP_REQUIRED_COLUMNS
    )

    # Clean crop names
    df["crop"] = (
        df["crop"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df = df[df["crop"] != ""]

    if df.empty:
        raise ValueError(
            "No valid records remain after dataset cleaning."
        )

    return df