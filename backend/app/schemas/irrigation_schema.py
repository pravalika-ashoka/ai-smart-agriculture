from typing import Optional

from pydantic import BaseModel, Field


# =========================================================
# IRRIGATION INPUT
# =========================================================

class IrrigationInput(BaseModel):

    crop_type: str

    location: str

    soil_moisture: float = Field(
        ge=0,
        le=100
    )

    humidity: float = Field(
        ge=0,
        le=100
    )

    temperature: float

    rainfall: float = Field(
        ge=0
    )

    soil_temperature: float

    wind_speed: float = Field(
        ge=0
    )

    rain_forecast: float = Field(
        ge=0,
        le=100
    )

    nitrogen: float

    phosphorus: float

    potassium: float

# =========================================================
# IRRIGATION RESPONSE
# =========================================================

class IrrigationResponse(BaseModel):

    irrigation_status: str

    water_need: str

    reason: str

    irrigation_score: float

    # -----------------------------------------------------
    # ML prediction
    # -----------------------------------------------------
    # Random Forest returns a class such as:
    #
    # "Irrigate now"
    # "Irrigate soon"
    # "Monitor"
    # "No irrigation"
    #
    # Therefore this MUST be a string, not float.
    # -----------------------------------------------------

    ml_prediction: Optional[str] = None

    model: str

    features_used: int

    advice: str

    crop_type: str

    location: str

    soil_moisture: float

    weather_temperature: Optional[float] = None

    weather_humidity: Optional[float] = None

    rainfall: float

    rain_probability: float

    notification_required: bool = False

    notification_created: bool = False