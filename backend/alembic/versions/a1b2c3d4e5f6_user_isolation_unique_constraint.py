"""User isolation — update unique constraint on daily_reports to include user_id

Revision ID: a1b2c3d4e5f6
Revises: 529dfc79d8bd
Create Date: 2026-06-21 15:20:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '529dfc79d8bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update unique constraint and index to include user_id for per-user isolation."""
    with op.batch_alter_table('daily_reports') as batch_op:
        # Drop old constraint and index (if they exist)
        try:
            batch_op.drop_constraint('uq_vessel_report_date', type_='unique')
        except Exception:
            pass  # Constraint may not exist if already updated
        try:
            batch_op.drop_index('ix_vessel_report_date')
        except Exception:
            pass  # Index may not exist

        # Create new constraint and index including user_id
        batch_op.create_unique_constraint(
            'uq_vessel_report_date_user',
            ['vessel_id', 'report_date', 'user_id'],
        )
        batch_op.create_index(
            'ix_vessel_report_date_user',
            ['vessel_id', 'report_date', 'user_id'],
        )


def downgrade() -> None:
    """Revert to the original (vessel_id, report_date) constraint."""
    with op.batch_alter_table('daily_reports') as batch_op:
        batch_op.drop_index('ix_vessel_report_date_user')
        batch_op.drop_constraint('uq_vessel_report_date_user', type_='unique')

        batch_op.create_unique_constraint(
            'uq_vessel_report_date',
            ['vessel_id', 'report_date'],
        )
        batch_op.create_index(
            'ix_vessel_report_date',
            ['vessel_id', 'report_date'],
        )
