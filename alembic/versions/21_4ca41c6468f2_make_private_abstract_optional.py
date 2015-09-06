"""make private abstract optional

Revision ID: 4ca41c6468f2
Revises: 4985a66cf639
Create Date: 2015-09-06 19:42:52.745488

"""

# revision identifiers, used by Alembic.
revision = '4ca41c6468f2'
down_revision = '4985a66cf639'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("ALTER TABLE proposal ALTER private_abstract DROP NOT NULL")


def downgrade():
    op.execute("ALTER TABLE proposal ALTER private_abstract SET NOT NULL")
