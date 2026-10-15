from app.ml_models.soil_model import predict_soil


def predict_soil_service(data):

    features = [[

        data.nitrogen,

        data.phosphorus,

        data.potassium,

        data.moisture,

        data.temperature

    ]]

    result = predict_soil(
        features
    )

    return {

        "soil_status":
            result["soil_health"],

        "confidence":
            round(
                result["confidence"] * 100,
                2
            ),

        "accuracy":
            round(
                result["accuracy"] * 100,
                2
            ),

        "probabilities":
            result["probabilities"]

    }