"""empty message

Revision ID: 7df2f99f6190
Revises: b0389155940e
Create Date: 2019-05-06 18:11:44.358993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7df2f99f6190'
down_revision = 'b0389155940e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('languages',
    sa.Column('language_id', sa.Integer(), nullable=False),
    sa.Column('language', sa.String(length=16), nullable=False),
    sa.PrimaryKeyConstraint('language_id')
    )
    op.add_column('problems', sa.Column('language', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'problems', 'languages', ['language'], ['language_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'problems', type_='foreignkey')
    op.drop_column('problems', 'language')
    op.drop_table('languages')
    # ### end Alembic commands ###