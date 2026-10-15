from fastapi import APIRouter, HTTPException, Depends

from app.schemas.soil_schema import SoilInput
from app.ml_models.soil_model import predict_soil
from app.ml_models.explainability import generate_explanation


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/soil",
    tags=["Soil Analysis"]
)


# =========================================================
# SOIL ANALYSIS
# =========================================================

@router.post("/analyze")
def analyze_soil(
    data: SoilInput
):

    try:

        # -------------------------------------------------
        # Convert request data to model format
        # -------------------------------------------------

        features = [[

            data.nitrogen,

            data.phosphorus,

            data.potassium,

            data.moisture,

            data.temperature

        ]]

        # -------------------------------------------------
        # Soil prediction
        # -------------------------------------------------

        result = predict_soil(
            features
        )

        # -------------------------------------------------
        # SHAP explanation
        # -------------------------------------------------

        explanation = generate_explanation(

            features,

            result["model"]

        )

        # -------------------------------------------------
        # Remove model object before returning JSON
        # -------------------------------------------------

        result.pop(
            "model",
            None
        )

        # -------------------------------------------------
        # Return complete response
        # -------------------------------------------------

        return {

            "success": True,

            "soil_health":
                result["soil_health"],

            "accuracy":
                result["accuracy"],

            "confidence":
                result["confidence"],

            "probabilities":
                result["probabilities"],

            "explanation":
                explanation

        }

    except Exception as error:

        print(
            "SOIL ANALYSIS ERROR:",
            error
        )

        raise HTTPException(

            status_code=500,

            detail=str(error)

        )