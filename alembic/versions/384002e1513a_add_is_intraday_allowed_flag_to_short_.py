"""add is_intraday_allowed flag to short listed stocks

Revision ID: 384002e1513a
Revises: d188049f0ace
Create Date: 2022-03-18 00:06:37.356076

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision = '384002e1513a'
down_revision = 'd188049f0ace'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('shortlisted_stocks', sa.Column(
        'is_intraday_allowed',
        sa.Boolean(),
        default=False
    ))


def downgrade():
    op.drop_column('shortlisted_stocks', 'is_intraday_allowed')
