"""notification subscriptions

Revision ID: 20260116_000002
Revises: 20260116_000001
Create Date: 2026-01-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260116_000002"
down_revision = "20260116_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_subscriptions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=64), sa.ForeignKey("users.uid", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(length=512), nullable=False),
        sa.Column("channels", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notification_subscriptions_user_id", "notification_subscriptions", ["user_id"])
    op.create_unique_constraint("uq_notification_subscriptions_token", "notification_subscriptions", ["token"])


def downgrade() -> None:
    op.drop_constraint("uq_notification_subscriptions_token", "notification_subscriptions", type_="unique")
    op.drop_index("ix_notification_subscriptions_user_id", table_name="notification_subscriptions")
    op.drop_table("notification_subscriptions")
