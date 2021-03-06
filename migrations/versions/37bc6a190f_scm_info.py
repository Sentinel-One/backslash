"""SCM Info

Revision ID: 37bc6a190f
Revises: 31a5269d02d
Create Date: 2015-10-03 23:08:48.308287

"""

# revision identifiers, used by Alembic.
revision = '37bc6a190f'
down_revision = '31a5269d02d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('test', sa.Column('file_hash', sa.String(length=40), nullable=True))
    op.add_column('test', sa.Column('scm', sa.String(length=5), nullable=True))
    op.add_column('test', sa.Column('scm_dirty', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('test', sa.Column('scm_revision', sa.String(length=40), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('test', 'scm_revision')
    op.drop_column('test', 'scm_dirty')
    op.drop_column('test', 'scm')
    op.drop_column('test', 'file_hash')
    ### end Alembic commands ###
