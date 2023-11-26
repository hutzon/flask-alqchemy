"""empty message

Revision ID: 1b0c496ef4c7
Revises: f3b93de651ed
Create Date: 2023-11-14 06:32:16.139401

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b0c496ef4c7'
down_revision = 'f3b93de651ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('alumno',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=250), nullable=True),
    sa.Column('apellido', sa.String(length=250), nullable=True),
    sa.Column('edad', sa.Integer(), nullable=True),
    sa.Column('profesor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['profesor_id'], ['profesor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('alumno')
    # ### end Alembic commands ###