"""SQLAlchemy models for AI-IMUTIS backend."""
from datetime import datetime
from typing import List, Optional
import uuid

from geoalchemy2 import Geography
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class."""


class User(Base):
    __tablename__ = "users"

    uid: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    role: Mapped[str] = mapped_column(String(32), default="standard")
    display_name: Mapped[Optional[str]] = mapped_column(String(120))
    language: Mapped[str] = mapped_column(String(8), default="en")
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    sessions: Mapped[List["DeviceSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    bookings: Mapped[List["Booking"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subscriptions: Mapped[List["NotificationSubscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class DeviceSession(Base):
    __tablename__ = "device_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.uid", ondelete="CASCADE"), index=True)
    device_ip: Mapped[str] = mapped_column(String(64))
    device_type: Mapped[Optional[str]] = mapped_column(String(64))
    device_os: Mapped[Optional[str]] = mapped_column(String(64))
    session_start: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    last_activity: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    ip_rotation_detected: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship(back_populates="sessions")


class City(Base):
    __tablename__ = "cities"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    population: Mapped[Optional[int]] = mapped_column(Integer)

    attractions: Mapped[List["Attraction"]] = relationship(back_populates="city", cascade="all, delete-orphan")


class Attraction(Base):
    __tablename__ = "attractions"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    city_id: Mapped[str] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(64))
    rating: Mapped[Optional[float]] = mapped_column(Float)
    opening_hours: Mapped[Optional[str]] = mapped_column(String(64))
    entry_fee: Mapped[Optional[str]] = mapped_column(String(64))
    location: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    tags: Mapped[List[str]] = mapped_column(JSONB, default=list)

    city: Mapped[City] = relationship(back_populates="attractions")


class TravelRoute(Base):
    __tablename__ = "travel_routes"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    origin: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    destination: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    estimated_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    available_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_seat: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    distance_km: Mapped[Optional[float]] = mapped_column(Float)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    amenities: Mapped[List[str]] = mapped_column(JSONB, default=list)
    route_geometry: Mapped[Optional[str]] = mapped_column(Geography(geometry_type="LINESTRING", srid=4326))

    bookings: Mapped[List["Booking"]] = relationship(back_populates="route", cascade="all, delete-orphan")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    route_id: Mapped[str] = mapped_column(ForeignKey("travel_routes.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.uid", ondelete="CASCADE"), index=True)
    passengers: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(32), nullable=False)
    special_requests: Mapped[Optional[str]] = mapped_column(String(280))
    status: Mapped[str] = mapped_column(String(24), default="confirmed")
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    estimated_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)

    route: Mapped[TravelRoute] = relationship(back_populates="bookings")
    user: Mapped[User] = relationship(back_populates="bookings")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.uid", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship(back_populates="notifications")


class NotificationSubscription(Base):
    __tablename__ = "notification_subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.uid", ondelete="CASCADE"), index=True)
    token: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    channels: Mapped[List[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship(back_populates="subscriptions")
