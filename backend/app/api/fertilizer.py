from fastapi import APIRouter, HTTPException

from app.schemas.fertilizer_schema import FertilizerInput

from app.ml_models.fertilizer_model import (
    predict_fertilizer
)

from app.services.dataset_service import (
    load_fertilizer_data
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/fertilizer",
    tags=["Fertilizer"]
)


# =========================================================
# FERTILIZER RECOMMENDATION
# =========================================================

@router.post("/recommend")
def fertilizer_recommendation(
    data: FertilizerInput
):

    try:

        # -------------------------------------------------
        # PREPARE NUMERIC MODEL INPUT
        # -------------------------------------------------
        #
        # IMPORTANT:
        # The fertilizer model was trained using ONLY
        # these 6 numeric features.
        #
        # crop_type is NOT passed to the ML model.
        # It is used later for crop-specific advice.
        #
        # -------------------------------------------------

        features = [

            float(data.nitrogen),

            float(data.phosphorus),

            float(data.potassium),

            float(data.moisture),

            float(data.temperature)

        ]


        # -------------------------------------------------
        # VALIDATE NUMERIC VALUES
        # -------------------------------------------------

        for value in features:

            if not isinstance(value, (int, float)):

                raise ValueError(
                    "Fertilizer input must contain numeric values."
                )


        # -------------------------------------------------
        # VALIDATE CROP TYPE
        # -------------------------------------------------

        crop_type = str(
            data.crop_type
        ).strip().lower()


        if not crop_type:

            raise ValueError(
                "Crop type is required for fertilizer recommendation."
            )


        # -------------------------------------------------
        # DEBUG LOG
        # -------------------------------------------------

        print(
            "Fertilizer model input:",
            {
                "nitrogen": features[0],
                "phosphorus": features[1],
                "potassium": features[2],
                "moisture": features[4],
                "temperature": features[5],
                "crop_type": crop_type
            }
        )


        # -------------------------------------------------
        # MODEL PREDICTION
        # -------------------------------------------------

        result = predict_fertilizer(
            features
        )


        # -------------------------------------------------
        # GET RECOMMENDED FERTILIZER
        # -------------------------------------------------

        fertilizer = result.get(
            "fertilizer"
        )

        accuracy = result.get(
            "accuracy",
            0
        )


        if not fertilizer:

            raise ValueError(
                "The fertilizer model did not return "
                "a fertilizer recommendation."
            )


        # -------------------------------------------------
        # GET ADVICE FROM DATASET
        # -------------------------------------------------

        advice = ""


        try:

            dataset = load_fertilizer_data()


            if (
                "recommended_fertilizer"
                in dataset.columns
                and
                "advice"
                in dataset.columns
            ):

                # -----------------------------------------
                # FIND FERTILIZER MATCHES
                # -----------------------------------------

                matching_rows = dataset[
                    dataset[
                        "recommended_fertilizer"
                    ]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    ==
                    str(fertilizer)
                    .strip()
                    .lower()
                ]


                # -----------------------------------------
                # PREFER CROP-SPECIFIC ADVICE
                # -----------------------------------------

                if (
                    "crop_type"
                    in dataset.columns
                ):

                    crop_rows = matching_rows[
                        matching_rows[
                            "crop_type"
                        ]
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        ==
                        crop_type
                    ]


                    if not crop_rows.empty:

                        matching_rows = crop_rows


                # -----------------------------------------
                # GET FIRST AVAILABLE ADVICE
                # -----------------------------------------

                if not matching_rows.empty:

                    advice_value = matching_rows[
                        "advice"
                    ].iloc[0]


                    if (
                        advice_value is not None
                        and
                        str(
                            advice_value
                        ).strip()
                    ):

                        advice = str(
                            advice_value
                        ).strip()


        except Exception as advice_error:

            print(
                "Fertilizer advice lookup warning:",
                advice_error
            )


        # -------------------------------------------------
        # DEFAULT ADVICE
        # -------------------------------------------------

        if not advice:

            advice = (
                f"Use {fertilizer} according to "
                f"the requirements of {crop_type} "
                "and the current soil condition. "
                "Avoid excessive fertilizer application."
            )


        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------

        return {

            "status": "success",

            "recommended_fertilizer":
                str(fertilizer),

            "accuracy":
                round(
                    float(accuracy),
                    2
                ),

            "crop_type":
                crop_type,

            "advice":
                advice

        }


    # =====================================================
    # VALID INPUT / MODEL ERROR
    # =====================================================

    except ValueError as error:

        print(
            "Fertilizer validation/model error:",
            error
        )

        raise HTTPException(

            status_code=400,

            detail=str(error)

        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as error:

        print(
            "Fertilizer recommendation error:",
            error
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Unable to generate fertilizer "
                "recommendation."
            )

        )