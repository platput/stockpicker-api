"""add symbol exists to stocknames table

Revision ID: a75b7537cf2d
Revises: 384002e1513a
Create Date: 2022-04-16 11:51:47.601964

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column


# revision identifiers, used by Alembic.
revision = 'a75b7537cf2d'
down_revision = '384002e1513a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('stock_names', Column('symbol_exists', sa.Boolean(), nullable=True, default=False))


def downgrade():
    op.drop_column('stock_names', 'symbol_exists')

