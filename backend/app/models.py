import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    Integer,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class SalesRep(Base):
    """A member of the sales team."""

    __tablename__ = "sales_reps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    territory = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    accounts = relationship("Account", back_populates="sales_rep")
    transcripts = relationship("Transcript", back_populates="sales_rep")


class Client(Base):
    """An external client organization."""

    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100))
    website = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)

    accounts = relationship("Account", back_populates="client")


class Account(Base):
    """The relationship between a sales rep and a client."""

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_rep_id = Column(UUID(as_uuid=True), ForeignKey("sales_reps.id"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    account_name = Column(String(200), nullable=False)
    stage = Column(String(80), default="discovery")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sales_rep = relationship("SalesRep", back_populates="accounts")
    client = relationship("Client", back_populates="accounts")
    transcripts = relationship("Transcript", back_populates="account")


class TranscriptStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Transcript(Base):
    """A meeting audio transcript."""

    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    sales_rep_id = Column(UUID(as_uuid=True), ForeignKey("sales_reps.id"), nullable=False)
    title = Column(String(300), nullable=False)
    meeting_date = Column(DateTime, nullable=False)
    raw_text = Column(Text, nullable=False)
    status = Column(SAEnum(TranscriptStatus), default=TranscriptStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="transcripts")
    sales_rep = relationship("SalesRep", back_populates="transcripts")
    updates = relationship("ClientUpdate", back_populates="transcript", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="transcript", cascade="all, delete-orphan")


class UpdateCategory(str, enum.Enum):
    requirement = "requirement"
    feedback = "feedback"
    blocker = "blocker"
    action_item = "action_item"
    context = "context"


class ClientUpdate(Base):
    """An extracted update/requirement from a transcript."""

    __tablename__ = "client_updates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcripts.id"), nullable=False)
    category = Column(SAEnum(UpdateCategory), nullable=False)
    summary = Column(Text, nullable=False)
    verbatim_quote = Column(Text)
    speaker = Column(String(120))
    priority = Column(String(20), default="medium")  # low / medium / high
    created_at = Column(DateTime, default=datetime.utcnow)

    transcript = relationship("Transcript", back_populates="updates")


class OpportunityStatus(str, enum.Enum):
    identified = "identified"
    qualified = "qualified"
    proposed = "proposed"
    closed_won = "closed_won"
    closed_lost = "closed_lost"


class Opportunity(Base):
    """A matched solution opportunity identified by the AI agent."""

    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcripts.id"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    matched_product = Column(String(200))
    matched_capability = Column(Text)
    confidence_score = Column(Float, default=0.0)
    status = Column(SAEnum(OpportunityStatus), default=OpportunityStatus.identified)
    agent_reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    transcript = relationship("Transcript", back_populates="opportunities")
