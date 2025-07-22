"""create_id_sequence

Revision ID: 9370fa5a3d4c
Revises: e620193cd1a9
Create Date: 2025-07-22 15:47:23.508573

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9370fa5a3d4c'
down_revision: Union[str, None] = 'e620193cd1a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE SEQUENCE id_sequence START 1;")


def downgrade():
    op.execute("DROP SEQUENCE id_sequence;")
