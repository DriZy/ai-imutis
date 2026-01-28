"""add vehicles table

Revision ID: 20260125_000003
Revises: 20260116_000002
Create Date: 2026-01-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260125_000003"
down_revision = "20260116_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create vehicles table
    op.create_table(
        "vehicles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_id", sa.String(length=64), sa.ForeignKey("users.uid", ondelete="CASCADE"), nullable=False),
        sa.Column("vehicle_type", sa.String(length=32), nullable=False),
        sa.Column("make", sa.String(length=64)),
        sa.Column("model", sa.String(length=64)),
        sa.Column("year", sa.Integer()),
        sa.Column("license_plate", sa.String(length=32), nullable=False, unique=True),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(length=32)),
        sa.Column("amenities", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_vehicles_owner_id", "vehicles", ["owner_id"])
    op.create_index("ix_vehicles_license_plate", "vehicles", ["license_plate"])

    # Add vehicle_id and owner_id to travel_routes
    op.add_column("travel_routes", sa.Column("vehicle_id", sa.String(length=36), sa.ForeignKey("vehicles.id", ondelete="SET NULL")))
    op.add_column("travel_routes", sa.Column("owner_id", sa.String(length=64), sa.ForeignKey("users.uid", ondelete="CASCADE")))
    op.create_index("ix_travel_routes_vehicle_id", "travel_routes", ["vehicle_id"])
    op.create_index("ix_travel_routes_owner_id", "travel_routes", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_travel_routes_owner_id", table_name="travel_routes")
    op.drop_index("ix_travel_routes_vehicle_id", table_name="travel_routes")
    op.drop_column("travel_routes", "owner_id")
    op.drop_column("travel_routes", "vehicle_id")
    op.drop_index("ix_vehicles_license_plate", table_name="vehicles")
    op.drop_index("ix_vehicles_owner_id", table_name="vehicles")
    op.drop_table("vehicles")
