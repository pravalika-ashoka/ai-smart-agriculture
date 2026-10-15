import pandas as pd


# =========================================================
# CROP WATER FACTORS
# =========================================================

CROP_WATER_FACTOR = {

    # -----------------------------------------------------
    # ORIGINAL CROPS
    # -----------------------------------------------------

    "rice": 1.30,
    "maize": 1.00,
    "chickpea": 0.75,
    "cotton": 1.10,
    "wheat": 0.90,
    "groundnut": 0.85,
    "banana": 1.25,

    # -----------------------------------------------------
    # ADDITIONAL CROPS
    # -----------------------------------------------------

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
# CROP ALIASES
# =========================================================
# This allows the backend to understand alternate spellings
# without changing the crop names sent by the frontend.
# =========================================================

CROP_ALIASES = {

    "pigeonpea": "pigeon_pea",
    "pigeon pea": "pigeon_pea",
    "pigeon-pea": "pigeon_pea",

    "ground nut": "groundnut",
    "ground-nut": "groundnut",

    "chilli pepper": "chilli",
    "chili": "chilli",

    "maize": "maize",
    "corn": "maize",

    "chick pea": "chickpea",
    "chick-pea": "chickpea",

    "sugar cane": "sugarcane",
    "sugar-cane": "sugarcane",

    "soy bean": "soybean",
    "soy-bean": "soybean",

    "ragi millet": "ragi",
}


# =========================================================
# CROP NORMALIZATION
# =========================================================

def normalize_crop(crop_type):

    if not crop_type:
        raise ValueError(
            "Crop type is required."
        )

    crop = str(crop_type).strip().lower()

    # -----------------------------------------------------
    # Replace spaces around the crop name
    # -----------------------------------------------------

    crop = " ".join(crop.split())

    # -----------------------------------------------------
    # Check aliases first
    # -----------------------------------------------------

    if crop in CROP_ALIASES:

        crop = CROP_ALIASES[crop]

    # -----------------------------------------------------
    # Convert common separator format
    # -----------------------------------------------------

    if crop.replace("-", "_") in CROP_WATER_FACTOR:

        crop = crop.replace("-", "_")

    # -----------------------------------------------------
    # Validate crop
    # -----------------------------------------------------

    if crop not in CROP_WATER_FACTOR:

        raise ValueError(
            f"Unsupported crop type: {crop_type}"
        )

    return crop


# =========================================================
# PREPROCESS IRRIGATION
# =========================================================

def preprocess_irrigation(data):

    # -----------------------------------------------------
    # Normalize crop
    # -----------------------------------------------------

    crop = normalize_crop(
        data.crop_type
    )

    # -----------------------------------------------------
    # Get crop water factor
    # -----------------------------------------------------

    crop_water_factor = (
        CROP_WATER_FACTOR[crop]
    )

    # -----------------------------------------------------
    # Prepare irrigation features
    # -----------------------------------------------------

    features = {

        "soil_moisture":
            float(data.soil_moisture),

        "humidity":
            float(data.humidity),

        "temperature":
            float(data.temperature),

        "rainfall":
            float(data.rainfall),

        "soil_temperature":
            float(data.soil_temperature),

        "wind_speed":
            float(data.wind_speed),

        "rain_forecast":
            float(data.rain_forecast),

        "nitrogen":
            float(data.nitrogen),

        "phosphorus":
            float(data.phosphorus),

        "potassium":
            float(data.potassium),

        "crop_water_factor":
            float(crop_water_factor),
    }

    # -----------------------------------------------------
    # Return DataFrame
    # -----------------------------------------------------

    return pd.DataFrame(
        [features]
    )