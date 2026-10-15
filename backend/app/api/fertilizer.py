from fastapi import APIRouter, HTTPException

from app.schemas.fertilizer_schema import FertilizerInput
from app.ml_models.fertilizer_model import predict_fertilizer
from app.services.dataset_service import load_fertilizer_data


router = APIRouter(
    prefix="/fertilizer",
    tags=["Fertilizer"]
)


@router.post("/recommend")
def fertilizer_recommendation(data: FertilizerInput):
    try:
        # Prepare model input: five numeric features, no pH.
        features = [
            float(data.nitrogen),
            float(data.phosphorus),
            float(data.potassium),
            float(data.moisture),
            float(data.temperature),
        ]

        # Validate numeric values.
        for value in features:
            if not isinstance(value, (int, float)):
                raise ValueError(
                    "Fertilizer input must contain numeric values."
                )

        # Validate crop type.
        crop_type = str(data.crop_type).strip().lower()

        if not crop_type:
            raise ValueError(
                "Crop type is required for fertilizer recommendation."
            )

        # Debug log.
        print(
            "Fertilizer model input:",
            {
                "nitrogen": features[0],
                "phosphorus": features[1],
                "potassium": features[2],
                "moisture": features[3],
                "temperature": features[4],
                "crop_type": crop_type,
            },
        )

        # Model prediction.
        result = predict_fertilizer(features)

        fertilizer = result.get("fertilizer")
        accuracy = result.get("accuracy", 0)

        if not fertilizer:
            raise ValueError(
                "The fertilizer model did not return "
                "a fertilizer recommendation."
            )

        # Retrieve fertilizer advice.
        advice = ""

        try:
            dataset = load_fertilizer_data()

            if (
                "recommended_fertilizer" in dataset.columns
                and "advice" in dataset.columns
            ):
                matching_rows = dataset[
                    dataset["recommended_fertilizer"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    == str(fertilizer).strip().lower()
                ]

                # Prefer crop-specific advice when available.
                if "crop_type" in dataset.columns:
                    crop_rows = matching_rows[
                        matching_rows["crop_type"]
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        == crop_type
                    ]

                    if not crop_rows.empty:
                        matching_rows = crop_rows

                if not matching_rows.empty:
                    advice_value = matching_rows["advice"].iloc[0]

                    if (
                        advice_value is not None
                        and str(advice_value).strip()
                    ):
                        advice = str(advice_value).strip()

        except Exception as advice_error:
            print(
                "Fertilizer advice lookup warning:",
                advice_error,
            )

        # Default advice.
        if not advice:
            advice = (
                f"Use {fertilizer} according to the requirements "
                f"of {crop_type} and the current soil condition. "
                "Avoid excessive fertilizer application."
            )

        return {
            "status": "success",
            "recommended_fertilizer": str(fertilizer),
            "accuracy": round(float(accuracy), 2),
            "crop_type": crop_type,
            "advice": advice,
        }

    except ValueError as error:
        print("Fertilizer validation/model error:", error)

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        print("Fertilizer recommendation error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to generate fertilizer recommendation.",
        )