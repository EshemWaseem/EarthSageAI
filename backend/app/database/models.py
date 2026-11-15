import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    refresh_tokens = relationship("RefreshTokenModel", back_populates="user", cascade="all, delete-orphan")
    investigations = relationship("InvestigationModel", back_populates="user")

class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, index=True)  # SHA-256 hash of raw token
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("UserModel", back_populates="refresh_tokens")

class InvestigationModel(Base):
    __tablename__ = "investigations"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    research_question = Column(Text, nullable=False)
    hypothesis = Column(Text, nullable=True)
    status = Column(String(32), default="draft", nullable=False)  # draft, queued, running, completed, failed
    
    # Location
    location_name = Column(String(128), nullable=False)
    region = Column(String(128), nullable=True)
    country = Column(String(128), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Spatial extent bounding box
    spatial_extent = Column(JSON, nullable=True)
    
    # Temporal window
    start_year = Column(String(4), nullable=False)
    end_year = Column(String(4), nullable=False)
    
    # Data parameters (e.g. ['T2M', 'PRECTOTCORR'])
    parameters = Column(JSON, nullable=False, default=list)
    dataset_ids = Column(JSON, nullable=False, default=list)
    
    # Execution & results
    findings = Column(JSON, nullable=False, default=list)
    time_series_data = Column(JSON, nullable=False, default=list)
    raw_data_summary = Column(JSON, nullable=True)
    statistical_metrics = Column(JSON, nullable=True)
    report_available = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    user = relationship("UserModel", back_populates="investigations")
    reports = relationship("ReportModel", back_populates="investigation", cascade="all, delete-orphan")

class ReportModel(Base):
    __tablename__ = "reports"

    id = Column(String(64), primary_key=True, index=True)
    investigation_id = Column(String(64), ForeignKey("investigations.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(128), default="EarthSage Research Engine", nullable=False)
    file_format = Column(String(16), default="PDF", nullable=False)
    file_size = Column(String(32), default="1.2 MB", nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    investigation = relationship("InvestigationModel", back_populates="reports")

