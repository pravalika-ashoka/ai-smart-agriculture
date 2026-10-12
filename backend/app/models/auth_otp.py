from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class AuthOTP(Base):
    __tablename__ = "auth_otps"

    id = Column(Integer, primary_key=True, index=True)

    phone_number = Column(
        String,
        nullable=False,
        index=True
    )

    purpose = Column(
        String,
        nullable=False,
        index=True
    )

    otp_hash = Column(
        String,
        nullable=False
    )

    # Store pending registration details until verification.
    username = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)

    expires_at = Column(
        DateTime,
        nullable=False
    )

    attempts = Column(
        Integer,
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )