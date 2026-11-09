"""append-only triggers (the partial unique indexes already exist from 0001)

Revision ID: 0002
Revises: 0001
"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Doc3 6.1: the database itself blocks edits to the compliance history (FR-19).
    op.execute(
        "CREATE FUNCTION no_mutation() RETURNS trigger AS $$ "
        "BEGIN RAISE EXCEPTION 'append-only table'; END $$ LANGUAGE plpgsql"
    )
    op.execute(
        "CREATE TRIGGER exf_immutable BEFORE UPDATE OR DELETE ON ex_factory_changes "
        "FOR EACH ROW EXECUTE FUNCTION no_mutation()"
    )
    op.execute(
        "CREATE TRIGGER audit_immutable BEFORE UPDATE OR DELETE ON audit_log "
        "FOR EACH ROW EXECUTE FUNCTION no_mutation()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS audit_immutable ON audit_log")
    op.execute("DROP TRIGGER IF EXISTS exf_immutable ON ex_factory_changes")
    op.execute("DROP FUNCTION IF EXISTS no_mutation()")
