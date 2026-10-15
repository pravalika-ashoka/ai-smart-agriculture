import pandas as pd

from app.ml_models.irrigation_model import (
    predict_irrigation
)


# =========================================================
# TEST CASES
# =========================================================

tests = [

    {
        "name": "Very dry field",
        "soil_moisture": 15,
        "humidity": 25,
        "temperature": 35,
        "rainfall": 0,
        "soil_temperature": 30,
        "wind_speed": 20,
        "rain_forecast": 0,
        "nitrogen": 50,
        "phosphorus": 30,
        "potassium": 40,
        "crop_water_factor": 1.0
    },

    {
        "name": "Low moisture",
        "soil_moisture": 30,
        "humidity": 40,
        "temperature": 32,
        "rainfall": 1,
        "soil_temperature": 28,
        "wind_speed": 15,
        "rain_forecast": 0,
        "nitrogen": 60,
        "phosphorus": 35,
        "potassium": 45,
        "crop_water_factor": 1.0
    },

    {
        "name": "Moderate moisture",
        "soil_moisture": 45,
        "humidity": 55,
        "temperature": 28,
        "rainfall": 2,
        "soil_temperature": 26,
        "wind_speed": 10,
        "rain_forecast": 0,
        "nitrogen": 70,
        "phosphorus": 40,
        "potassium": 50,
        "crop_water_factor": 1.0
    },

    {
        "name": "Wet field",
        "soil_moisture": 65,
        "humidity": 70,
        "temperature": 25,
        "rainfall": 10,
        "soil_temperature": 24,
        "wind_speed": 8,
        "rain_forecast": 0,
        "nitrogen": 80,
        "phosphorus": 45,
        "potassium": 60,
        "crop_water_factor": 1.0
    },

]


# =========================================================
# RUN TESTS
# =========================================================

for test in tests:

    name = test.pop("name")

    features = pd.DataFrame([test])

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    try:

        result = predict_irrigation(
            features
        )

        print(
            "Status:",
            result["irrigation_status"]
        )

        print(
            "Water need:",
            result["water_need"]
        )

        print(
            "Reason:",
            result["reason"]
        )

        print(
            "ML prediction:",
            result["ml_prediction"]
        )

        print(
            "Notification:",
            result["notification_required"]
        )

    except Exception as exc:

        print(
            "ERROR:",
            exc
        )