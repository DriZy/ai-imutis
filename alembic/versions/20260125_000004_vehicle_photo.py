"""add vehicle photo url

Revision ID: 20260125_000004
Revises: 20260125_000003
Create Date: 2026-01-25
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260125_000004"
down_revision = "20260125_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("vehicles", sa.Column("photo_url", sa.String(length=512), nullable=False, server_default=""))
    # Drop the server_default after populating existing rows (none in fresh deployments)
    op.alter_column("vehicles", "photo_url", server_default=None)


def downgrade() -> None:
    op.drop_column("vehicles", "photo_url")
