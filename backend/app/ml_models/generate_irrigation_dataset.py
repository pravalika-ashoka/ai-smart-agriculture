import pandas as pd
import random

from pathlib import Path


# =========================================================
# Paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    BASE_DIR
    / "dataset"
    / "irrigation_training_data.csv"
)


# =========================================================
# Crop factors
# =========================================================

CROPS = {
    "rice": 1.30,
    "maize": 1.00,
    "chickpea": 0.75,
    "cotton": 1.10,
    "wheat": 0.90,
    "groundnut": 0.85,
    "banana": 1.25
}


# =========================================================
# Irrigation recommendation
# =========================================================

def calculate_irrigation(
    soil_moisture,
    rainfall,
    rain_forecast,
    temperature,
    crop_factor
):

    # Strong irrigation requirement
    if (
        soil_moisture < 25
        and rainfall < 5
        and rain_forecast == 0
    ):
        return "Irrigate now"

    # High water demand
    if (
        soil_moisture < 35
        and rainfall < 10
        and temperature >= 30
    ):
        return "Irrigate now"

    # Moderate requirement
    if (
        soil_moisture < 40
        and rainfall < 15
    ):
        return "Irrigate soon"

    # Crop with higher water requirement
    if (
        soil_moisture < 45
        and crop_factor >= 1.20
        and rainfall < 20
    ):
        return "Irrigate soon"

    # Adequate moisture
    if (
        soil_moisture >= 50
        or rainfall >= 25
    ):
        return "No irrigation"

    return "Monitor"


# =========================================================
# Generate dataset
# =========================================================

def generate_dataset(
    number_of_rows=50000
):

    random.seed(42)

    rows = []

    crop_names = list(
        CROPS.keys()
    )

    for _ in range(
        number_of_rows
    ):

        # -------------------------------------------------
        # Environmental values
        # -------------------------------------------------

        soil_moisture = random.uniform(
            15,
            70
        )

        humidity = random.uniform(
            20,
            90
        )

        temperature = random.uniform(
            20,
            40
        )

        rainfall = random.uniform(
            0,
            40
        )

        soil_temperature = random.uniform(
            20,
            35
        )

        wind_speed = random.uniform(
            2,
            30
        )

        rain_forecast = random.choice(
            [0, 1]
        )

        # -------------------------------------------------
        # Soil nutrients
        # -------------------------------------------------

        nitrogen = random.uniform(
            20,
            120
        )

        phosphorus = random.uniform(
            10,
            70
        )

        potassium = random.uniform(
            15,
            80
        )

        # -------------------------------------------------
        # Crop
        # -------------------------------------------------

        crop_type = random.choice(
            crop_names
        )

        crop_factor = CROPS[
            crop_type
        ]

        # -------------------------------------------------
        # Target
        # -------------------------------------------------

        recommendation = calculate_irrigation(

            soil_moisture,

            rainfall,

            rain_forecast,

            temperature,

            crop_factor
        )

        rows.append({

            "soil_moisture":
                round(
                    soil_moisture,
                    2
                ),

            "humidity":
                round(
                    humidity,
                    2
                ),

            "temperature":
                round(
                    temperature,
                    2
                ),

            "rainfall":
                round(
                    rainfall,
                    2
                ),

            "soil_temperature":
                round(
                    soil_temperature,
                    2
                ),

            "wind_speed":
                round(
                    wind_speed,
                    2
                ),

            "rain_forecast":
                rain_forecast,

            "nitrogen":
                round(
                    nitrogen,
                    2
                ),

            "phosphorus":
                round(
                    phosphorus,
                    2
                ),

            "potassium":
                round(
                    potassium,
                    2
                ),


            "crop_type":
                crop_type,

            "crop_water_factor":
                crop_factor,

            "irrigation_recommendation":
                recommendation
        })

    # -----------------------------------------------------
    # DataFrame
    # -----------------------------------------------------

    df = pd.DataFrame(
        rows
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "Irrigation training dataset created."
    )

    print(
        "File:",
        OUTPUT_FILE
    )

    print(
        "Rows:",
        len(df)
    )

    print(
        "Columns:",
        len(df.columns)
    )

    print(
        "\nRecommendation distribution:"
    )

    print(
        df[
            "irrigation_recommendation"
        ].value_counts()
    )


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":

    generate_dataset(
        number_of_rows=50000
    )