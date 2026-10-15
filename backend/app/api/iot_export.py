import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.iot_reading import IoTReading

router = APIRouter(
    prefix="/iot",
    tags=["IoT Data Export"]
)


@router.get("/export")
def export_iot_data(db: Session = Depends(get_db)):
    readings = (
        db.query(IoTReading)
        .order_by(IoTReading.id.asc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id",
        "soil_moisture",
        "temperature",
        "humidity",
        "rainfall",
        "nitrogen",
        "phosphorus",
        "potassium",
        "recorded_at"
    ])

    for row in readings:
        writer.writerow([
            row.id,
            row.soil_moisture,
            row.temperature,
            row.humidity,
            row.rainfall,
            row.nitrogen,
            row.phosphorus,
            row.potassium,
            row.recorded_at
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                'attachment; filename="iot_sensor_data.csv"'
        }
    )