"""Message parser router — parse SMS/email payment notifications"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import re

from routers.auth import get_current_user, User

router = APIRouter()


class SMSParseRequest(BaseModel):
    message: str
    source: str = "sms"  # sms, email, whatsapp


class ParsedPayment(BaseModel):
    detected: bool
    transaction_type: Optional[str]  # credit, debit
    amount: Optional[float]
    utr_number: Optional[str]
    bank_name: Optional[str]
    account_last4: Optional[str]
    date: Optional[str]
    sender_name: Optional[str]
    raw_message: str


@router.post("/parse/sms", response_model=ParsedPayment)
def parse_sms(
    body: SMSParseRequest,
    current_user: User = Depends(get_current_user),
):
    """Parse SMS/UPI payment notification into structured data"""
    msg = body.message
    result = _parse_payment_message(msg)
    return result


def _parse_payment_message(msg: str) -> ParsedPayment:
    """Regex-based payment SMS parser"""
    # Amount patterns: Rs. 50,000 | INR 50000 | ₹50,000
    amount_match = re.search(
        r"(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d{1,2})?)", msg, re.IGNORECASE
    )
    amount = float(amount_match.group(1).replace(",", "")) if amount_match else None

    # UTR / Reference
    utr_match = re.search(r"(?:UTR|Ref(?:erence)?(?:\s+No)?)[:\s]*([A-Z0-9]+)", msg, re.IGNORECASE)
    utr = utr_match.group(1) if utr_match else None

    # Transaction type
    tx_type = None
    if re.search(r"\b(credited|received|credit)\b", msg, re.IGNORECASE):
        tx_type = "credit"
    elif re.search(r"\b(debited|sent|debit|paid)\b", msg, re.IGNORECASE):
        tx_type = "debit"

    # Date
    date_match = re.search(r"\d{2}[-/]\d{2}[-/]\d{4}", msg)
    date_str = date_match.group(0) if date_match else None

    return ParsedPayment(
        detected=amount is not None,
        transaction_type=tx_type,
        amount=amount,
        utr_number=utr,
        bank_name=None,
        account_last4=None,
        date=date_str,
        sender_name=None,
        raw_message=msg,
    )
