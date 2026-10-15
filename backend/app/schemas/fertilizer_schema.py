from pydantic import BaseModel, Field


class FertilizerInput(BaseModel):

    # =====================================================
    # SOIL NUTRIENTS
    # =====================================================

    nitrogen: float = Field(
        ...,
        ge=0
    )

    phosphorus: float = Field(
        ...,
        ge=0
    )

    potassium: float = Field(
        ...,
        ge=0
    )

    # =====================================================
    # SOIL MOISTURE
    # =====================================================

    moisture: float = Field(
        ...,
        ge=0,
        le=100
    )


    # =====================================================
    # TEMPERATURE
    # =====================================================

    temperature: float = Field(
        ...,
        ge=-50,
        le=80
    )


    # =====================================================
    # CROP TYPE
    # =====================================================

    crop_type: str = Field(
        ...,
        min_length=2,
        max_length=50
    )