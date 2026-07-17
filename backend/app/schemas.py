from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


# ── SalesRep ──────────────────────────────────────────────────────────────────

class SalesRepBase(BaseModel):
    name: str
    email: str
    territory: Optional[str] = None


class SalesRepCreate(SalesRepBase):
    pass


class SalesRepOut(SalesRepBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Client ────────────────────────────────────────────────────────────────────

class ClientBase(BaseModel):
    company_name: str
    industry: Optional[str] = None
    website: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientOut(ClientBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Account ───────────────────────────────────────────────────────────────────

class AccountBase(BaseModel):
    account_name: str
    stage: Optional[str] = "discovery"
    notes: Optional[str] = None


class AccountCreate(AccountBase):
    sales_rep_id: UUID
    client_id: UUID


class AccountOut(AccountBase):
    id: UUID
    sales_rep_id: UUID
    client_id: UUID
    created_at: datetime
    updated_at: datetime
    client: Optional[ClientOut] = None
    sales_rep: Optional[SalesRepOut] = None

    model_config = {"from_attributes": True}


# ── Transcript ────────────────────────────────────────────────────────────────

class TranscriptBase(BaseModel):
    title: str
    meeting_date: datetime
    raw_text: str


class TranscriptCreate(TranscriptBase):
    account_id: UUID
    sales_rep_id: UUID


class TranscriptOut(TranscriptBase):
    id: UUID
    account_id: UUID
    sales_rep_id: UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── ClientUpdate ──────────────────────────────────────────────────────────────

class ClientUpdateOut(BaseModel):
    id: UUID
    transcript_id: UUID
    category: str
    summary: str
    verbatim_quote: Optional[str] = None
    speaker: Optional[str] = None
    priority: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Opportunity ───────────────────────────────────────────────────────────────

class OpportunityOut(BaseModel):
    id: UUID
    transcript_id: UUID
    title: str
    description: str
    matched_product: Optional[str] = None
    matched_capability: Optional[str] = None
    confidence_score: float
    status: str
    agent_reasoning: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Agent ─────────────────────────────────────────────────────────────────────

class AnalyzeTranscriptRequest(BaseModel):
    transcript_id: UUID


class AnalyzeTranscriptResponse(BaseModel):
    transcript_id: UUID
    updates: list[ClientUpdateOut]
    opportunities: list[OpportunityOut]
    status: str
