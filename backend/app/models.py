"""SQLAlchemy 2.0 models (Doc3 section 6). Append-only triggers and partial unique
indexes that need raw SQL live in migration 0002; the partial indexes are also
declared here so tests on a clean schema see them."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

JsonType = JSON().with_variant(JSONB(), "postgresql")

ROLES = ("MERCHANDISER", "SUPERVISOR")
UNIT_KINDS = ("OWN", "SUBCONTRACT")
STAGE_KEYS = ("CUTTING", "PRINTING", "STITCHING", "WASHING", "FINISHING", "PACKING")
MILESTONE_KINDS = ("STAGE", "MANUAL")
WARNING_STATUSES = ("DRAFT", "CONFIRMED", "DISMISSED")
NOTE_SOURCES = ("AI", "RULE", "HUMAN")
NOTE_CATEGORIES = (
    "MACHINE_BREAKDOWN", "POWER_CUT", "ABSENTEEISM", "MATERIAL_SHORTAGE", "QUALITY_REWORK",
    "SUBCONTRACTOR_DELAY", "APPROVAL_PENDING", "OTHER", "NEEDS_REVIEW",
)
HEALTHS = ("GREEN", "AMBER", "RED", "GREY")


def new_id() -> str:
    return uuid.uuid4().hex


def _enum(values: tuple[str, ...], name: str) -> Enum:
    return Enum(*values, name=name)


def _ts() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Base(DeclarativeBase):
    pass


class Unit(Base):
    __tablename__ = "units"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String, unique=True)
    kind: Mapped[str] = mapped_column(_enum(UNIT_KINDS, "unit_kind"))


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    username: Mapped[str] = mapped_column(String, unique=True)
    display_name: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(_enum(ROLES, "role"))
    unit_id: Mapped[str | None] = mapped_column(ForeignKey("units.id"))
    lang: Mapped[str] = mapped_column(String, default="en")
    failed_logins: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _ts()


class Buyer(Base):
    __tablename__ = "buyers"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String, unique=True)
    country: Mapped[str] = mapped_column(String)


class BuyerLink(Base):
    __tablename__ = "buyer_links"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    buyer_id: Mapped[str] = mapped_column(ForeignKey("buyers.id"))
    token_hash: Mapped[str] = mapped_column(String, unique=True)
    label: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = _ts()
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TnaTemplate(Base):
    __tablename__ = "tna_templates"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String, unique=True)
    items: Mapped[list[TnaItem]] = relationship(order_by="TnaItem.sort_order", cascade="all, delete-orphan")


class TnaItem(Base):
    __tablename__ = "tna_items"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    template_id: Mapped[str] = mapped_column(ForeignKey("tna_templates.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(_enum(MILESTONE_KINDS, "milestone_kind"))
    stage_key: Mapped[str | None] = mapped_column(_enum(STAGE_KEYS, "stage_key"))
    offset_days: Mapped[int] = mapped_column(Integer)
    print_only: Mapped[bool] = mapped_column(default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (Index("ix_orders_buyer_exf", "buyer_id", "ex_factory"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    po_no: Mapped[str] = mapped_column(String, unique=True)
    buyer_id: Mapped[str] = mapped_column(ForeignKey("buyers.id"))
    style: Mapped[str] = mapped_column(String)
    colour: Mapped[str] = mapped_column(String)
    qty: Mapped[int] = mapped_column(Integer)
    has_print: Mapped[bool] = mapped_column(default=False)
    has_wash: Mapped[bool] = mapped_column(default=False)
    ex_factory: Mapped[date] = mapped_column(Date)
    ex_factory_original: Mapped[date] = mapped_column(Date)
    template_id: Mapped[str] = mapped_column(ForeignKey("tna_templates.id"))
    created_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = _ts()
    lines: Mapped[list[OrderLine]] = relationship(cascade="all, delete-orphan")
    buyer: Mapped[Buyer] = relationship()


class OrderLine(Base):
    __tablename__ = "order_lines"
    __table_args__ = (UniqueConstraint("order_id", "size"), CheckConstraint("qty > 0", name="ck_line_qty"))
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    size: Mapped[str] = mapped_column(String)
    qty: Mapped[int] = mapped_column(Integer)


class StageAssignment(Base):
    __tablename__ = "stage_assignments"
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True)
    stage_key: Mapped[str] = mapped_column(_enum(STAGE_KEYS, "stage_key"), primary_key=True)
    unit_id: Mapped[str] = mapped_column(ForeignKey("units.id"), index=True)


class Milestone(Base):
    __tablename__ = "milestones"
    __table_args__ = (UniqueConstraint("order_id", "name"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(_enum(MILESTONE_KINDS, "milestone_kind"))
    stage_key: Mapped[str | None] = mapped_column(_enum(STAGE_KEYS, "stage_key"))
    planned_date: Mapped[date] = mapped_column(Date)
    actual_date: Mapped[date | None] = mapped_column(Date)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class DailyLog(Base):
    __tablename__ = "daily_logs"
    __table_args__ = (
        CheckConstraint("qty >= 0", name="ck_log_qty"),
        Index("ix_logs_order_stage_date", "order_id", "stage_key", "log_date"),
        Index(
            "one_effective_log", "order_id", "stage_key", "log_date", unique=True,
            postgresql_where=text("superseded_by_id IS NULL"),
            sqlite_where=text("superseded_by_id IS NULL"),
        ),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True)  # client UUID = idempotency key
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    stage_key: Mapped[str] = mapped_column(_enum(STAGE_KEYS, "stage_key"))
    log_date: Mapped[date] = mapped_column(Date)
    qty: Mapped[int] = mapped_column(Integer)
    superseded_by_id: Mapped[str | None] = mapped_column(ForeignKey("daily_logs.id"))
    entered_by_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    client_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _ts()


class Photo(Base):
    __tablename__ = "photos"
    id: Mapped[str] = mapped_column(String, primary_key=True)  # client UUID
    log_id: Mapped[str] = mapped_column(ForeignKey("daily_logs.id"))
    mime: Mapped[str] = mapped_column(String)
    size_bytes: Mapped[int] = mapped_column(Integer)
    share_with_buyer: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = _ts()


class PhotoBlob(Base):
    __tablename__ = "photo_blobs"
    photo_id: Mapped[str] = mapped_column(ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True)
    bytes: Mapped[bytes] = mapped_column(LargeBinary)


class IssueNote(Base):
    __tablename__ = "issue_notes"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    log_id: Mapped[str] = mapped_column(ForeignKey("daily_logs.id"))
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    original_text: Mapped[str] = mapped_column(Text)
    lang: Mapped[str] = mapped_column(String, default="ta")
    translation_en: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(_enum(NOTE_CATEGORIES, "note_category"))
    confidence: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str] = mapped_column(_enum(NOTE_SOURCES, "note_source"))
    reviewed_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _ts()


class Warning(Base):
    __tablename__ = "warnings"
    __table_args__ = (
        Index(
            "one_open_warning", "order_id", unique=True,
            postgresql_where=text("status = 'DRAFT'"),
            sqlite_where=text("status = 'DRAFT'"),
        ),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    status: Mapped[str] = mapped_column(_enum(WARNING_STATUSES, "warning_status"), default="DRAFT")
    health: Mapped[str] = mapped_column(_enum(HEALTHS, "health"))
    snapshot: Mapped[dict] = mapped_column(JsonType)
    note_id: Mapped[str | None] = mapped_column(ForeignKey("issue_notes.id"))
    category_final: Mapped[str | None] = mapped_column(_enum(NOTE_CATEGORIES, "note_category"))
    created_at: Mapped[datetime] = _ts()
    updated_at: Mapped[datetime] = _ts()
    confirmed_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ExFactoryChange(Base):
    __tablename__ = "ex_factory_changes"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    from_date: Mapped[date] = mapped_column(Date)
    to_date: Mapped[date] = mapped_column(Date)
    reason_code: Mapped[str] = mapped_column(String)
    reason_text: Mapped[str | None] = mapped_column(Text)
    changed_by_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    changed_at: Mapped[datetime] = _ts()


class Holiday(Base):
    __tablename__ = "holidays"
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    name: Mapped[str] = mapped_column(String)


class AiCache(Base):
    __tablename__ = "ai_cache"
    hash: Mapped[str] = mapped_column(String, primary_key=True)
    model: Mapped[str] = mapped_column(String)
    result: Mapped[dict] = mapped_column(JsonType)
    created_at: Mapped[datetime] = _ts()


class OutboxMessage(Base):
    __tablename__ = "outbox_messages"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    buyer_id: Mapped[str] = mapped_column(ForeignKey("buyers.id"))
    subject: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(Text)
    warning_id: Mapped[str | None] = mapped_column(ForeignKey("warnings.id"))
    created_at: Mapped[datetime] = _ts()


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    actor_id: Mapped[str | None] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    entity: Mapped[str] = mapped_column(String)
    entity_id: Mapped[str] = mapped_column(String)
    meta: Mapped[dict] = mapped_column(JsonType, default=dict)
    at: Mapped[datetime] = _ts()


class RateLimit(Base):
    __tablename__ = "rate_limits"
    key: Mapped[str] = mapped_column(String, primary_key=True)
    count: Mapped[int] = mapped_column(BigInteger, default=0)
    window_start: Mapped[datetime] = _ts()
