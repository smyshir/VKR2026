from datetime import datetime
from sqlalchemy import Float, DateTime, String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class Measurement(Base):
    __tablename__ = 'measurements'
    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[str] = mapped_column(String(64), index=True)
    timestamp_utc: Mapped[datetime] = mapped_column(DateTime)
    uav_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    uav_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    bearing_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)


class Estimation(Base):
    __tablename__ = 'estimations'
    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[str] = mapped_column(String(64), index=True)
    batch_no: Mapped[int] = mapped_column(Integer)
    estimated_x: Mapped[float] = mapped_column(Float)
    estimated_y: Mapped[float] = mapped_column(Float)
    rmse: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WeaponProfile(Base):
    __tablename__ = 'weapon_profiles'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    category: Mapped[str] = mapped_column(String(64))
    min_range_km: Mapped[float] = mapped_column(Float)
    max_range_km: Mapped[float] = mapped_column(Float)
    lethal_radius_m: Mapped[float] = mapped_column(Float)
    notes: Mapped[str] = mapped_column(String(255), default='')
