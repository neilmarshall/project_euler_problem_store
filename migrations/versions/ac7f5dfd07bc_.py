"""empty message

Revision ID: ac7f5dfd07bc
Revises: 8c684b973618
Create Date: 2019-05-31 20:37:48.344745

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ac7f5dfd07bc'
down_revision = '8c684b973618'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('problems', sa.Column('title', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('problems', 'title')
