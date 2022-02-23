"""add stock details url column and create sector table

Revision ID: 3892a425cf5b
Revises: 84912adf4ed2
Create Date: 2022-02-23 23:06:07.820752

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey, Column
from sqlalchemy_utils import UUIDType
import uuid

# revision identifiers, used by Alembic.

revision = '3892a425cf5b'
down_revision = '84912adf4ed2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('sectors',
                    sa.Column('id', UUIDType(binary=False), nullable=False, default=uuid.uuid4()),
                    sa.Column('sector_name', sa.String(), nullable=False, unique=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    )

    op.add_column('stock_names', Column('sector_id', UUIDType(binary=False), ForeignKey('sectors.id')))
    op.add_column('stock_names', Column('details_url', sa.String()))


def downgrade():
    op.drop_column('stock_names', 'details_url')
    op.drop_column('op.', 'sector_id')
    op.drop_table('sectors')
