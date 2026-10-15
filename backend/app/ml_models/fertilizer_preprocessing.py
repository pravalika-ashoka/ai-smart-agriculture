import numpy as np


FEATURE_NAMES = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "moisture",
    "temperature"
]


def preprocess_fertilizer(data):

    features = np.array(
        [
            data.nitrogen,
            data.phosphorus,
            data.potassium,
            data.moisture,
            data.temperature
        ],
        dtype=float
    )

    # Check for invalid numeric values
    if not np.all(
        np.isfinite(features)
    ):
        raise ValueError(
            "Fertilizer input contains "
            "invalid numeric values."
        )

    # Convert to model input shape
    features = features.reshape(
        1,
        -1
    )

    return features