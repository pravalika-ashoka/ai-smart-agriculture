from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.iot_ai_service import get_latest_sensor_reading

router = APIRouter(
    prefix="/iot-ai",
    tags=["IoT AI Integration"]
)


@router.get("/latest")
def latest_sensor_reading(db: Session = Depends(get_db)):
    reading = get_latest_sensor_reading(db)

    if reading is None:
        raise HTTPException(
            status_code=404,
            detail="No sensor readings available"
        )

    return {
        "id": reading.id,
        "soil_moisture": reading.soil_moisture,
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "rainfall": reading.rainfall,
        "nitrogen": reading.nitrogen,
        "phosphorus": reading.phosphorus,
        "potassium": reading.potassium,
        "recorded_at": reading.recorded_at
    }