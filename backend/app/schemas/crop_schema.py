from pydantic import BaseModel, Field


class CropInput(BaseModel):
    """
    Input data used for crop recommendation.

    These fields match the Kaggle crop dataset:

        nitrogen
        phosphorus
        potassium
        temperature
        humidity
        rainfall
    """

    nitrogen: float = Field(..., ge=0)

    phosphorus: float = Field(..., ge=0)

    potassium: float = Field(..., ge=0)

    temperature: float

    humidity: float = Field(
        ...,
        ge=0,
        le=100
    )

    rainfall: float = Field(
        ...,
        ge=0
    )