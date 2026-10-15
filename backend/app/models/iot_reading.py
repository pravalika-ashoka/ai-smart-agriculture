from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class IoTReading(Base):
    __tablename__ = "iot_readings"

    id = Column(Integer, primary_key=True, index=True)

    soil_moisture = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    rainfall = Column(Float, nullable=False)

    nitrogen = Column(Float, nullable=False)
    phosphorus = Column(Float, nullable=False)
    potassium = Column(Float, nullable=False)

    ph = Column(Float, nullable=False)

    recorded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )