"""empty message

Revision ID: ca5e26fc0cb5
Revises: d81faa7c470b
Create Date: 2017-04-30 18:50:25.977000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca5e26fc0cb5'
down_revision = 'd81faa7c470b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'password_hash')
    # ### end Alembic commands ###