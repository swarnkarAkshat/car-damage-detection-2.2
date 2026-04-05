from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime
from sqlalchemy.dialects.mysql import LONGTEXT

# ==========================================
# SQLAlchemy Models — matched to REAL MySQL schema
# ==========================================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    predictions = relationship("Prediction", back_populates="owner")
    history = relationship("History", back_populates="owner")


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    input = Column(String(255), nullable=True)              # image filename
    damage_percentage = Column(Integer, nullable=True)      # confidence as int %
    cost = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    prediction_result = Column(String(100), nullable=True)
    explanation = Column(String(1000), nullable=True)
    report_path = Column(String(255), nullable=True)
    recommendations = Column(String(1000), nullable=True)

    owner = relationship("User", back_populates="predictions")


class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    prediction = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    damage_percentage = Column(Integer, nullable=True) # Actual damage % calculated by costCalculator
    cost = Column(Float, nullable=True) # Calculated repair cost
    explanation = Column(String(5000), nullable=True)
    image_data = Column(LONGTEXT, nullable=True) # Store original image as base64
    report_path = Column(String(255), nullable=True) # Added report path
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="history")
