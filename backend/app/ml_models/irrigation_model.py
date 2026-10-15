# =========================================================
# IRRIGATION MODEL
# Dataset + Crop + Soil Moisture + Weather + Random Forest
# =========================================================

from pathlib import Path
from functools import lru_cache

import joblib
import pandas as pd


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "app"
    / "ml_models"
    / "irrigation_model.pkl"
)

SCALER_PATH = (
    BASE_DIR
    / "app"
    / "ml_models"
    / "irrigation_scaler.pkl"
)


# =========================================================
# LAZY LOAD TRAINED MODEL
# =========================================================
#
# IMPORTANT FOR RENDER
#
# The old version loaded the irrigation model and scaler
# immediately when this Python module was imported.
#
# That means FastAPI loaded them during application startup,
# even when nobody was using irrigation.
#
# This version loads them ONLY when predict_irrigation()
# actually needs them.
#
# maxsize=1 ensures only one cached copy is retained.
# =========================================================


@lru_cache(maxsize=1)
def load_irrigation_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "Irrigation model not found: "
            f"{MODEL_PATH}"
        )

    try:

        print(
            "Loading irrigation model..."
        )

        loaded_model = joblib.load(
            MODEL_PATH
        )

        print(
            "Irrigation model loaded successfully."
        )

        return loaded_model

    except Exception as exc:

        print(
            "Warning: irrigation model could not "
            "be loaded:",
            exc
        )

        raise RuntimeError(
            "Irrigation model could not be loaded."
        ) from exc


@lru_cache(maxsize=1)
def load_irrigation_scaler():

    if not SCALER_PATH.exists():

        raise FileNotFoundError(
            "Irrigation scaler not found: "
            f"{SCALER_PATH}"
        )

    try:

        print(
            "Loading irrigation scaler..."
        )

        loaded_scaler = joblib.load(
            SCALER_PATH
        )

        print(
            "Irrigation scaler loaded successfully."
        )

        return loaded_scaler

    except Exception as exc:

        print(
            "Warning: irrigation scaler could not "
            "be loaded:",
            exc
        )

        raise RuntimeError(
            "Irrigation scaler could not be loaded."
        ) from exc


# =========================================================
# CROP WATER FACTOR
# =========================================================
# IMPORTANT:
# These values MUST match the irrigation training dataset.
# =========================================================

CROP_WATER_FACTOR = {

    # -----------------------------------------------------
    # Original crops used by the training dataset
    # -----------------------------------------------------

    "rice": 1.30,
    "maize": 1.00,
    "chickpea": 0.75,
    "cotton": 1.10,
    "wheat": 0.90,
    "groundnut": 0.85,
    "banana": 1.25,

    # -----------------------------------------------------
    # Additional crops
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
    "carrot": 0.90
}


# =========================================================
# CROP ALIASES
# =========================================================

CROP_ALIASES = {

    "pigeonpea": "pigeon_pea",
    "pigeon pea": "pigeon_pea",
    "pigeon-pea": "pigeon_pea",

    "ground nut": "groundnut",
    "ground-nut": "groundnut",

    "chilli pepper": "chilli",
    "chili": "chilli",

    "corn": "maize",

    "chick pea": "chickpea",
    "chick-pea": "chickpea",

    "sugar cane": "sugarcane",
    "sugar-cane": "sugarcane",

    "soy bean": "soybean",
    "soy-bean": "soybean",

    "ragi millet": "ragi"
}


# =========================================================
# CROP NORMALIZATION
# =========================================================

def normalize_crop(crop_type):

    if not crop_type:

        raise ValueError(
            "Crop type is required."
        )

    crop = (
        str(crop_type)
        .strip()
        .lower()
    )

    # -----------------------------------------------------
    # Normalize repeated spaces
    # -----------------------------------------------------

    crop = " ".join(
        crop.split()
    )

    # -----------------------------------------------------
    # Check aliases
    # -----------------------------------------------------

    if crop in CROP_ALIASES:

        crop = CROP_ALIASES[crop]

    # -----------------------------------------------------
    # Convert hyphen format
    # -----------------------------------------------------

    normalized = crop.replace(
        "-",
        "_"
    )

    if normalized in CROP_WATER_FACTOR:

        crop = normalized

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

    crop = normalize_crop(
        data.crop_type
    )

    crop_water_factor = (
        CROP_WATER_FACTOR[crop]
    )

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
            float(crop_water_factor)
    }

    return pd.DataFrame(
        [features]
    )


# =========================================================
# CROP-SPECIFIC MOISTURE LIMITS
# =========================================================

CROP_MOISTURE_LIMITS = {

    "rice": {
        "critical": 25,
        "low": 35,
        "good": 55
    },

    "maize": {
        "critical": 25,
        "low": 35,
        "good": 55
    },

    "chickpea": {
        "critical": 20,
        "low": 30,
        "good": 50
    },

    "cotton": {
        "critical": 23,
        "low": 32,
        "good": 52
    },

    "wheat": {
        "critical": 23,
        "low": 32,
        "good": 52
    },

    "groundnut": {
        "critical": 22,
        "low": 32,
        "good": 52
    },

    "banana": {
        "critical": 30,
        "low": 40,
        "good": 60
    },

    "sugarcane": {
        "critical": 30,
        "low": 42,
        "good": 65
    },

    "tomato": {
        "critical": 25,
        "low": 35,
        "good": 55
    },

    "potato": {
        "critical": 23,
        "low": 33,
        "good": 55
    },

    "onion": {
        "critical": 20,
        "low": 30,
        "good": 50
    },

    "turmeric": {
        "critical": 25,
        "low": 35,
        "good": 55
    },

    "chilli": {
        "critical": 23,
        "low": 33,
        "good": 53
    },

    "millet": {
        "critical": 18,
        "low": 28,
        "good": 48
    },

    "ragi": {
        "critical": 18,
        "low": 28,
        "good": 48
    },

    "soybean": {
        "critical": 23,
        "low": 33,
        "good": 55
    },

    "pigeon_pea": {
        "critical": 20,
        "low": 30,
        "good": 50
    },

    "okra": {
        "critical": 25,
        "low": 35,
        "good": 55
    },

    "cabbage": {
        "critical": 25,
        "low": 35,
        "good": 55
    },

    "carrot": {
        "critical": 22,
        "low": 32,
        "good": 52
    },

    "sorghum": {
        "critical": 20,
        "low": 30,
        "good": 50
    }
}


# =========================================================
# IRRIGATION DECISION
# =========================================================

def calculate_irrigation_decision(
    crop,
    soil_moisture,
    humidity,
    temperature,
    rainfall,
    rain_forecast,
    wind_speed
):

    limits = CROP_MOISTURE_LIMITS.get(
        crop,
        {
            "critical": 25,
            "low": 35,
            "good": 55
        }
    )

    critical = limits["critical"]
    low = limits["low"]
    good = limits["good"]

    # =====================================================
    # HEAVY RAINFALL PROTECTION
    # =====================================================

    if rainfall >= 5:

        if soil_moisture <= critical:

            return (
                "Irrigate soon",

                "Soil moisture is very low despite recent rainfall. "
                "Monitor the field closely and provide water if moisture "
                "does not recover."
            )

        return (
            "No irrigation",

            "Recent rainfall has reduced the need for irrigation."
        )

    # =====================================================
    # STRONG RAIN FORECAST
    # =====================================================

    if rain_forecast >= 70:

        if soil_moisture <= critical:

            return (
                "Monitor",

                "Soil moisture is low, but significant rainfall is "
                "forecast. Recheck the field before irrigating."
            )

        return (
            "No irrigation",

            "Rain is expected soon, so irrigation can be avoided."
        )

    # =====================================================
    # CRITICAL MOISTURE
    # =====================================================

    if soil_moisture <= critical:

        return (
            "Irrigate now",

            "Soil moisture is critically low."
        )

    # =====================================================
    # LOW MOISTURE
    # =====================================================

    if soil_moisture <= low:

        if (
            temperature >= 32
            and humidity <= 45
            and rain_forecast < 40
        ):

            return (
                "Irrigate now",

                "Soil moisture is low and hot, dry weather is "
                "increasing the crop's water requirement."
            )

        return (
            "Irrigate soon",

            "Soil moisture is below the recommended range "
            "for this crop."
        )

    # =====================================================
    # MODERATE MOISTURE + HOT WEATHER
    # =====================================================

    if (
        soil_moisture < good
        and temperature >= 35
        and humidity < 40
        and rain_forecast < 30
    ):

        return (
            "Irrigate soon",

            "The soil still contains moisture, but hot and dry "
            "conditions are increasing water demand."
        )

    # =====================================================
    # HIGH WIND + MODERATE MOISTURE
    # =====================================================

    if (
        soil_moisture < good
        and wind_speed >= 25
        and humidity < 50
        and rain_forecast < 30
    ):

        return (
            "Irrigate soon",

            "Dry and windy conditions may increase water loss "
            "from the soil."
        )

    # =====================================================
    # SUFFICIENT MOISTURE
    # =====================================================

    if soil_moisture >= good:

        return (
            "No irrigation",

            "Soil moisture is sufficient for the crop."
        )

    # =====================================================
    # DEFAULT
    # =====================================================

    return (
        "Monitor",

        "Soil moisture is currently acceptable. Continue "
        "monitoring the field conditions."
    )


# =========================================================
# IRRIGATION PREDICTION
# =========================================================

def predict_irrigation(features):

    if features is None:

        raise ValueError(
            "Irrigation features are missing."
        )

    if features.empty:

        raise ValueError(
            "Irrigation feature data is empty."
        )

    # =====================================================
    # READ VALUES
    # =====================================================

    soil_moisture = float(
        features["soil_moisture"].iloc[0]
    )

    humidity = float(
        features["humidity"].iloc[0]
    )

    temperature = float(
        features["temperature"].iloc[0]
    )

    rainfall = float(
        features["rainfall"].iloc[0]
    )

    rain_forecast = float(
        features["rain_forecast"].iloc[0]
    )

    wind_speed = float(
        features["wind_speed"].iloc[0]
    )

    crop_water_factor = float(
        features["crop_water_factor"].iloc[0]
    )

    # =====================================================
    # IDENTIFY CROP
    # =====================================================

    crop = None

    for name, factor in CROP_WATER_FACTOR.items():

        if abs(
            factor - crop_water_factor
        ) < 0.0001:

            crop = name

            break

    if crop is None:

        crop = "rice"

    # =====================================================
    # FINAL AGRICULTURAL DECISION
    # =====================================================

    status, reason = calculate_irrigation_decision(

        crop=crop,

        soil_moisture=soil_moisture,

        humidity=humidity,

        temperature=temperature,

        rainfall=rainfall,

        rain_forecast=rain_forecast,

        wind_speed=wind_speed
    )

    # =====================================================
    # ML PREDICTION
    # =====================================================

    ml_prediction = None

    prediction_probabilities = {}

    try:

        # -------------------------------------------------
        # LAZY LOAD MODEL ONLY WHEN IRRIGATION IS USED
        # -------------------------------------------------

        model = load_irrigation_model()

        scaler = load_irrigation_scaler()

        model_columns = [

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
            "crop_water_factor"

        ]

        model_features = (

            features[
                model_columns
            ]
            .copy()
            .astype(float)

        )

        # -------------------------------------------------
        # SCALE
        # -------------------------------------------------

        values = scaler.transform(
            model_features
        )

        # -------------------------------------------------
        # RANDOM FOREST PREDICTION
        # -------------------------------------------------

        prediction = model.predict(
            values
        )

        if len(prediction) > 0:

            ml_prediction = str(
                prediction[0]
            )

        print(
            "ML irrigation prediction:",
            ml_prediction
        )

        # -------------------------------------------------
        # PREDICTION PROBABILITIES
        # -------------------------------------------------

        if hasattr(
            model,
            "predict_proba"
        ):

            probabilities = (
                model.predict_proba(
                    values
                )
            )

            classes = model.classes_

            if len(probabilities) > 0:

                prediction_probabilities = {

                    str(label):

                        round(
                            float(probability),
                            4
                        )

                    for label, probability
                    in zip(
                        classes,
                        probabilities[0]
                    )

                }

                print(
                    "Prediction probabilities:",
                    prediction_probabilities
                )

    except Exception as exc:

        # -------------------------------------------------
        # IMPORTANT:
        #
        # Keep your original behavior:
        # if ML prediction fails, the rule-based
        # agricultural decision still works.
        # -------------------------------------------------

        print(
            "ML prediction skipped:",
            exc
        )

    # =====================================================
    # IRRIGATION SCORE
    # =====================================================

    limits = CROP_MOISTURE_LIMITS.get(

        crop,

        {
            "critical": 25,
            "low": 35,
            "good": 55
        }
    )

    critical = float(
        limits["critical"]
    )

    good = float(
        limits["good"]
    )

    moisture_stress = max(
        0.0,
        good - soil_moisture
    )

    temperature_stress = max(
        0.0,
        temperature - 25.0
    ) * 0.50

    humidity_stress = max(
        0.0,
        50.0 - humidity
    ) * 0.15

    wind_stress = max(
        0.0,
        wind_speed - 20.0
    ) * 0.10

    rainfall_relief = min(
        rainfall * 1.5,
        15.0
    )

    forecast_relief = (
        rain_forecast / 10.0
    )

    irrigation_score = (

        moisture_stress
        + temperature_stress
        + humidity_stress
        + wind_stress
        - rainfall_relief
        - forecast_relief

    )

    # =====================================================
    # CRITICAL MOISTURE OVERRIDE
    # =====================================================

    if soil_moisture <= critical:

        irrigation_score = max(
            irrigation_score,
            75.0
        )

    irrigation_score = max(
        0.0,
        min(
            100.0,
            float(irrigation_score)
        )
    )

    # =====================================================
    # WATER NEED
    # =====================================================

    if status == "Irrigate now":

        water_need = "HIGH"

    elif status == "Irrigate soon":

        water_need = "MEDIUM"

    elif status == "Monitor":

        water_need = "LOW"

    else:

        water_need = "NONE"

    # =====================================================
    # NOTIFICATION REQUIRED
    # =====================================================

    notification_required = (
        status in [
            "Irrigate now",
            "Irrigate soon"
        ]
    )

    # =====================================================
    # FINAL RESULT
    # =====================================================

    return {

        "irrigation_status":
            status,

        "water_need":
            water_need,

        "reason":
            reason,

        "crop_type":
            crop,

        "soil_moisture":
            round(
                soil_moisture,
                2
            ),

        "temperature":
            round(
                temperature,
                2
            ),

        "humidity":
            round(
                humidity,
                2
            ),

        "rainfall":
            round(
                rainfall,
                2
            ),

        "rain_forecast":
            round(
                rain_forecast,
                2
            ),

        "irrigation_score":
            round(
                irrigation_score,
                3
            ),

        "ml_prediction":
            ml_prediction,

        "prediction_probabilities":
            prediction_probabilities,

        "notification_required":
            notification_required,

        "model":
            "Random Forest + Irrigation Dataset + Weather + Soil Moisture",

        "features_used":
            11

    }