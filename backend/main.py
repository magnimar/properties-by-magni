from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone

import os
import secrets
from dotenv import load_dotenv

from email_service import send_verification_email, send_password_reset_email
from sqlalchemy import inspect

load_dotenv("/opt/properties-by-magni/.env")

# --- JWT Config ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- Check for required environment variables ---
if not os.getenv("BREVO_API_KEY"):
    raise RuntimeError(
        "BREVO_API_KEY is not set in the environment or .env file. The application cannot start without it."
    )

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL")

# --- SQLAlchemy Setup ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Models ---
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_pro = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True, index=True)
    reset_token = Column(String, nullable=True, index=True)
    reset_token_expires = Column(DateTime, nullable=True)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    min_bedrooms = Column(Integer, nullable=True)
    max_bedrooms = Column(Integer, nullable=True)
    zip_codes = Column(String, nullable=True)  # Comma separated list
    ignored_streets = Column(String, nullable=True)  # Comma separated list
    einbylishus = Column(Boolean, default=False)
    fjolbylishus = Column(Boolean, default=False)
    atvinnuhusnaedi = Column(Boolean, default=False)
    radhus_parhus = Column(Boolean, default=False)
    sumarhus = Column(Boolean, default=False)
    parhus = Column(Boolean, default=False)
    jord_lod = Column(Boolean, default=False)
    haed = Column(Boolean, default=False)
    hesthus = Column(Boolean, default=False)
    oflokkad = Column(Boolean, default=False)
    outdoor_filter = Column(String, default="none")
    want_garage = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


# Create tables
Base.metadata.create_all(bind=engine)

# --- Quick & Dirty Schema Migration ---

inspector = inspect(engine)
existing_columns = [c["name"] for c in inspector.get_columns("users")]
with engine.begin() as conn:
    if "reset_token" not in existing_columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN reset_token TEXT;"))
    if "reset_token_expires" not in existing_columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN reset_token_expires DATETIME;"))
    if "min_price" not in existing_columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN min_price FLOAT;"))
    if "max_price" not in existing_columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN max_price FLOAT;"))
    if "min_bedrooms" not in existing_columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN min_bedrooms INTEGER;"))
    if "max_bedrooms" not in existing_columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN max_bedrooms INTEGER;"))
    if "zip_codes" not in existing_columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN zip_codes TEXT;"))
    if "ignored_streets" not in existing_columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN ignored_streets TEXT;"))
    if "einbylishus" not in existing_columns:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN einbylishus BOOLEAN DEFAULT FALSE;")
        )
    if "fjolbylishus" not in existing_columns:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN fjolbylishus BOOLEAN DEFAULT FALSE;")
        )
    if "atvinnuhusnaedi" not in existing_columns:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN atvinnuhusnaedi BOOLEAN DEFAULT FALSE;")
        )
    if "radhus_parhus" not in existing_columns:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN radhus_parhus BOOLEAN DEFAULT FALSE;")
        )
    if "sumarhus" not in existing_columns:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN sumarhus BOOLEAN DEFAULT FALSE;")
        )
    if "parhus" not in existing_columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN parhus BOOLEAN DEFAULT FALSE;"))
    if "jord_lod" not in existing_columns:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN jord_lod BOOLEAN DEFAULT FALSE;")
        )
    if "haed" not in existing_columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN haed BOOLEAN DEFAULT FALSE;"))
    if "hesthus" not in existing_columns:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN hesthus BOOLEAN DEFAULT FALSE;")
        )
    if "oflokkad" not in existing_columns:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN oflokkad BOOLEAN DEFAULT FALSE;")
        )
    if "outdoor_filter" not in existing_columns:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN outdoor_filter TEXT DEFAULT 'none';")
        )
    if "want_garage" not in existing_columns:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN want_garage BOOLEAN DEFAULT FALSE;")
        )

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Schemas ---
class UserLogin(BaseModel):
    email: str
    password: str


class ForgotPassword(BaseModel):
    email: str


class ResetPassword(BaseModel):
    token: str
    new_password: str


class UserCreate(BaseModel):
    email: str
    password: str


class UserPreferences(BaseModel):
    min_price: float | None = None
    max_price: float | None = None
    min_bedrooms: int | None = None
    max_bedrooms: int | None = None
    zip_codes: list[str] | None = None
    ignored_streets: list[str] | None = None
    einbylishus: bool = False
    fjolbylishus: bool = False
    atvinnuhusnaedi: bool = False
    radhus_parhus: bool = False
    sumarhus: bool = False
    parhus: bool = False
    jord_lod: bool = False
    haed: bool = False
    hesthus: bool = False
    oflokkad: bool = False
    outdoor_filter: str = "none"
    want_garage: bool = False


# --- FastAPI App ---
app = FastAPI()

# CORS configuration
origins = [
    "https://propertiesbymagni.com",
    "https://www.propertiesbymagni.com",
    "https://api.propertiesbymagni.com",
    "http://localhost:5000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# --- Routes ---
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "is_pro": current_user.is_pro,
        "min_price": current_user.min_price,
        "max_price": current_user.max_price,
        "min_bedrooms": current_user.min_bedrooms,
        "max_bedrooms": current_user.max_bedrooms,
        "zip_codes": (
            current_user.zip_codes.split(",") if current_user.zip_codes else []
        ),
        "ignored_streets": (
            current_user.ignored_streets.split(",")
            if current_user.ignored_streets
            else []
        ),
        "einbylishus": current_user.einbylishus,
        "fjolbylishus": current_user.fjolbylishus,
        "atvinnuhusnaedi": current_user.atvinnuhusnaedi,
        "radhus_parhus": current_user.radhus_parhus,
        "sumarhus": current_user.sumarhus,
        "parhus": current_user.parhus,
        "jord_lod": current_user.jord_lod,
        "haed": current_user.haed,
        "hesthus": current_user.hesthus,
        "oflokkad": current_user.oflokkad,
        "outdoor_filter": current_user.outdoor_filter,
        "want_garage": current_user.want_garage,
    }


@app.post("/me/preferences")
async def update_my_preferences(
    prefs: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.min_price = prefs.min_price
    current_user.max_price = prefs.max_price
    current_user.min_bedrooms = prefs.min_bedrooms
    current_user.max_bedrooms = prefs.max_bedrooms
    current_user.einbylishus = prefs.einbylishus
    current_user.fjolbylishus = prefs.fjolbylishus
    current_user.atvinnuhusnaedi = prefs.atvinnuhusnaedi
    current_user.radhus_parhus = prefs.radhus_parhus
    current_user.sumarhus = prefs.sumarhus
    current_user.parhus = prefs.parhus
    current_user.jord_lod = prefs.jord_lod
    current_user.haed = prefs.haed
    current_user.hesthus = prefs.hesthus
    current_user.oflokkad = prefs.oflokkad
    current_user.outdoor_filter = prefs.outdoor_filter
    current_user.want_garage = prefs.want_garage
    if prefs.zip_codes is not None:
        current_user.zip_codes = ",".join(prefs.zip_codes)
    if prefs.ignored_streets is not None:
        current_user.ignored_streets = ",".join(prefs.ignored_streets)
    db.commit()
    return {"message": "Preferences updated successfully"}


@app.post("/login")
async def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_verified:
        raise HTTPException(
            status_code=400, detail="Email not verified. Please check your inbox."
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {
        "message": "Login successful",
        "token": access_token,
        "user": {"email": user.email, "is_pro": user.is_pro},
    }


@app.post("/forgot-password")
async def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if user:
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()
        send_password_reset_email(user.email, reset_token)

    # Always return a success message for security to avoid email enumeration
    return {"message": "If your email is registered, you will receive a reset link."}


@app.post("/reset-password")
async def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.reset_token == data.token)
        .filter(User.reset_token_expires > datetime.now(timezone.utc))
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.hashed_password = pwd_context.hash(data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {"message": "Password reset successfully"}


@app.post("/register")
async def register(data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()

    hashed_password = pwd_context.hash(data.password)
    verification_token = secrets.token_urlsafe(32)

    if existing_user:
        if existing_user.is_verified:
            raise HTTPException(
                status_code=400, detail="Email already registered and verified"
            )
        else:
            # Update the existing unverified user with new password and new token
            existing_user.hashed_password = hashed_password
            existing_user.verification_token = verification_token
            db.commit()
            db.refresh(existing_user)
            send_verification_email(existing_user.email, verification_token)
            return {
                "message": "Verification email resent. Please check your email.",
                "email": existing_user.email,
            }

    new_user = User(
        email=data.email,
        hashed_password=hashed_password,
        verification_token=verification_token,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send actual email via Brevo
    send_verification_email(new_user.email, verification_token)

    return {
        "message": "User created successfully. Please check your email.",
        "email": new_user.email,
    }


@app.get("/verify-email")
async def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token"
        )

    user.is_verified = True
    user.verification_token = None
    db.commit()

    return {"message": "Email verified successfully"}


@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.post("/items/")
def create_item(name: str, description: str, db: Session = Depends(get_db)):
    db_item = Item(name=name, description=description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")
