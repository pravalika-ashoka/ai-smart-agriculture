from pydantic import BaseModel


class CropRequest(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    temperature: float
    humidity: float
    rainfall: float


class CropResponse(BaseModel):
    recommended_crop: str
    confidence: float