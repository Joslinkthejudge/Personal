"""changed password field

Revision ID: 9fbdc3fb242c
Revises: 
Create Date: 2023-07-18 08:34:08.263928

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9fbdc3fb242c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('_password', sa.String(length=120), nullable=False))
        batch_op.drop_index('password')
        batch_op.create_unique_constraint(None, ['_password'])
        batch_op.drop_column('password')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', mysql.VARCHAR(length=120), nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_index('password', ['password'], unique=False)
        batch_op.drop_column('_password')

    # ### end Alembic commands ###
