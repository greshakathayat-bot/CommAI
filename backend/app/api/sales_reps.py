from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/sales-reps", tags=["Sales Reps"])


@router.get("/", response_model=list[schemas.SalesRepOut])
def list_sales_reps(db: Session = Depends(get_db)):
    return db.query(models.SalesRep).all()


@router.get("/{rep_id}", response_model=schemas.SalesRepOut)
def get_sales_rep(rep_id: str, db: Session = Depends(get_db)):
    rep = db.query(models.SalesRep).filter(models.SalesRep.id == rep_id).first()
    if not rep:
        raise HTTPException(status_code=404, detail="Sales rep not found")
    return rep


@router.post("/", response_model=schemas.SalesRepOut, status_code=201)
def create_sales_rep(payload: schemas.SalesRepCreate, db: Session = Depends(get_db)):
    rep = models.SalesRep(**payload.model_dump())
    db.add(rep)
    db.commit()
    db.refresh(rep)
    return rep
