"""Add User.hash_format and Result.export columns

Revision ID: cd3f8e6affcc
Revises: 95fe71fbb867
Create Date: 2025-01-03 21:26:19.812712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd3f8e6affcc'
down_revision: Union[str, None] = '95fe71fbb867'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('hash_format', sa.String(), nullable=False, default='legacy'))
    op.add_column('results', sa.Column('export', sa.Boolean()))


def downgrade() -> None:
    op.drop_column('users', 'hash_format')
    op.drop_column('results', 'export')
