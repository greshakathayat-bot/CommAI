import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db, SessionLocal
from app.agent.analyzer import analyze_transcript

router = APIRouter(prefix="/agent", tags=["Agent"])
logger = logging.getLogger(__name__)


async def _run_analysis(transcript_id: str):
    """Background task: run AI analysis and persist results."""
    db: Session = SessionLocal()
    try:
        transcript = db.query(models.Transcript).filter(models.Transcript.id == transcript_id).first()
        if not transcript:
            return

        transcript.status = models.TranscriptStatus.processing
        db.commit()

        try:
            result = await analyze_transcript(transcript.raw_text)

            # Persist extracted updates
            for u in result.get("updates", []):
                update = models.ClientUpdate(
                    transcript_id=transcript.id,
                    category=u.get("category", "context"),
                    summary=u.get("summary", ""),
                    verbatim_quote=u.get("verbatim_quote"),
                    speaker=u.get("speaker"),
                    priority=u.get("priority", "medium"),
                )
                db.add(update)

            # Persist opportunities
            for o in result.get("opportunities", []):
                opp = models.Opportunity(
                    transcript_id=transcript.id,
                    title=o.get("title", "Untitled Opportunity"),
                    description=o.get("description", ""),
                    matched_product=o.get("matched_product"),
                    matched_capability=o.get("matched_capability"),
                    confidence_score=float(o.get("confidence_score", 0.0)),
                    agent_reasoning=o.get("agent_reasoning"),
                )
                db.add(opp)

            transcript.status = models.TranscriptStatus.completed
            db.commit()
            logger.info("Analysis complete for transcript %s", transcript_id)

        except Exception as exc:
            logger.error("Analysis failed for transcript %s: %s", transcript_id, exc)
            transcript.status = models.TranscriptStatus.failed
            db.commit()
    finally:
        db.close()


@router.post("/analyze", response_model=dict)
async def trigger_analysis(
    payload: schemas.AnalyzeTranscriptRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger AI analysis of a transcript (runs asynchronously)."""
    transcript_id = str(payload.transcript_id)
    transcript = db.query(models.Transcript).filter(models.Transcript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    if transcript.status == models.TranscriptStatus.processing:
        return {"message": "Analysis already in progress", "transcript_id": transcript_id}

    background_tasks.add_task(_run_analysis, transcript_id)
    return {"message": "Analysis started", "transcript_id": transcript_id}


@router.get("/opportunities", response_model=list[schemas.OpportunityOut])
def list_all_opportunities(db: Session = Depends(get_db)):
    """Return all opportunities across all transcripts."""
    return (
        db.query(models.Opportunity)
        .order_by(models.Opportunity.confidence_score.desc())
        .all()
    )
