"""Vouchers router — CRUD for accounting vouchers"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from decimal import Decimal

from database import get_db
from models import Voucher, VoucherStatus
from routers.auth import get_current_user, User

router = APIRouter()


class VoucherCreate(BaseModel):
    voucher_type: str
    date: date
    narration: Optional[str] = None
    reference: Optional[str] = None
    total_amount: Decimal
    source: Optional[str] = "manual"
    company_id: str


class VoucherOut(BaseModel):
    id: str
    voucher_type: str
    voucher_number: Optional[str]
    date: date
    narration: Optional[str]
    reference: Optional[str]
    total_amount: Decimal
    status: VoucherStatus
    source: Optional[str]
    created_at: date

    class Config:
        from_attributes = True


@router.get("/", response_model=List[VoucherOut])
def list_vouchers(
    company_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Voucher)
    if company_id:
        query = query.filter(Voucher.company_id == company_id)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=VoucherOut, status_code=status.HTTP_201_CREATED)
def create_voucher(
    data: VoucherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    voucher = Voucher(
        **data.model_dump(),
        created_by=current_user.id,
        status=VoucherStatus.POSTED,
    )
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    return voucher


@router.get("/{voucher_id}", response_model=VoucherOut)
def get_voucher(
    voucher_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return voucher


@router.put("/{voucher_id}", response_model=VoucherOut)
def update_voucher(
    voucher_id: str,
    data: VoucherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    for key, value in data.model_dump().items():
        setattr(voucher, key, value)
    db.commit()
    db.refresh(voucher)
    return voucher


@router.delete("/{voucher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_voucher(
    voucher_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    voucher.status = VoucherStatus.CANCELLED
    db.commit()
