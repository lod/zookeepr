"""text match extensions

Revision ID: 4985a66cf639
Revises: 1c22ceb384a7
Create Date: 2015-09-04 02:36:46.128345

"""

# revision identifiers, used by Alembic.
revision = '4985a66cf639'
down_revision = '1c22ceb384a7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # pg_trgm provides trigram based algorithm for fuzzy string matching
    op.execute("CREATE EXTENSION pg_trgm")
    # Index the trigram to make life not turtle speed
    op.execute("CREATE INDEX proposal_abstract_tri ON proposal USING gist (abstract gist_trgm_ops)")
    op.execute("CREATE INDEX proposal_title_tri ON proposal USING gist (title gist_trgm_ops)")
    # proposal (status_id) is very commonly hit to filter proposals
    op.execute("CREATE INDEX proposal_status_id ON proposal (status_id)")

def downgrade():
    op.execute("DROP INDEX proposal_abstract_tri")
    op.execute("DROP INDEX proposal_title_tri")
    op.execute("DROP EXTENSION pg_trgm")
    op.execute("DROP INDEX proposal_status_id")
