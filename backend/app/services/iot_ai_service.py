from sqlalchemy.orm import Session

from app.models.iot_reading import IoTReading


def get_latest_sensor_reading(db: Session):
    """Fetch the latest sensor reading from PostgreSQL."""

    return (
        db.query(IoTReading)
        .order_by(IoTReading.id.desc())
        .first()
    )


def get_sensor_history(db: Session, limit: int = 100):
    """Fetch recent sensor readings for analysis."""

    limit = max(1, min(limit, 500))

    readings = (
        db.query(IoTReading)
        .order_by(IoTReading.id.desc())
        .limit(limit)
        .all()
    )

    return list(reversed(readings))