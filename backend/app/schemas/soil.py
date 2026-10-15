from pydantic import BaseModel


class SoilRequest(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    moisture: float
    temperature: float


class SoilResponse(BaseModel):
    soil_status: str
    confidence: float