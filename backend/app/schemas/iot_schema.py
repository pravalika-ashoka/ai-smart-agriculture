from pydantic import BaseModel, Field


class IoTSensorData(BaseModel):

    soil_moisture: float = Field(
        ...,
        ge=0,
        le=100
    )

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