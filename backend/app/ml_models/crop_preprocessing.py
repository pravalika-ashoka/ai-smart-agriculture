import numpy as np


# =========================================================
# CROP FEATURE ORDER
# =========================================================

FEATURE_COLUMNS = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "temperature",
    "humidity",
    "rainfall"
]


def preprocess_crop(data):
    """
    Convert CropInput into the feature format
    required by the crop model.

    Feature order:

        0 - nitrogen
        1 - phosphorus
        2 - potassium
        3 - temperature
        4 - humidity
        5 - rainfall
    """

    features = np.array(
        [
            data.nitrogen,
            data.phosphorus,
            data.potassium,
            data.temperature,
            data.humidity,
            data.rainfall
        ],
        dtype=float
    )

    # Expected shape: (1, 7)

    return features.reshape(1, -1)