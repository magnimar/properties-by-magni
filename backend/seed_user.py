import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv("/opt/properties-by-magni/.env")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_pro = Column(Boolean, default=False)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_user():
    db = SessionLocal()
    email = "test@example.com"
    password = "password123"

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"User {email} already exists.")
        return

    hashed_password = pwd_context.hash(password)
    new_user = User(email=email, hashed_password=hashed_password, is_pro=True)
    db.add(new_user)
    db.commit()
    print(f"User {email} created with password: {password}")
    db.close()


if __name__ == "__main__":
    seed_user()
