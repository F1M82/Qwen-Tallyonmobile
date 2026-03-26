# FILE: backend/routers/message_parser.py
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import anthropic
import json
import re
from datetime import datetime
from config import settings

router = APIRouter()

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None

SMS_PARSE_PROMPT = """
You are an Indian bank message parser for accounting software.
Parse this bank/UPI message and extract payment details.
Return ONLY valid JSON.

Message: "{message}"
Source: "{source}"

Return:
{{
    "is_financial": true/false,
    "transaction_type": "credit" | "debit",
    "voucher_type": "Receipt" | "Payment",
    "amount": 0.00,
    "currency": "INR",
    "payment_rail": "UPI" | "NEFT" | "RTGS" | "IMPS",
    "utr_reference": "",
    "counterparty_name": "",
    "bank_name": "",
    "transaction_date": "DD-MM-YYYY",
    "confidence": 0.0
}}

Rules:
- credit = money IN = Receipt voucher
- debit = money OUT = Payment voucher
- Extract exact amount
- confidence: 0.0-1.0
- Return ONLY JSON
"""

class ParsedMessage(BaseModel):
    is_financial: bool
    transaction_type: Optional[str]
    voucher_type: Optional[str]
    amount: Optional[float]
    counterparty_name: Optional[str]
    utr_reference: Optional[str]
    payment_rail: Optional[str]
    confidence: float
    raw_message: str

@router.post("/parse/sms", response_model=ParsedMessage)
async def parse_sms_message(message: str, source: str = "SMS"):
    if not client:
        raise HTTPException(500, "AI API not configured")
    
    # Quick regex pre-filter (zero AI cost)
    financial_keywords = ["credited", "debited", "neft", "rtgs", "imps", "upi"]
    if not any(kw in message.lower() for kw in financial_keywords):
        return ParsedMessage(
            is_financial=False,
            confidence=0.0,
            raw_message=message
        )
    
    # Extract amount with regex
    amount_match = re.search(r'Rs\.?[\s]?(\d+[,\d]*(\.\d+)?)|INR[\s]?(\d+[,\d]*(\.\d+)?)', message, re.I)
    amount = float(amount_match.group(1).replace(',', '')) if amount_match else 0.0
    
    # Send to Claude for full parsing
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": SMS_PARSE_PROMPT.format(message=message, source=source)
            }]
        )
        
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        
        parsed = json.loads(raw.strip())
        
        return ParsedMessage(
            is_financial=parsed.get("is_financial", False),
            transaction_type=parsed.get("transaction_type"),
            voucher_type=parsed.get("voucher_type"),
            amount=parsed.get("amount", amount),
            counterparty_name=parsed.get("counterparty_name"),
            utr_reference=parsed.get("utr_reference"),
            payment_rail=parsed.get("payment_rail"),
            confidence=parsed.get("confidence", 0.5),
            raw_message=message
        )
    
    except Exception as e:
        raise HTTPException(500, f"AI parsing failed: {str(e)}")

@router.post("/parse/email")
async def parse_email(subject: str, body: str, has_attachment: bool = False):
    # Similar to SMS but for email
    pass
"""
