from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.user_schema import UserCreate

from app.services.auth_service import (
    request_registration_otp,
    verify_registration_otp,
    request_login_otp,
    verify_login_otp,
    create_password_reset_otp,
    verify_password_reset_otp,
    reset_password,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ========================================
# REGISTER — REQUEST OTP
# ========================================

@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return request_registration_otp(
            db=db,
            username=user.username,
            phone_number=user.phone_number,
            password=user.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ========================================
# VERIFY REGISTRATION OTP
# ========================================

@router.post("/verify-registration-otp")
def verify_registration(
    phone_number: str,
    otp: str,
    db: Session = Depends(get_db),
):
    result = verify_registration_otp(
        db=db,
        phone_number=phone_number,
        otp=otp,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or exhausted registration OTP",
        )

    return result


# ========================================
# LOGIN — REQUEST OTP
# ========================================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # The username field contains the user's phone number.
    result = request_login_otp(
        db=db,
        phone_number=form_data.username,
        password=form_data.password,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return result


# ========================================
# VERIFY LOGIN OTP
# ========================================

@router.post("/verify-login-otp")
def verify_login(
    phone_number: str,
    otp: str,
    db: Session = Depends(get_db),
):
    result = verify_login_otp(
        db=db,
        phone_number=phone_number,
        otp=otp,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or exhausted login OTP",
        )

    return result


# ========================================
# FORGOT PASSWORD — REQUEST OTP
# ========================================

@router.post("/forgot-password")
def forgot_password(
    phone_number: str,
    db: Session = Depends(get_db),
):
    # The service queues an SMS if the phone number exists.
    # Return the same message either way to avoid revealing
    # whether a phone number is registered.
    create_password_reset_otp(
        db=db,
        phone_number=phone_number,
    )

    return {
        "message": (
            "If the phone number is registered, "
            "a password reset OTP will be sent."
        )
    }


# ========================================
# VERIFY PASSWORD RESET OTP
# ========================================

@router.post("/verify-reset-otp")
def verify_reset_otp(
    phone_number: str,
    otp: str,
    db: Session = Depends(get_db),
):
    reset_token = verify_password_reset_otp(
        db=db,
        phone_number=phone_number,
        otp=otp,
    )

    if reset_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    return {
        "message": "OTP verified successfully",
        "reset_token": reset_token,
    }


# ========================================
# RESET PASSWORD
# ========================================

@router.post("/reset-password")
def reset_user_password(
    phone_number: str,
    reset_token: str,
    new_password: str,
    db: Session = Depends(get_db),
):
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters",
        )

    if len(new_password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be longer than 72 bytes",
        )

    success = reset_password(
        db=db,
        phone_number=phone_number,
        reset_token=reset_token,
        new_password=new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset request",
        )

    return {
        "message": "Password reset successfully"
    }