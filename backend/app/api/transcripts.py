from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/transcripts", tags=["Transcripts"])


@router.get("/", response_model=list[schemas.TranscriptOut])
def list_transcripts(account_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Transcript)
    if account_id:
        query = query.filter(models.Transcript.account_id == account_id)
    return query.order_by(models.Transcript.meeting_date.desc()).all()


@router.get("/{transcript_id}", response_model=schemas.TranscriptOut)
def get_transcript(transcript_id: str, db: Session = Depends(get_db)):
    t = db.query(models.Transcript).filter(models.Transcript.id == transcript_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return t


@router.get("/{transcript_id}/updates", response_model=list[schemas.ClientUpdateOut])
def get_transcript_updates(transcript_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.ClientUpdate)
        .filter(models.ClientUpdate.transcript_id == transcript_id)
        .all()
    )


@router.get("/{transcript_id}/opportunities", response_model=list[schemas.OpportunityOut])
def get_transcript_opportunities(transcript_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.Opportunity)
        .filter(models.Opportunity.transcript_id == transcript_id)
        .all()
    )


@router.post("/", response_model=schemas.TranscriptOut, status_code=201)
def create_transcript(payload: schemas.TranscriptCreate, db: Session = Depends(get_db)):
    transcript = models.Transcript(**payload.model_dump())
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript
