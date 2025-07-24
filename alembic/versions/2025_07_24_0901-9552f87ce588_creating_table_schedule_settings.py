from datetime import time
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, Time
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9552f87ce588'
down_revision: Union[str, None] = '23c133c5b8d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

schedule_settings_table = table(
    "schedule_settings",
    column("id", Integer),
    column("working_days", postgresql.ARRAY(Integer)),
    column("start_working_time", Time),
    column("end_working_time", Time),
    column("booking_days_ahead", Integer),
    column("slot_duration_minutes", Integer),
)


def upgrade() -> None:
    op.create_table('schedule_settings',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('working_days', postgresql.ARRAY(sa.Integer()), nullable=False),
                    sa.Column('start_working_time', sa.Time(), server_default=sa.text("'09:00:00'"), nullable=False),
                    sa.Column('end_working_time', sa.Time(), server_default=sa.text("'18:00:00'"), nullable=False),
                    sa.Column('booking_days_ahead', sa.Integer(), server_default=sa.text('14'), nullable=False),
                    sa.Column('slot_duration_minutes', sa.Integer(), server_default=sa.text('30'), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.bulk_insert(
        schedule_settings_table,
        [{
            "id": 1,
            "working_days": [0, 1, 2, 3, 4],
            "start_working_time": time(9, 0, 0),
            "end_working_time": time(18, 0, 0),
            "booking_days_ahead": 14,
            "slot_duration_minutes": 30,
        }]
    )


def downgrade() -> None:
    op.drop_table('schedule_settings')
