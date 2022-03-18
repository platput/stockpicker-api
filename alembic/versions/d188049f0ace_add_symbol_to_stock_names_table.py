"""add symbol to stock_names table

Revision ID: d188049f0ace
Revises: 3892a425cf5b
Create Date: 2022-03-17 20:14:29.610953

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column


# revision identifiers, used by Alembic.
revision = 'd188049f0ace'
down_revision = '3892a425cf5b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('stock_names', Column('symbol', sa.String(), nullable=True))


def downgrade():
    op.drop_column('stock_names', 'symbol')
