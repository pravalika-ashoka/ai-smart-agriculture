from pydantic import BaseModel, Field


class SoilInput(BaseModel):

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

    moisture: float = Field(
        ...,
        ge=0,
        le=100
    )

    temperature: float = Field(
        ...,
        ge=-50,
        le=100
    )