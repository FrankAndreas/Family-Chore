"""People come from the family hub (spec 2026-10-30): a hub id, whether the hub lists them; no PINs any more

Revision ID: a1b2c3d4e5f6
Revises: 3f3aab4a71ed
Create Date: 2026-10-30 21:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '3f3aab4a71ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # batch: SQLite can't drop a column or add a constraint in place; the table is rebuilt
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("hub_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch.create_unique_constraint("uq_users_hub_id", ["hub_id"])
        batch.drop_column("login_pin")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("login_pin", sa.String(), nullable=False, server_default=""))
        batch.drop_constraint("uq_users_hub_id", type_="unique")
        batch.drop_column("is_active")
        batch.drop_column("hub_id")
