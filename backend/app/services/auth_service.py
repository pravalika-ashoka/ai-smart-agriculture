from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import hmac

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.password_reset import PasswordReset
from app.models.auth_otp import AuthOTP
from app.models.sms_message import SmsMessage

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


# ============================================================
# CONSTANTS
# ============================================================

OTP_EXPIRY_MINUTES = 5
OTP_MAX_ATTEMPTS = 5
RESET_OTP_EXPIRY_MINUTES = 10
RESET_TOKEN_EXPIRY_MINUTES = 10


# ============================================================
# OTP HELPERS
# ============================================================

def generate_otp() -> str:
    """Generate a cryptographically secure six-digit OTP."""
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    """Hash an OTP before storing it."""
    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()


def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


def is_expired(expiry: datetime) -> bool:
    """Check expiry safely for timezone-aware or naive DB values."""
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    return utc_now() > expiry


# ============================================================
# SMS QUEUE
# ============================================================

def queue_sms(
    db: Session,
    phone_number: str,
    message: str,
    device_id: int | None = None
) -> SmsMessage:
    """
    Add an SMS to the existing Android relay queue.

    device_id=None allows an active relay device to retrieve
    the message using the existing /sms-relay/poll endpoint.
    """

    sms = SmsMessage(
        device_id=device_id,
        phone_number=phone_number,
        message=message,
        status="pending",
        attempts=0
    )

    db.add(sms)
    db.flush()

    return sms


def queue_auth_otp_sms(
    db: Session,
    phone_number: str,
    otp: str,
    purpose: str
) -> SmsMessage:
    """Queue a registration or login OTP SMS."""

    messages = {
        "register": (
            f"Your AI Smart Agriculture registration OTP is {otp}. "
            f"It expires in {OTP_EXPIRY_MINUTES} minutes. "
            "Do not share it."
        ),
        "login": (
            f"Your AI Smart Agriculture login OTP is {otp}. "
            f"It expires in {OTP_EXPIRY_MINUTES} minutes. "
            "Do not share it."
        )
    }

    if purpose not in messages:
        raise ValueError("Unsupported OTP purpose")

    return queue_sms(
        db=db,
        phone_number=phone_number,
        message=messages[purpose]
    )


# ============================================================
# USER REGISTRATION — STEP 1: REQUEST OTP
# ============================================================

def request_registration_otp(
    db: Session,
    username: str,
    phone_number: str,
    password: str
):
    """
    Validate registration details and queue an OTP.

    The user account is not created until the OTP is verified.
    """

    existing_username = db.query(User).filter(
        User.username == username
    ).first()

    if existing_username:
        raise ValueError("Username already registered")

    existing_phone = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if existing_phone:
        raise ValueError("Phone number already registered")

    if not username.strip():
        raise ValueError("Username is required")

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password cannot be longer than 72 bytes")

    otp = generate_otp()

    # Remove previous pending registration challenges
    db.query(AuthOTP).filter(
        AuthOTP.phone_number == phone_number,
        AuthOTP.purpose == "register"
    ).delete(synchronize_session=False)

    challenge = AuthOTP(
        phone_number=phone_number,
        purpose="register",
        otp_hash=hash_otp(otp),
        username=username,
        password_hash=hash_password(password),
        expires_at=utc_now() + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        ),
        attempts=0
    )

    db.add(challenge)

    queue_auth_otp_sms(
        db=db,
        phone_number=phone_number,
        otp=otp,
        purpose="register"
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Registration OTP queued successfully",
        "phone_number": phone_number
    }


# ============================================================
# USER REGISTRATION — STEP 2: VERIFY OTP
# ============================================================

def verify_registration_otp(
    db: Session,
    phone_number: str,
    otp: str
):
    """Verify registration OTP and create the account."""

    challenge = db.query(AuthOTP).filter(
        AuthOTP.phone_number == phone_number,
        AuthOTP.purpose == "register"
    ).first()

    if challenge is None:
        return None

    if challenge.attempts >= OTP_MAX_ATTEMPTS:
        db.delete(challenge)
        db.commit()
        return None

    challenge.attempts += 1

    if is_expired(challenge.expires_at):
        db.delete(challenge)
        db.commit()
        return None

    if not hmac.compare_digest(
        challenge.otp_hash,
        hash_otp(otp)
    ):
        db.commit()
        return None

    # Recheck uniqueness in case another registration occurred
    existing_username = db.query(User).filter(
        User.username == challenge.username
    ).first()

    existing_phone = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if existing_username or existing_phone:
        db.delete(challenge)
        db.commit()
        return None

    user = User(
        username=challenge.username,
        phone_number=challenge.phone_number,
        password=challenge.password_hash
    )

    db.add(user)
    db.delete(challenge)

    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Phone number verified and registration successful",
        "username": user.username,
        "phone_number": user.phone_number
    }


# ============================================================
# AUTHENTICATE USER
# ============================================================

def authenticate_user(
    db: Session,
    phone_number: str,
    password: str
):
    """Validate the user's phone number and password."""

    user = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if user is None:
        return None

    if not verify_password(password, user.password):
        return None

    return user


# ============================================================
# LOGIN — STEP 1: VERIFY PASSWORD AND REQUEST OTP
# ============================================================

def request_login_otp(
    db: Session,
    phone_number: str,
    password: str
):
    """
    Verify the password and queue a login OTP.

    No JWT is issued at this stage.
    """

    user = authenticate_user(
        db,
        phone_number,
        password
    )

    if user is None:
        return None

    otp = generate_otp()

    db.query(AuthOTP).filter(
        AuthOTP.phone_number == phone_number,
        AuthOTP.purpose == "login"
    ).delete(synchronize_session=False)

    challenge = AuthOTP(
        phone_number=phone_number,
        purpose="login",
        otp_hash=hash_otp(otp),
        username=None,
        password_hash=None,
        expires_at=utc_now() + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        ),
        attempts=0
    )

    db.add(challenge)

    queue_auth_otp_sms(
        db=db,
        phone_number=phone_number,
        otp=otp,
        purpose="login"
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Login OTP queued successfully",
        "phone_number": phone_number
    }


# ============================================================
# LOGIN — STEP 2: VERIFY OTP AND ISSUE JWT
# ============================================================

def verify_login_otp(
    db: Session,
    phone_number: str,
    otp: str
):
    """Verify login OTP and issue the JWT only after verification."""

    challenge = db.query(AuthOTP).filter(
        AuthOTP.phone_number == phone_number,
        AuthOTP.purpose == "login"
    ).first()

    if challenge is None:
        return None

    if challenge.attempts >= OTP_MAX_ATTEMPTS:
        db.delete(challenge)
        db.commit()
        return None

    challenge.attempts += 1

    if is_expired(challenge.expires_at):
        db.delete(challenge)
        db.commit()
        return None

    if not hmac.compare_digest(
        challenge.otp_hash,
        hash_otp(otp)
    ):
        db.commit()
        return None

    user = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if user is None:
        db.delete(challenge)
        db.commit()
        return None

    access_token = create_access_token(
        data={
            "sub": str(user.phone_number)
        }
    )

    # Make the OTP single-use
    db.delete(challenge)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================
# LEGACY LOGIN SERVICE
# ============================================================

def login_user(
    db: Session,
    phone_number: str,
    password: str
):
    """
    Legacy password-only login.

    Do not expose this function through a public login endpoint
    if login OTP verification is required.
    """

    user = authenticate_user(
        db,
        phone_number,
        password
    )

    if user is None:
        return None

    access_token = create_access_token(
        data={
            "sub": str(user.phone_number)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================
# LEGACY REGISTRATION SERVICE
# ============================================================

def register_user(
    db: Session,
    username: str,
    phone_number: str,
    password: str
):
    """
    Legacy direct registration.

    The public registration endpoint should use
    request_registration_otp() and verify_registration_otp().
    """

    existing_username = db.query(User).filter(
        User.username == username
    ).first()

    if existing_username:
        raise ValueError("Username already registered")

    existing_phone = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if existing_phone:
        raise ValueError("Phone number already registered")

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password cannot be longer than 72 bytes")

    user = User(
        username=username,
        phone_number=phone_number,
        password=hash_password(password)
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise

    return user


# ============================================================
# CREATE PASSWORD RESET OTP
# ============================================================

def create_password_reset_otp(
    db: Session,
    phone_number: str
):
    """
    Create a password-reset OTP and queue it through the SMS relay.

    Returns True when the request is queued.
    Does not return the OTP to the API caller.
    """

    user = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if user is None:
        return None

    otp = generate_otp()

    db.query(PasswordReset).filter(
        PasswordReset.phone_number == phone_number
    ).delete(synchronize_session=False)

    reset = PasswordReset(
        phone_number=phone_number,
        otp_hash=hash_otp(otp),
        expires_at=utc_now() + timedelta(
            minutes=RESET_OTP_EXPIRY_MINUTES
        ),
        attempts=0,
        reset_token_hash=None,
        token_expires_at=None
    )

    db.add(reset)

    queue_sms(
        db=db,
        phone_number=phone_number,
        message=(
            f"Your AI Smart Agriculture password reset OTP is {otp}. "
            f"It expires in {RESET_OTP_EXPIRY_MINUTES} minutes. "
            "Do not share it."
        )
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return True


# ============================================================
# VERIFY PASSWORD RESET OTP
# ============================================================

def verify_password_reset_otp(
    db: Session,
    phone_number: str,
    otp: str
):
    """Verify reset OTP and issue a short-lived reset token."""

    reset = db.query(PasswordReset).filter(
        PasswordReset.phone_number == phone_number
    ).first()

    if reset is None:
        return None

    if reset.attempts >= OTP_MAX_ATTEMPTS:
        db.delete(reset)
        db.commit()
        return None

    reset.attempts += 1

    if is_expired(reset.expires_at):
        db.commit()
        return None

    if not hmac.compare_digest(
        reset.otp_hash,
        hash_otp(otp)
    ):
        db.commit()
        return None

    reset_token = secrets.token_urlsafe(32)

    reset.reset_token_hash = hashlib.sha256(
        reset_token.encode("utf-8")
    ).hexdigest()

    reset.token_expires_at = utc_now() + timedelta(
        minutes=RESET_TOKEN_EXPIRY_MINUTES
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return reset_token


# ============================================================
# RESET PASSWORD
# ============================================================

def reset_password(
    db: Session,
    phone_number: str,
    reset_token: str,
    new_password: str
):
    """Reset a password using a verified, unexpired reset token."""

    if len(new_password) < 6:
        return False

    if len(new_password.encode("utf-8")) > 72:
        return False

    reset = db.query(PasswordReset).filter(
        PasswordReset.phone_number == phone_number
    ).first()

    if reset is None:
        return False

    if reset.reset_token_hash is None:
        return False

    if reset.token_expires_at is None:
        return False

    if is_expired(reset.token_expires_at):
        db.delete(reset)
        db.commit()
        return False

    supplied_hash = hashlib.sha256(
        reset_token.encode("utf-8")
    ).hexdigest()

    if not hmac.compare_digest(
        supplied_hash,
        reset.reset_token_hash
    ):
        return False

    user = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if user is None:
        return False

    user.password = hash_password(new_password)

    db.delete(reset)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return True