# =========================================================
# RESOURCE / THREAD LIMITS
# =========================================================

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("TORCH_NUM_THREADS", "1")


# =========================================================
# FASTAPI IMPORTS
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# =========================================================
# DATABASE
# =========================================================

from app.database.database import (
    Base,
    engine
)


# =========================================================
# DATABASE MODELS
# =========================================================

from app.models.user import User
from app.models.prediction import Prediction
from app.models.notification import Notification
from app.models.sms_relay_device import SmsRelayDevice
from app.models.sms_message import SmsMessage
from app.models.iot_reading import IoTReading

# Password reset model
from app.models.password_reset import PasswordReset
from app.models.auth_otp import AuthOTP

# =========================================================
# API ROUTERS
# =========================================================

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.dashboard import router as dashboard_router
from app.api.soil import router as soil_router
from app.api.crop import router as crop_router
from app.api.fertilizer import router as fertilizer_router
from app.api.irrigation import router as irrigation_router
from app.api.weather import router as weather_router
from app.api.prediction import router as prediction_router
from app.api.iot import router as iot_router
from app.api.notifications import router as notifications_router
from app.api.assistant import router as assistant_router
from app.api.tts import router as tts_router
from app.api.yield_prediction import router as yield_router
from app.api.market import router as market_router
from app.api.disease import router as disease_router
from app.api.sms_relay import router as sms_relay_router
from app.api import iot_export

# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI Smart Agriculture API",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",

        # Production Vercel
        "https://ai-smart-agriculture-ten.vercel.app",
        "https://aismartagriculture-b5b1g1jot-pravalikaappu2936.vercel.app",
    ],

    # Allow Vercel deployment URLs belonging to your project
    allow_origin_regex=r"https://[a-z0-9-]+-pravalikaappu2936\.vercel\.app",

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(dashboard_router)
app.include_router(soil_router)
app.include_router(crop_router)
app.include_router(fertilizer_router)
app.include_router(irrigation_router)
app.include_router(weather_router)
app.include_router(prediction_router)
app.include_router(iot_router)
app.include_router(notifications_router)
app.include_router(assistant_router)
app.include_router(tts_router)
app.include_router(yield_router)
app.include_router(market_router)
app.include_router(disease_router)
app.include_router(sms_relay_router)
app.include_router(iot_export.router)
# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "AI Smart Agriculture Backend Running"
    }