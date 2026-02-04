"""add moodle_user_id and remove password

Revision ID: bbf99b17b878
Revises: 
Create Date: 2026-02-03 03:02:15.056845

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bbf99b17b878'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('moodle_user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('username', sa.String(length=100), nullable=True))
        batch_op.alter_column(
            'mail',
            existing_type=mysql.VARCHAR(length=50),
            type_=sa.String(length=255),
            existing_nullable=False
        )
        batch_op.alter_column(
            'role',
            existing_type=mysql.VARCHAR(length=50),
            nullable=True
        )
        batch_op.drop_index(batch_op.f('mail'))
        batch_op.create_unique_constraint(None, ['moodle_user_id'])
        batch_op.drop_column('user_name')
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###


def downgrade():
     pass
