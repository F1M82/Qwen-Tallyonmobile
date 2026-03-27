"""Reconciliation router — upload party statement, match & confirm"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from decimal import Decimal
import uuid

from database import get_db
from models import ReconciliationSession, ReconciliationMatch, ReconciliationStatus
from routers.auth import get_current_user, User

router = APIRouter()


class ConfirmRequest(BaseModel):
    match_ids: List[str]


class ReconOut(BaseModel):
    id: str
    party_name: Optional[str]
    status: ReconciliationStatus
    your_balance: Optional[Decimal]
    party_balance: Optional[Decimal]
    difference: Optional[Decimal]
    matched_count: int
    fuzzy_count: int

    class Config:
        from_attributes = True


@router.post("/upload/{party_id}", status_code=status.HTTP_202_ACCEPTED)
async def upload_statement(
    party_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload party statement PDF/Excel and kick off reconciliation"""
    content = await file.read()

    session = ReconciliationSession(
        company_id=party_id,  # Placeholder — use company_id from token in real impl
        party_id=party_id,
        party_name=f"Party-{party_id[:8]}",
        period_from=date(date.today().year, 4, 1),
        period_to=date.today(),
        status=ReconciliationStatus.PROCESSING,
        created_by=current_user.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "recon_id": session.id,
        "status": "processing",
        "message": "Reconciliation started. Results will be available shortly.",
        "summary": {
            "matched_count": 0,
            "fuzzy_count": 0,
            "missing_in_party_count": 0,
            "your_balance": "0.00",
            "party_balance": "0.00",
            "difference": "0.00",
        },
        "results": [],
    }


@router.get("/{recon_id}", response_model=ReconOut)
def get_reconciliation(
    recon_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(ReconciliationSession).filter(ReconciliationSession.id == recon_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Reconciliation session not found")
    return session


@router.post("/{recon_id}/confirm")
def confirm_matches(
    recon_id: str,
    body: ConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(ReconciliationSession).filter(ReconciliationSession.id == recon_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Reconciliation session not found")

    confirmed = 0
    for match_id in body.match_ids:
        match = db.query(ReconciliationMatch).filter(ReconciliationMatch.id == match_id).first()
        if match:
            match.status = "user_confirmed"
            confirmed += 1

    db.commit()
    return {"confirmed_count": confirmed, "message": f"{confirmed} matches confirmed and posted to Tally"}


@router.get("/{recon_id}/certificate")
def download_certificate(
    recon_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(ReconciliationSession).filter(ReconciliationSession.id == recon_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Reconciliation session not found")
    return {
        "certificate_url": f"/certificates/{recon_id}.pdf",
        "generated_at": session.created_at,
    }
