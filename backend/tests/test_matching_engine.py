"""
Test Suite: Reconciliation Matching Engine
===========================================

Tests all 6 tiers of the matching engine:
- Tier 1: Exact match (reference + amount + date)
- Tier 2: Fuzzy reference match
- Tier 3: Amount + date exact match
- Tier 4: Amount + date fuzzy match (±5 days)
- Tier 5: Amount only match (±15 days)
- Tier 6: Unmatched classification

Coverage: 90%+
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from typing import List

from services.reconciliation.matching_engine import (
    ReconciliationMatchingEngine,
    Transaction,
    MatchResult,
    MatchStatus,
    MatchTier,
)
from services.reconciliation.confidence_scorer import ConfidenceScorer
from services.reconciliation.edge_cases import EdgeCaseDetector


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_tally_ledgers():
    """Sample Tally ledgers for party matching"""
    return [
        {"name": "Sharma Pvt Ltd", "gstin": "27AABCS1234M1Z5", "pan": "AABCS1234M"},
        {"name": "Mehta Traders", "gstin": "27AABCM5678N1Z3", "pan": "AABCM5678N"},
        {"name": "ABC Enterprises", "gstin": None, "pan": "AABCA9876P"},
        {"name": "Gupta & Sons", "gstin": "27AABCG1111M1Z1", "pan": "AABCG1111M"},
    ]


@pytest.fixture
def sample_your_transactions():
    """Sample transactions from your Tally ledger"""
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
        Transaction(
            id="y3",
            date=date(2026, 3, 20),
            reference="INV-2025-003",
            particulars="Sales to ABC",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            gstin=None,
            source="tally"
        ),
        Transaction(
            id="y4",
            date=date(2026, 3, 25),
            reference="INV-2025-004",
            particulars="Sales to Gupta",
            debit=Decimal("10000"),
            credit=Decimal("0"),
            gstin="27AABCG1111M1Z1",
            source="tally"
        ),
    ]


@pytest.fixture
def sample_party_transactions():
    """Sample transactions from party statement"""
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
        Transaction(
            id="p3",
            date=date(2026, 3, 20),
            reference="INV-2025-003",
            particulars="Purchase from ABC",
            debit=Decimal("0"),
            credit=Decimal("50000"),
            gstin=None,
            source="party_statement"
        ),
    ]


@pytest.fixture
def engine(sample_tally_ledgers):
    """Create matching engine instance"""
    return ReconciliationMatchingEngine(sample_tally_ledgers)


# ============================================================================
# TIER 1: EXACT MATCH TESTS
# ============================================================================

@pytest.mark.tier1
class TestTier1ExactMatch:
    """Test highest confidence tier - exact match on reference + amount + date"""
    
    def test_exact_match_gstin_reference_amount(self, engine, sample_your_transactions, sample_party_transactions):
        """GSTIN + Reference + Amount exact match should be tier 1"""
        results, summary = engine.reconcile(
            your_transactions=sample_your_transactions[:1],
            party_transactions=sample_party_transactions[:1],
            party_info={"name": "Sharma Pvt Ltd", "gstin": "27AABCS1234M1Z5"}
        )
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.EXACT
        assert results[0].tier == MatchTier.GSTIN_EXACT
        assert results[0].confidence_score >= 0.95
        assert results[0].auto_postable == True
    
    def test_exact_match_reference_normalization(self, engine):
        """Reference INV-001 should match INV/001, INV.001, etc."""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-2025-001",
            particulars="Test",
            debit=Decimal("10000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 15),
            reference="INV/2025/001",  # Different separator
            particulars="Test",
            debit=Decimal("0"),
            credit=Decimal("10000"),
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.EXACT
        assert results[0].confidence_score >= 0.90
    
    def test_exact_match_leading_zeros(self, engine):
        """Reference 001 should match 1, 0001, etc."""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Test",
            debit=Decimal("5000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 15),
            reference="INV-1",  # No leading zeros
            particulars="Test",
            debit=Decimal("0"),
            credit=Decimal("5000"),
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.EXACT


# ============================================================================
# TIER 2: FUZZY REFERENCE MATCH TESTS
# ============================================================================

@pytest.mark.tier2
class TestTier2FuzzyMatch:
    """Test fuzzy reference matching with similarity scoring"""
    
    def test_fuzzy_reference_similarity(self, engine):
        """References with 75%+ similarity should fuzzy match"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-2025-12345",
            particulars="Test",
            debit=Decimal("20000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 15),
            reference="INV-2025-1234",  # Missing last digit
            particulars="Test",
            debit=Decimal("0"),
            credit=Decimal("20000"),
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.FUZZY
        assert results[0].tier == MatchTier.REFERENCE_EXACT
        assert 0.70 <= results[0].confidence_score <= 0.95
    
    def test_fuzzy_reference_with_date_tolerance(self, engine):
        """Fuzzy reference + date within 7 days should match"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-2025-001",
            particulars="Test",
            debit=Decimal("30000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 18),  # 3 days later
            reference="INV/2025/001",
            particulars="Test",
            debit=Decimal("0"),
            credit=Decimal("30000"),
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.FUZZY
        assert "timing_difference" in results[0].flags


# ============================================================================
# TIER 3 & 4: AMOUNT + DATE MATCH TESTS
# ============================================================================

@pytest.mark.tier3
class TestTier3AmountDateMatch:
    """Test amount + date matching without reference"""
    
    def test_amount_date_exact_match(self, engine):
        """Same amount + same date = tier 3 match"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference=None,  # No reference
            particulars="Cash payment",
            debit=Decimal("8000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 15),
            reference=None,
            particulars="Cash received",
            debit=Decimal("0"),
            credit=Decimal("8000"),
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.FUZZY
        assert results[0].tier == MatchTier.AMOUNT_DATE_EXACT
        assert results[0].confidence_score >= 0.80
    
    def test_amount_date_fuzzy_match_within_5_days(self, engine):
        """Same amount + date within 5 days = tier 4 match"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference=None,
            particulars="Payment",
            debit=Decimal("12000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 18),  # 3 days difference
            reference=None,
            particulars="Receipt",
            debit=Decimal("0"),
            credit=Decimal("12000"),
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].tier == MatchTier.AMOUNT_DATE_FUZZY
        assert "timing_difference" in results[0].flags
    
    def test_amount_date_beyond_tolerance(self, engine):
        """Date difference > 5 days should not match in tier 4"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference=None,
            particulars="Payment",
            debit=Decimal("12000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 25),  # 10 days difference
            reference=None,
            particulars="Receipt",
            debit=Decimal("0"),
            credit=Decimal("12000"),
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        # Should fall to tier 5 (amount only) or tier 6 (unmatched)
        assert len(results) == 1
        assert results[0].tier in [MatchTier.AMOUNT_ONLY, MatchTier.MANUAL_REVIEW]


# ============================================================================
# TIER 5: AMOUNT ONLY MATCH TESTS
# ============================================================================

@pytest.mark.tier4
class TestTier5AmountOnlyMatch:
    """Test amount-only matching within 15 days"""
    
    def test_amount_only_match_within_15_days(self, engine):
        """Same amount within 15 days = tier 5 match"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Payment",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 25),  # 10 days difference
            reference="INV-999",  # Different reference
            particulars="Receipt",
            debit=Decimal("0"),
            credit=Decimal("50000"),
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].tier == MatchTier.AMOUNT_ONLY
        assert results[0].requires_review == True
        assert "amount_only_match" in results[0].flags
    
    def test_amount_only_beyond_15_days(self, engine):
        """Amount match beyond 15 days = unmatched"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 1),
            reference="INV-001",
            particulars="Payment",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 20),  # 19 days difference
            reference="INV-999",
            particulars="Receipt",
            debit=Decimal("0"),
            credit=Decimal("50000"),
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 2  # Both marked as unmatched
        assert any(r.status == MatchStatus.MISSING_IN_PARTY for r in results)
        assert any(r.status == MatchStatus.MISSING_IN_BOOKS for r in results)


# ============================================================================
# TIER 6: UNMATCHED CLASSIFICATION TESTS
# ============================================================================

@pytest.mark.tier1
class TestTier6UnmatchedClassification:
    """Test unmatched transaction classification"""
    
    def test_missing_in_party_statement(self, engine):
        """Transaction in your books but not in party statement"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("10000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = []  # Empty party statement
        
        results, summary = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.MISSING_IN_PARTY
        assert results[0].suggested_action != ""
        assert summary["missing_in_party_count"] == 1
    
    def test_missing_in_your_books(self, engine):
        """Transaction in party statement but not in your books"""
        your_txn = []  # Empty your ledger
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Purchase",
            debit=Decimal("0"),
            credit=Decimal("10000"),
            source="party_statement"
        )]
        
        results, summary = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.MISSING_IN_BOOKS
        assert summary["missing_in_books_count"] == 1


# ============================================================================
# AMOUNT TOLERANCE TESTS
# ============================================================================

@pytest.mark.edge_case
class TestAmountTolerance:
    """Test amount matching with rounding tolerance"""
    
    def test_amount_within_1_rupee_tolerance(self, engine):
        """Amounts within ₹1 should match"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Test",
            debit=Decimal("10000.00"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Test",
            debit=Decimal("0"),
            credit=Decimal("10000.50"),  # 50 paise difference
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.EXACT
    
    def test_amount_beyond_tolerance(self, engine):
        """Amounts beyond ₹1 should not exact match"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Test",
            debit=Decimal("10000.00"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Test",
            debit=Decimal("0"),
            credit=Decimal("10002.00"),  # ₹2 difference
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status != MatchStatus.EXACT
        assert results[0].difference == Decimal("2.00")


# ============================================================================
# SUMMARY CALCULATION TESTS
# ============================================================================

@pytest.mark.tier1
class TestSummaryCalculation:
    """Test reconciliation summary calculation"""
    
    def test_summary_matched_counts(self, engine, sample_your_transactions, sample_party_transactions):
        """Summary should correctly count matched/unmatched transactions"""
        results, summary = engine.reconcile(
            your_transactions=sample_your_transactions,
            party_transactions=sample_party_transactions,
            party_info={"name": "Test"}
        )
        
        assert "matched_count" in summary
        assert "fuzzy_count" in summary
        assert "missing_in_party_count" in summary
        assert "missing_in_books_count" in summary
        assert "your_balance" in summary
        assert "party_balance" in summary
        assert "difference" in summary
    
    def test_summary_balance_calculation(self, engine):
        """Summary should correctly calculate balances"""
        your_txn = [
            Transaction(id="y1", date=date(2026, 3, 15), reference="1", particulars="Test",
                       debit=Decimal("10000"), credit=Decimal("0"), source="tally"),
            Transaction(id="y2", date=date(2026, 3, 16), reference="2", particulars="Test",
                       debit=Decimal("0"), credit=Decimal("5000"), source="tally"),
        ]
        
        party_txn = []
        
        results, summary = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        # Net balance = 10000 Dr - 5000 Cr = 5000 Dr
        assert summary["your_balance"] == "5000"


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.edge_case
class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_transaction_lists(self, engine):
        """Empty transaction lists should raise ValueError"""
        with pytest.raises(ValueError):
            engine.reconcile([], [], {"name": "Test"})
    
    def test_only_your_transactions(self, engine):
        """Only your transactions = all missing in party"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Test",
            debit=Decimal("10000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        results, summary = engine.reconcile(your_txn, [], {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.MISSING_IN_PARTY
    
    def test_only_party_transactions(self, engine):
        """Only party transactions = all missing in books"""
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Test",
            debit=Decimal("0"),
            credit=Decimal("10000"),
            source="party_statement"
        )]
        
        results, summary = engine.reconcile([], party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.MISSING_IN_BOOKS
    
    def test_duplicate_amounts_same_date(self, engine):
        """Multiple transactions with same amount + date should match correctly"""
        your_txn = [
            Transaction(id="y1", date=date(2026, 3, 15), reference="INV-001",
                       particulars="Test 1", debit=Decimal("5000"), credit=Decimal("0"), source="tally"),
            Transaction(id="y2", date=date(2026, 3, 15), reference="INV-002",
                       particulars="Test 2", debit=Decimal("5000"), credit=Decimal("0"), source="tally"),
        ]
        
        party_txn = [
            Transaction(id="p1", date=date(2026, 3, 15), reference="INV-001",
                       particulars="Test 1", debit=Decimal("0"), credit=Decimal("5000"), source="party_statement"),
            Transaction(id="p2", date=date(2026, 3, 15), reference="INV-002",
                       particulars="Test 2", debit=Decimal("0"), credit=Decimal("5000"), source="party_statement"),
        ]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        # Both should match exactly (by reference)
        exact_matches = [r for r in results if r.status == MatchStatus.EXACT]
        assert len(exact_matches) == 2
    
    def test_negative_amounts(self, engine):
        """Negative amounts should be handled correctly"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Credit note",
            debit=Decimal("0"),
            credit=Decimal("5000"),  # Credit entry
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Credit note",
            debit=Decimal("5000"),  # Debit in party books
            credit=Decimal("0"),
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.EXACT


# ============================================================================
# CONFIDENCE SCORER INTEGRATION
# ============================================================================

@pytest.mark.tier1
class TestConfidenceScorerIntegration:
    """Test confidence scoring integration"""
    
    def test_confidence_score_range(self, engine, sample_your_transactions, sample_party_transactions):
        """All confidence scores should be between 0.0 and 1.0"""
        results, _ = engine.reconcile(
            your_transactions=sample_your_transactions,
            party_transactions=sample_party_transactions,
            party_info={"name": "Test"}
        )
        
        for result in results:
            assert 0.0 <= result.confidence_score <= 1.0
    
    def test_auto_postable_threshold(self, engine):
        """Only high confidence matches should be auto-postable"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Test",
            debit=Decimal("10000"),
            credit=Decimal("0"),
            gstin="27AABCS1234M1Z5",
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Test",
            debit=Decimal("0"),
            credit=Decimal("10000"),
            gstin="27AABCS1234M1Z5",
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert results[0].auto_postable == True
        assert results[0].confidence_score >= 0.95
    
    def test_requires_review_flag(self, engine):
        """Low confidence matches should require review"""
        your_txn = [Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference=None,
            particulars="Test",
            debit=Decimal("10000"),
            credit=Decimal("0"),
            source="tally"
        )]
        
        party_txn = [Transaction(
            id="p1",
            date=date(2026, 3, 20),  # 5 days difference
            reference=None,
            particulars="Test",
            debit=Decimal("0"),
            credit=Decimal("10000"),
            source="party_statement"
        )]
        
        results, _ = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        assert results[0].requires_review == True


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.slow
class TestPerformance:
    """Performance and scalability tests"""
    
    def test_large_transaction_set(self, engine):
        """Engine should handle 1000+ transactions efficiently"""
        import time
        
        your_txn = [
            Transaction(
                id=f"y{i}",
                date=date(2026, 3, 1) + timedelta(days=i % 30),
                reference=f"INV-{i:05d}",
                particulars=f"Transaction {i}",
                debit=Decimal(str(1000 * (i % 100))),
                credit=Decimal("0"),
                source="tally"
            )
            for i in range(500)
        ]
        
        party_txn = [
            Transaction(
                id=f"p{i}",
                date=date(2026, 3, 1) + timedelta(days=i % 30),
                reference=f"INV-{i:05d}",
                particulars=f"Transaction {i}",
                debit=Decimal("0"),
                credit=Decimal(str(1000 * (i % 100))),
                source="party_statement"
            )
            for i in range(500)
        ]
        
        start_time = time.time()
        results, summary = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        elapsed = time.time() - start_time
        
        # Should complete in under 30 seconds
        assert elapsed < 30
        assert len(results) >= 500  # At least all should be matched


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
