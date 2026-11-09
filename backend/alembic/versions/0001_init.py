"""initial schema (static DDL snapshot of the models at this revision)

Revision ID: 0001
Revises:
"""
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# Static SQL on purpose: later model edits must come as new migrations, not rewrite history.
STATEMENTS = [
    """CREATE TYPE unit_kind AS ENUM ('OWN', 'SUBCONTRACT')""",
    """CREATE TYPE milestone_kind AS ENUM ('STAGE', 'MANUAL')""",
    """CREATE TYPE stage_key AS ENUM ('CUTTING', 'PRINTING', 'STITCHING', 'WASHING', 'FINISHING', 'PACKING')""",
    """CREATE TYPE role AS ENUM ('MERCHANDISER', 'SUPERVISOR')""",
    """CREATE TYPE note_category AS ENUM ('MACHINE_BREAKDOWN', 'POWER_CUT', 'ABSENTEEISM', 'MATERIAL_SHORTAGE', 'QUALITY_REWORK', 'SUBCONTRACTOR_DELAY', 'APPROVAL_PENDING', 'OTHER', 'NEEDS_REVIEW')""",
    """CREATE TYPE note_source AS ENUM ('AI', 'RULE', 'HUMAN')""",
    """CREATE TYPE warning_status AS ENUM ('DRAFT', 'CONFIRMED', 'DISMISSED')""",
    """CREATE TYPE health AS ENUM ('GREEN', 'AMBER', 'RED', 'GREY')""",
    """CREATE TABLE ai_cache (
	hash VARCHAR NOT NULL, 
	model VARCHAR NOT NULL, 
	result JSONB NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (hash)
)""",
    """CREATE TABLE audit_log (
	id VARCHAR NOT NULL, 
	actor_id VARCHAR, 
	action VARCHAR NOT NULL, 
	entity VARCHAR NOT NULL, 
	entity_id VARCHAR NOT NULL, 
	meta JSONB NOT NULL, 
	at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
)""",
    """CREATE TABLE buyers (
	id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	country VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
)""",
    """CREATE TABLE holidays (
	date DATE NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (date)
)""",
    """CREATE TABLE rate_limits (
	key VARCHAR NOT NULL, 
	count BIGINT NOT NULL, 
	window_start TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (key)
)""",
    """CREATE TABLE tna_templates (
	id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
)""",
    """CREATE TABLE units (
	id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	kind unit_kind NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
)""",
    """CREATE TABLE buyer_links (
	id VARCHAR NOT NULL, 
	buyer_id VARCHAR NOT NULL, 
	token_hash VARCHAR NOT NULL, 
	label VARCHAR NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	revoked_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(buyer_id) REFERENCES buyers (id), 
	UNIQUE (token_hash)
)""",
    """CREATE TABLE tna_items (
	id VARCHAR NOT NULL, 
	template_id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	kind milestone_kind NOT NULL, 
	stage_key stage_key, 
	offset_days INTEGER NOT NULL, 
	print_only BOOLEAN NOT NULL, 
	sort_order INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(template_id) REFERENCES tna_templates (id) ON DELETE CASCADE
)""",
    """CREATE TABLE users (
	id VARCHAR NOT NULL, 
	username VARCHAR NOT NULL, 
	display_name VARCHAR NOT NULL, 
	password_hash VARCHAR NOT NULL, 
	role role NOT NULL, 
	unit_id VARCHAR, 
	lang VARCHAR NOT NULL, 
	failed_logins INTEGER NOT NULL, 
	locked_until TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	FOREIGN KEY(unit_id) REFERENCES units (id)
)""",
    """CREATE TABLE orders (
	id VARCHAR NOT NULL, 
	po_no VARCHAR NOT NULL, 
	buyer_id VARCHAR NOT NULL, 
	style VARCHAR NOT NULL, 
	colour VARCHAR NOT NULL, 
	qty INTEGER NOT NULL, 
	has_print BOOLEAN NOT NULL, 
	has_wash BOOLEAN NOT NULL, 
	ex_factory DATE NOT NULL, 
	ex_factory_original DATE NOT NULL, 
	template_id VARCHAR NOT NULL, 
	created_by_id VARCHAR, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (po_no), 
	FOREIGN KEY(buyer_id) REFERENCES buyers (id), 
	FOREIGN KEY(template_id) REFERENCES tna_templates (id), 
	FOREIGN KEY(created_by_id) REFERENCES users (id)
)""",
    """CREATE INDEX ix_orders_buyer_exf ON orders (buyer_id, ex_factory)""",
    """CREATE TABLE daily_logs (
	id VARCHAR NOT NULL, 
	order_id VARCHAR NOT NULL, 
	stage_key stage_key NOT NULL, 
	log_date DATE NOT NULL, 
	qty INTEGER NOT NULL, 
	superseded_by_id VARCHAR, 
	entered_by_id VARCHAR NOT NULL, 
	client_created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_log_qty CHECK (qty >= 0), 
	FOREIGN KEY(order_id) REFERENCES orders (id), 
	FOREIGN KEY(superseded_by_id) REFERENCES daily_logs (id), 
	FOREIGN KEY(entered_by_id) REFERENCES users (id)
)""",
    """CREATE INDEX ix_logs_order_stage_date ON daily_logs (order_id, stage_key, log_date)""",
    """CREATE UNIQUE INDEX one_effective_log ON daily_logs (order_id, stage_key, log_date) WHERE superseded_by_id IS NULL""",
    """CREATE TABLE ex_factory_changes (
	id VARCHAR NOT NULL, 
	order_id VARCHAR NOT NULL, 
	from_date DATE NOT NULL, 
	to_date DATE NOT NULL, 
	reason_code VARCHAR NOT NULL, 
	reason_text TEXT, 
	changed_by_id VARCHAR NOT NULL, 
	changed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES orders (id), 
	FOREIGN KEY(changed_by_id) REFERENCES users (id)
)""",
    """CREATE INDEX ix_ex_factory_changes_order_id ON ex_factory_changes (order_id)""",
    """CREATE TABLE milestones (
	id VARCHAR NOT NULL, 
	order_id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	kind milestone_kind NOT NULL, 
	stage_key stage_key, 
	planned_date DATE NOT NULL, 
	actual_date DATE, 
	sort_order INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (order_id, name), 
	FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE CASCADE
)""",
    """CREATE TABLE order_lines (
	id VARCHAR NOT NULL, 
	order_id VARCHAR NOT NULL, 
	size VARCHAR NOT NULL, 
	qty INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (order_id, size), 
	CONSTRAINT ck_line_qty CHECK (qty > 0), 
	FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE CASCADE
)""",
    """CREATE TABLE stage_assignments (
	order_id VARCHAR NOT NULL, 
	stage_key stage_key NOT NULL, 
	unit_id VARCHAR NOT NULL, 
	PRIMARY KEY (order_id, stage_key), 
	FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE CASCADE, 
	FOREIGN KEY(unit_id) REFERENCES units (id)
)""",
    """CREATE INDEX ix_stage_assignments_unit_id ON stage_assignments (unit_id)""",
    """CREATE TABLE issue_notes (
	id VARCHAR NOT NULL, 
	log_id VARCHAR NOT NULL, 
	order_id VARCHAR NOT NULL, 
	original_text TEXT NOT NULL, 
	lang VARCHAR NOT NULL, 
	translation_en TEXT NOT NULL, 
	category note_category NOT NULL, 
	confidence FLOAT, 
	source note_source NOT NULL, 
	reviewed_by_id VARCHAR, 
	reviewed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(log_id) REFERENCES daily_logs (id), 
	FOREIGN KEY(order_id) REFERENCES orders (id), 
	FOREIGN KEY(reviewed_by_id) REFERENCES users (id)
)""",
    """CREATE INDEX ix_issue_notes_order_id ON issue_notes (order_id)""",
    """CREATE TABLE photos (
	id VARCHAR NOT NULL, 
	log_id VARCHAR NOT NULL, 
	mime VARCHAR NOT NULL, 
	size_bytes INTEGER NOT NULL, 
	share_with_buyer BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(log_id) REFERENCES daily_logs (id)
)""",
    """CREATE TABLE photo_blobs (
	photo_id VARCHAR NOT NULL, 
	bytes BYTEA NOT NULL, 
	PRIMARY KEY (photo_id), 
	FOREIGN KEY(photo_id) REFERENCES photos (id) ON DELETE CASCADE
)""",
    """CREATE TABLE warnings (
	id VARCHAR NOT NULL, 
	order_id VARCHAR NOT NULL, 
	status warning_status NOT NULL, 
	health health NOT NULL, 
	snapshot JSONB NOT NULL, 
	note_id VARCHAR, 
	category_final note_category, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	confirmed_by_id VARCHAR, 
	confirmed_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES orders (id), 
	FOREIGN KEY(note_id) REFERENCES issue_notes (id), 
	FOREIGN KEY(confirmed_by_id) REFERENCES users (id)
)""",
    """CREATE INDEX ix_warnings_order_id ON warnings (order_id)""",
    """CREATE UNIQUE INDEX one_open_warning ON warnings (order_id) WHERE status = 'DRAFT'""",
    """CREATE TABLE outbox_messages (
	id VARCHAR NOT NULL, 
	buyer_id VARCHAR NOT NULL, 
	subject VARCHAR NOT NULL, 
	body TEXT NOT NULL, 
	warning_id VARCHAR, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(buyer_id) REFERENCES buyers (id), 
	FOREIGN KEY(warning_id) REFERENCES warnings (id)
)""",
]

DROPS = [
    "DROP TABLE IF EXISTS outbox_messages CASCADE",
    "DROP TABLE IF EXISTS warnings CASCADE",
    "DROP TABLE IF EXISTS photo_blobs CASCADE",
    "DROP TABLE IF EXISTS photos CASCADE",
    "DROP TABLE IF EXISTS issue_notes CASCADE",
    "DROP TABLE IF EXISTS stage_assignments CASCADE",
    "DROP TABLE IF EXISTS order_lines CASCADE",
    "DROP TABLE IF EXISTS milestones CASCADE",
    "DROP TABLE IF EXISTS ex_factory_changes CASCADE",
    "DROP TABLE IF EXISTS daily_logs CASCADE",
    "DROP TABLE IF EXISTS orders CASCADE",
    "DROP TABLE IF EXISTS users CASCADE",
    "DROP TABLE IF EXISTS tna_items CASCADE",
    "DROP TABLE IF EXISTS buyer_links CASCADE",
    "DROP TABLE IF EXISTS units CASCADE",
    "DROP TABLE IF EXISTS tna_templates CASCADE",
    "DROP TABLE IF EXISTS rate_limits CASCADE",
    "DROP TABLE IF EXISTS holidays CASCADE",
    "DROP TABLE IF EXISTS buyers CASCADE",
    "DROP TABLE IF EXISTS audit_log CASCADE",
    "DROP TABLE IF EXISTS ai_cache CASCADE",
    "DROP TYPE IF EXISTS unit_kind",
    "DROP TYPE IF EXISTS milestone_kind",
    "DROP TYPE IF EXISTS stage_key",
    "DROP TYPE IF EXISTS role",
    "DROP TYPE IF EXISTS note_category",
    "DROP TYPE IF EXISTS note_source",
    "DROP TYPE IF EXISTS warning_status",
    "DROP TYPE IF EXISTS health",
]


def upgrade() -> None:
    for stmt in STATEMENTS:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DROPS:
        op.execute(stmt)
