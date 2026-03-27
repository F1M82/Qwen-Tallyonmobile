# backend/services/reconciliation/types.py

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import date
from decimal import Decimal
from enum import Enum

class MatchStatus(str, Enum):
    EXACT = "exact"
    FUZZY = "fuzzy"
    AMOUNT_ONLY = "amount_only"
    MISSING_IN_PARTY = "missing_in_party"
    MISSING_IN_BOOKS = "missing_in_books"
    AMOUNT_MISMATCH = "amount_mismatch"
    PENDING_REVIEW = "pending_review"

class MatchTier(str, Enum):
    GSTIN_EXACT = "gstin_exact"
    REFERENCE_EXACT = "reference_exact"
    AMOUNT_DATE_EXACT = "amount_date_exact"
    AMOUNT_DATE_FUZZY = "amount_date_fuzzy"
    AMOUNT_ONLY = "amount_only"
    MANUAL_REVIEW = "manual_review"

class Transaction(BaseModel):
    """Normalized transaction from any source (Tally, Excel, PDF)"""
    id: str
    date: date
    reference: Optional[str] = None  # Invoice no, UTR, Cheque no
    particulars: str
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    balance: Optional[Decimal] = None
    balance_type: Optional[Literal["Dr", "Cr"]] = None
    gstin: Optional[str] = None  # Critical for party matching
    pan: Optional[str] = None
    voucher_type: Optional[str] = None
    source: str  # "tally" | "party_statement"
    metadata: dict = Field(default_factory=dict)  # Extra info for audit
    
    @property
    def amount(self) -> Decimal:
        return self.debit if self.debit > 0 else self.credit
    
    @property
    def entry_type(self) -> Literal["Dr", "Cr"]:
        return "Dr" if self.debit > 0 else "Cr"

class MatchResult(BaseModel):
    """Single match result with full audit trail"""
    id: str
    your_transaction: Optional[Transaction] = None
    party_transaction: Optional[Transaction] = None
    status: MatchStatus
    tier: MatchTier
    confidence_score: float = Field(ge=0.0, le=1.0)
    difference: Decimal = Decimal("0")
    reason: str
    flags: List[str] = Field(default_factory=list)  # TDS, timing, duplicate etc.
    suggested_action: str
    requires_review: bool = True
    auto_postable: bool = False
    created_at: str
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }

class ReconciliationSummary(BaseModel):
    """High-level summary for UI"""
    recon_id: str
    party_name: str
    period_from: date
    period_to: date
    your_balance: Decimal
    party_balance: Decimal
    total_difference: Decimal
    matched_count: int
    matched_amount: Decimal
    fuzzy_count: int
    fuzzy_amount: Decimal
    missing_in_party_count: int
    missing_in_party_amount: Decimal
    missing_in_books_count: int
    missing_in_books_amount: Decimal
    mismatch_count: int
    mismatch_amount: Decimal
    auto_postable_count: int
    requires_review_count: int
    status: Literal["processing", "completed", "partial"]
    certificate_generated: bool = False
