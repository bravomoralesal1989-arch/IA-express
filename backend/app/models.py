from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False)  # e.g., Restaurante, Bodega, Hotel
    town = Column(String(100), nullable=False)      # e.g., Bormujos, Villanueva del Ariscal
    province = Column(String(100), default="Sevilla")
    address = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    website = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    specialties = Column(Text, nullable=True)        # e.g., Carnes a la brasa, guisos caseros, catas
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    contents = relationship("GeneratedContent", back_populates="business", cascade="all, delete-orphan")
    index_jobs = relationship("IndexJob", back_populates="business", cascade="all, delete-orphan")


class GeneratedContent(Base):
    __tablename__ = "generated_contents"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content_html = Column(Text, nullable=False)
    schema_jsonld = Column(Text, nullable=False)    # Raw JSON String of Schema.org LocalBusiness/Restaurant
    published_path = Column(String(255), nullable=False)
    published_url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    business = relationship("Business", back_populates="contents")


class IndexJob(Base):
    __tablename__ = "index_jobs"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    target_url = Column(String(255), nullable=False)
    indexnow_status = Column(String(50), default="pending")  # success, error, pending
    http_status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    business = relationship("Business", back_populates="index_jobs")
