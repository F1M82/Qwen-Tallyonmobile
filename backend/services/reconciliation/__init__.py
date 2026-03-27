"""
TaxMind Reconciliation Engine
=============================

Production-grade debtor/creditor reconciliation module for Indian CA firms.

Features:
- GSTIN-first party matching
- 6-tier transaction matching logic
- Partial payment detection (one-to-many, many-to-one)
- TDS, timing difference, duplicate detection
- Confidence scoring for auto-post decisions
- Audit trail ready

Usage:
    from services.reconciliation import ReconciliationMatchingEngine
    from services.reconciliation import Transaction, MatchResult, MatchStatus
    
    engine = ReconciliationMatchingEngine(tally_ledgers)
    results, summary = engine.reconcile(your_transactions, party_transactions, party_info)
"""

from .types import (
    Transaction,
    MatchResult,
    MatchStatus,
    MatchTier,
    ReconciliationSummary,
    ReconSession,
    PartyInfo,
)

from .party_matcher import PartyMatcher

from .confidence_scorer import ConfidenceScorer

from .edge_cases import EdgeCaseDetector

from .partial_payment_matcher import PartialPaymentMatcher, PartialMatchGroup

from .matching_engine import ReconciliationMatchingEngine

from .excel_parser import parse_excel_statement, normalize_excel_columns

from .pdf_extractor import extract_pdf_ledger

from .certificate_generator import generate_reconciliation_certificate

# Public API - what gets imported when someone does:
# from services.reconciliation import *
__all__ = [
    # Core Engine
    "ReconciliationMatchingEngine",
    
    # Data Models
    "Transaction",
    "MatchResult",
    "MatchStatus",
    "MatchTier",
    "ReconciliationSummary",
    "ReconSession",
    "PartyInfo",
    
    # Matching Components
    "PartyMatcher",
    "ConfidenceScorer",
    "EdgeCaseDetector",
    "PartialPaymentMatcher",
    "PartialMatchGroup",
    
    # Document Processing
    "parse_excel_statement",
    "normalize_excel_columns",
    "extract_pdf_ledger",
    
    # Output Generation
    "generate_reconciliation_certificate",
]

# Version info
__version__ = "1.0.0"
__author__ = "TaxMind Platform"

# Quick validation on import
def _validate_imports():
    """Ensure all critical components are importable"""
    try:
        engine = ReconciliationMatchingEngine([])
        assert hasattr(engine, 'reconcile')
        assert hasattr(engine, 'party_matcher')
        assert hasattr(engine, 'confidence_scorer')
        return True
    except Exception as e:
        print(f"⚠️  Reconciliation module validation failed: {e}")
        return False

# Run validation on first import
_validation_passed = _validate_imports()
