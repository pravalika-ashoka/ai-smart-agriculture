from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.iot_reading import IoTReading
from app.schemas.iot_schema import IoTSensorData


router = APIRouter(
    prefix="/iot",
    tags=["IoT Sensors"]
)


# =========================================================
# LATEST SENSOR DATA
# =========================================================

latest_sensor_data = {
    "soil_moisture": 42.5,
    "temperature": 28.4,
    "humidity": 65.0,
    "rainfall": 12.0,
    "nitrogen": 80.0,
    "phosphorus": 45.0,
    "potassium": 50.0,
    "ph": 6.5
}


# =========================================================
# SENSOR STATUS
# =========================================================

@router.get("/status")
def iot_status():
    return {
        "message": "IoT Sensor Module Ready",
        "status": "connected"
    }


# =========================================================
# GET LATEST SENSOR DATA
# =========================================================

@router.get("/latest")
def get_latest_sensor_data(db: Session = Depends(get_db)):

    reading = (
        db.query(IoTReading)
        .order_by(IoTReading.id.desc())
        .first()
    )

    if reading is not None:
        data = {
            "soil_moisture": reading.soil_moisture,
            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "rainfall": reading.rainfall,
            "nitrogen": reading.nitrogen,
            "phosphorus": reading.phosphorus,
            "potassium": reading.potassium,
            "ph": reading.ph
        }
    else:
        data = latest_sensor_data

    return {
        "status": "success",
        "data": data
    }


# =========================================================
# UPDATE AND SAVE SENSOR DATA
# =========================================================

@router.post("/update")
def update_sensor_data(
    data: IoTSensorData,
    db: Session = Depends(get_db)
):

    global latest_sensor_data

    latest_sensor_data = data.model_dump()

    reading = IoTReading(**latest_sensor_data)

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return {
        "status": "success",
        "message": "Sensor data saved successfully",
        "data": latest_sensor_data,
        "reading_id": reading.id,
        "recorded_at": reading.recorded_at
    }


# =========================================================
# GET SENSOR HISTORY
# =========================================================

@router.get("/history")
def get_sensor_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    limit = max(1, min(limit, 500))

    readings = (
        db.query(IoTReading)
        .order_by(IoTReading.id.desc())
        .limit(limit)
        .all()
    )

    return {
        "status": "success",
        "count": len(readings),
        "data": [
            {
                "id": r.id,
                "soil_moisture": r.soil_moisture,
                "temperature": r.temperature,
                "humidity": r.humidity,
                "rainfall": r.rainfall,
                "nitrogen": r.nitrogen,
                "phosphorus": r.phosphorus,
                "potassium": r.potassium,
                "ph": r.ph,
                "recorded_at": r.recorded_at
            }
            for r in readings
        ]
    }