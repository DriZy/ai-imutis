"""initial schema

Revision ID: 20260116_000001
Revises: 
Create Date: 2026-01-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = "20260116_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "users",
        sa.Column("uid", sa.String(length=64), primary_key=True),
        sa.Column("email", sa.String(length=255), index=True),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="standard"),
        sa.Column("display_name", sa.String(length=120)),
        sa.Column("language", sa.String(length=8), nullable=False, server_default="en"),
        sa.Column("notification_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "cities",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("country", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("population", sa.Integer()),
    )

    op.create_table(
        "travel_routes",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("origin", sa.String(length=120), nullable=False),
        sa.Column("destination", sa.String(length=120), nullable=False),
        sa.Column("departure_time", sa.DateTime(), nullable=False),
        sa.Column("estimated_arrival", sa.DateTime(), nullable=False),
        sa.Column("available_seats", sa.Integer(), nullable=False),
        sa.Column("price_per_seat", sa.Numeric(10, 2), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("distance_km", sa.Float()),
        sa.Column("duration_minutes", sa.Integer()),
        sa.Column("amenities", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb")),
        sa.Column("route_geometry", Geography(geometry_type="LINESTRING", srid=4326)),
    )
    op.create_index("ix_travel_routes_origin", "travel_routes", ["origin"])
    op.create_index("ix_travel_routes_destination", "travel_routes", ["destination"])

    op.create_table(
        "device_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=64), sa.ForeignKey("users.uid", ondelete="CASCADE"), nullable=False),
        sa.Column("device_ip", sa.String(length=64), nullable=False),
        sa.Column("device_type", sa.String(length=64)),
        sa.Column("device_os", sa.String(length=64)),
        sa.Column("session_start", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_activity", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("ip_rotation_detected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_device_sessions_user_id", "device_sessions", ["user_id"])

    op.create_table(
        "attractions",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("city_id", sa.String(length=64), sa.ForeignKey("cities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("category", sa.String(length=64)),
        sa.Column("rating", sa.Float()),
        sa.Column("opening_hours", sa.String(length=64)),
        sa.Column("entry_fee", sa.String(length=64)),
        sa.Column("location", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb")),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb")),
    )
    op.create_index("ix_attractions_city_id", "attractions", ["city_id"])

    op.create_table(
        "bookings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("route_id", sa.String(length=128), sa.ForeignKey("travel_routes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(length=64), sa.ForeignKey("users.uid", ondelete="CASCADE"), nullable=False),
        sa.Column("passengers", sa.Integer(), nullable=False),
        sa.Column("payment_method", sa.String(length=32), nullable=False),
        sa.Column("special_requests", sa.String(length=280)),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="confirmed"),
        sa.Column("departure_time", sa.DateTime(), nullable=False),
        sa.Column("estimated_arrival", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_bookings_route_id", "bookings", ["route_id"])
    op.create_index("ix_bookings_user_id", "bookings", ["user_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=64), sa.ForeignKey("users.uid", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=64)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_bookings_user_id", table_name="bookings")
    op.drop_index("ix_bookings_route_id", table_name="bookings")
    op.drop_table("bookings")
    op.drop_index("ix_attractions_city_id", table_name="attractions")
    op.drop_table("attractions")
    op.drop_index("ix_device_sessions_user_id", table_name="device_sessions")
    op.drop_table("device_sessions")
    op.drop_index("ix_travel_routes_destination", table_name="travel_routes")
    op.drop_index("ix_travel_routes_origin", table_name="travel_routes")
    op.drop_table("travel_routes")
    op.drop_table("cities")
    op.drop_table("users")