# backend/tests/test_matching_engine.py

import pytest
from decimal import Decimal
from datetime import date, timedelta

from services.reconciliation.matching_engine import ReconciliationMatchingEngine
from services.reconciliation.types import Transaction, MatchStatus, MatchTier

@pytest.fixture
def sample_tally_ledgers():
    return [
        {"name": "Sharma Pvt Ltd", "gstin": "27AABCS1234M1Z5", "pan": "AABCS1234M"},
        {"name": "Mehta Traders", "gstin": "27AABCM5678N1Z3", "pan": "AABCM5678N"},
        {"name": "ABC Enterprises", "gstin": None, "pan": "AABCA9876P"},
    ]

@pytest.fixture
def sample_your_transactions():
    return [
        Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-2025-001",
            particulars="Sales to Sharma",
            debit=Decimal("25000"),
            credit=Decimal("0"),
            gstin="27AABCS1234M1Z5",
            source="tally"
        ),
        Transaction(
            id="y2",
            date=date(2026, 3, 18),
            reference="INV-2025-002",
            particulars="Sales to Mehta",
            debit=Decimal("15000"),
            credit=Decimal("0"),
            gstin="27AABCM5678N1Z3",
            source="tally"
        ),
    ]

@pytest.fixture
def sample_party_transactions():
    return [
        Transaction(
            id="p1",
            date=date(2026, 3, 15),
            reference="INV/2025/001",
            particulars="Purchase from you",
            debit=Decimal("0"),
            credit=Decimal("25000"),
            gstin="27AABCS1234M1Z5",
            source="party_statement"
        ),
        Transaction(
            id="p2",
            date=date(2026, 3, 20),  # 2 days difference
            reference="INV-2025-002",
            particulars="Purchase",
            debit=Decimal("0"),
            credit=Decimal("15000"),
            gstin="27AABCM5678N1Z3",
            source="party_statement"
        ),
    ]

def test_tier1_gstin_reference_match(sample_tally_ledgers, sample_your_transactions, sample_party_transactions):
    """Test highest confidence tier matching"""
    engine = ReconciliationMatchingEngine(sample_tally_ledgers)
    results, summary = engine.reconcile(
        sample_your_transactions,
        sample_party_transactions,
        {"name": "Sharma Pvt Ltd", "gstin": "27AABCS1234M1Z5"}
    )
    
    # First transaction should be exact GSTIN + reference match
    exact_matches = [r for r in results if r.tier == MatchTier.GSTIN_EXACT]
    assert len(exact_matches) >= 1
    assert exact_matches[0].confidence_score >= 0.95
    assert exact_matches[0].auto_postable == True

def test_tier4_date_tolerance(sample_tally_ledgers, sample_your_transactions, sample_party_transactions):
    """Test fuzzy date matching (±5 days)"""
    engine = ReconciliationMatchingEngine(sample_tally_ledgers)
    results, summary = engine.reconcile(
        sample_your_transactions,
        sample_party_transactions,
        {"name": "Mehta Traders"}
    )
    
    # Second transaction has 2-day difference
    fuzzy_matches = [r for r in results if r.tier == MatchTier.AMOUNT_DATE_FUZZY]
    assert len(fuzzy_matches) >= 1
    assert "timing_difference" in fuzzy_matches[0].flags

def test_tds_detection(sample_tally_ledgers):
    """Test TDS difference detection"""
    your_txn = Transaction(
        id="y1",
        date=date(2026, 3, 15),
        reference="INV-001",
        particulars="Professional fees",
        debit=Decimal("10000"),
        credit=Decimal("0"),
        source="tally"
    )
    
    party_txn = Transaction(
        id="p1",
        date=date(2026, 3, 15),
        reference="INV-001",
        particulars="Professional fees",
        debit=Decimal("0"),
        credit=Decimal("9000"),  # ₹1000 less (10% TDS)
        source="party_statement"
    )
    
    engine = ReconciliationMatchingEngine(sample_tally_ledgers)
    results, summary = engine.reconcile(
        [your_txn],
        [party_txn],
        {"name": "Test Party"}
    )
    
    # Should detect TDS
    assert len(results) == 1
    assert "tds_detected" in results[0].flags

def test_missing_in_party(sample_tally_ledgers, sample_your_transactions):
    """Test transactions missing in party statement"""
    engine = ReconciliationMatchingEngine(sample_tally_ledgers)
    results, summary = engine.reconcile(
        sample_your_transactions,
        [],  # Empty party statement
        {"name": "Test Party"}
    )
    
    missing = [r for r in results if r.status == MatchStatus.MISSING_IN_PARTY]
    assert len(missing) == 2
    assert summary.missing_in_party_count == 2

def test_reference_normalization():
    """Test reference number normalization"""
    engine = ReconciliationMatchingEngine([])
    
    # These should all match
    assert engine._references_match("INV-001", "INV/001") == True
    assert engine._references_match("INV-2025-001", "INV/2025/001") == True
    assert engine._references_match("001", "INV-001") == True
    assert engine._references_match("INV-001", "INV-002") == False

def test_party_name_matching():
    """Test fuzzy party name matching"""
    ledgers = [
        {"name": "Sharma Private Limited", "gstin": "27AABCS1234M1Z5"},
        {"name": "ABC & Co. Traders", "gstin": None},
    ]
    
    matcher = PartyMatcher(ledgers)
    
    # Should match despite variations
    ledger, method, confidence = matcher.match({"name": "Sharma Pvt Ltd"})
    assert ledger is not None
    assert confidence >= 0.85
    
    ledger, method, confidence = matcher.match({"name": "ABC and Company Traders"})
    assert ledger is not None
    assert confidence >= 0.70
