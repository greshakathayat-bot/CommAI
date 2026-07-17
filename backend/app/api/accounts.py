from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("/", response_model=list[schemas.AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return (
        db.query(models.Account)
        .options(joinedload(models.Account.client), joinedload(models.Account.sales_rep))
        .all()
    )


@router.get("/{account_id}", response_model=schemas.AccountOut)
def get_account(account_id: str, db: Session = Depends(get_db)):
    account = (
        db.query(models.Account)
        .options(joinedload(models.Account.client), joinedload(models.Account.sales_rep))
        .filter(models.Account.id == account_id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("/", response_model=schemas.AccountOut, status_code=201)
def create_account(payload: schemas.AccountCreate, db: Session = Depends(get_db)):
    account = models.Account(**payload.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account
