from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from passlib.context import CryptContext

import os
import secrets
from dotenv import load_dotenv

from email_service import send_verification_email

load_dotenv()

# --- Check for required environment variables ---
if not os.getenv("BREVO_API_KEY"):
    raise RuntimeError("BREVO_API_KEY is not set in the environment or .env file. The application cannot start without it.")

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
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

# Create tables
Base.metadata.create_all(bind=engine)

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Schemas ---
class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str

# --- FastAPI App ---
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# --- Routes ---
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/login")
async def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified. Please check your inbox.")
    
    return {
        "message": "Login successful", 
        "token": "fake-jwt-token-for-now",
        "user": {"email": user.email, "is_pro": user.is_pro}
    }

@app.post("/register")
async def register(data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(data.password)
    verification_token = secrets.token_urlsafe(32)
    
    new_user = User(
        email=data.email, 
        hashed_password=hashed_password,
        verification_token=verification_token
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send actual email via Brevo
    send_verification_email(new_user.email, verification_token)
    
    return {"message": "User created successfully. Please check your email.", "email": new_user.email}

@app.get("/verify-email")
async def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
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
        db.execute(text('SELECT 1'))
        return {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")
