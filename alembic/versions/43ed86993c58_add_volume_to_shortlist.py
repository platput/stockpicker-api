"""add_volume_to_shortlist

Revision ID: 43ed86993c58
Revises: a75b7537cf2d
Create Date: 2022-05-14 21:37:50.418373

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import Column

revision = '43ed86993c58'
down_revision = 'a75b7537cf2d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('shortlisted_stocks', Column('volume', sa.Numeric(), nullable=True))


def downgrade():
    op.drop_column('shortlisted_stocks', 'volume')

