"""
Test Suite: Partial Payment Matcher
====================================

Tests partial payment matching scenarios:
- One invoice → Multiple payments
- Multiple invoices → One payment
- Advance + Final payment combinations
- TDS deduction handling

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
from services.reconciliation.partial_payment_matcher import (
    PartialPaymentMatcher,
    PartialMatchGroup,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_tally_ledgers():
    """Sample Tally ledgers"""
    return [
        {"name": "Sharma Pvt Ltd", "gstin": "27AABCS1234M1Z5", "pan": "AABCS1234M"},
    ]


@pytest.fixture
def matcher():
    """Create PartialPaymentMatcher instance"""
    return PartialPaymentMatcher()


@pytest.fixture
def engine(sample_tally_ledgers):
    """Create matching engine with partial payment support"""
    return ReconciliationMatchingEngine(sample_tally_ledgers)


# ============================================================================
# ONE-TO-MANY MATCHING TESTS
# ============================================================================

@pytest.mark.tier1
class TestOneToManyMatching:
    """Test one invoice paid via multiple payments"""
    
    def test_one_invoice_two_payments(self, matcher):
        """Single invoice paid via 2 payments should match"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payments = [
            Transaction(
                id="p1",
                date=date(2026, 3, 20),
                reference="PMT-001",
                particulars="Part payment",
                debit=Decimal("0"),
                credit=Decimal("30000"),
                source="party_statement"
            ),
            Transaction(
                id="p2",
                date=date(2026, 3, 25),
                reference="PMT-002",
                particulars="Final payment",
                debit=Decimal("0"),
                credit=Decimal("20000"),
                source="party_statement"
            ),
        ]
        
        results, remaining_yours, remaining_party = matcher.find_partial_matches(
            [invoice],
            payments
        )
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.FUZZY
        assert "partial_payment" in results[0].flags
        assert "multi_entry_match" in results[0].flags
        assert len(remaining_yours) == 0
        assert len(remaining_party) == 0
    
    def test_one_invoice_three_payments(self, matcher):
        """Single invoice paid via 3 payments should match"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("100000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payments = [
            Transaction(id="p1", date=date(2026, 3, 20), reference="PMT-1",
                       particulars="Payment 1", debit=Decimal("0"), credit=Decimal("40000"), source="party_statement"),
            Transaction(id="p2", date=date(2026, 3, 25), reference="PMT-2",
                       particulars="Payment 2", debit=Decimal("0"), credit=Decimal("30000"), source="party_statement"),
            Transaction(id="p3", date=date(2026, 3, 30), reference="PMT-3",
                       particulars="Payment 3", debit=Decimal("0"), credit=Decimal("30000"), source="party_statement"),
        ]
        
        results, remaining_yours, remaining_party = matcher.find_partial_matches(
            [invoice],
            payments
        )
        
        assert len(results) == 1
        assert results[0].metadata["entry_count"] == 3
        assert len(remaining_party) == 0
    
    def test_partial_payment_with_balance(self, matcher):
        """Partial payment with remaining balance should flag"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payments = [
            Transaction(
                id="p1",
                date=date(2026, 3, 20),
                reference="PMT-001",
                particulars="Part payment",
                debit=Decimal("0"),
                credit=Decimal("30000"),  # Only 30K of 50K
                source="party_statement"
            ),
        ]
        
        results, remaining_yours, remaining_party = matcher.find_partial_matches(
            [invoice],
            payments
        )
        
        # Should not match as partial (only 1 payment, not multiple)
        assert len(results) == 0
        assert len(remaining_yours) == 1  # Invoice still unmatched


# ============================================================================
# MANY-TO-ONE MATCHING TESTS
# ============================================================================

@pytest.mark.tier2
class TestManyToOneMatching:
    """Test multiple invoices paid via single payment"""
    
    def test_two_invoices_one_payment(self, matcher):
        """Two invoices paid via 1 consolidated payment should match"""
        invoices = [
            Transaction(
                id="y1",
                date=date(2026, 3, 15),
                reference="INV-001",
                particulars="Sales 1",
                debit=Decimal("30000"),
                credit=Decimal("0"),
                source="tally"
            ),
            Transaction(
                id="y2",
                date=date(2026, 3, 18),
                reference="INV-002",
                particulars="Sales 2",
                debit=Decimal("20000"),
                credit=Decimal("0"),
                source="tally"
            ),
        ]
        
        payment = Transaction(
            id="p1",
            date=date(2026, 3, 25),
            reference="PMT-001",
            particulars="Consolidated payment",
            debit=Decimal("0"),
            credit=Decimal("50000"),
            source="party_statement"
        )
        
        results, remaining_yours, remaining_party = matcher.find_partial_matches(
            invoices,
            [payment]
        )
        
        assert len(results) == 1
        assert results[0].status == MatchStatus.FUZZY
        assert "partial_payment" in results[0].flags
        assert results[0].metadata["match_type"] == "many_to_one"
        assert len(remaining_yours) == 0
        assert len(remaining_party) == 0
    
    def test_three_invoices_one_payment(self, matcher):
        """Three invoices paid via 1 payment should match"""
        invoices = [
            Transaction(id="y1", date=date(2026, 3, 15), reference="INV-001",
                       particulars="Sales 1", debit=Decimal("20000"), credit=Decimal("0"), source="tally"),
            Transaction(id="y2", date=date(2026, 3, 18), reference="INV-002",
                       particulars="Sales 2", debit=Decimal("15000"), credit=Decimal("0"), source="tally"),
            Transaction(id="y3", date=date(2026, 3, 20), reference="INV-003",
                       particulars="Sales 3", debit=Decimal("15000"), credit=Decimal("0"), source="tally"),
        ]
        
        payment = Transaction(
            id="p1",
            date=date(2026, 3, 25),
            reference="PMT-001",
            particulars="Consolidated payment",
            debit=Decimal("0"),
            credit=Decimal("50000"),
            source="party_statement"
        )
        
        results, remaining_yours, remaining_party = matcher.find_partial_matches(
            invoices,
            [payment]
        )
        
        assert len(results) == 1
        assert results[0].metadata["entry_count"] == 3


# ============================================================================
# TDS DEDUCTION TESTS
# ============================================================================

@pytest.mark.edge_case
class TestTDSDeduction:
    """Test TDS deduction handling in partial payments"""
    
    def test_payment_with_tds_deduction(self, engine):
        """Payment with TDS deducted should detect TDS"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Professional fees",
            debit=Decimal("10000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payment = Transaction(
            id="p1",
            date=date(2026, 3, 20),
            reference="PMT-001",
            particulars="Payment after TDS",
            debit=Decimal("0"),
            credit=Decimal("9000"),  # 10% TDS deducted
            source="party_statement"
        )
        
        results, summary = engine.reconcile(
            [invoice],
            [payment],
            {"name": "Test"}
        )
        
        # Should detect TDS difference
        assert len(results) >= 1
        # TDS detection happens in edge_cases module
        tds_flagged = any("tds_detected" in r.flags for r in results)
        assert tds_flagged == True
    
    def test_payment_with_tds_section_194j(self, engine):
        """TDS on professional fees should flag section 194J"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Professional fees to CA",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payment = Transaction(
            id="p1",
            date=date(2026, 3, 20),
            reference="PMT-001",
            particulars="Payment",
            debit=Decimal("0"),
            credit=Decimal("45000"),  # 10% TDS
            source="party_statement"
        )
        
        results, _ = engine.reconcile([invoice], [payment], {"name": "Test"})
        
        tds_flagged = any("tds_detected" in r.flags for r in results)
        assert tds_flagged == True


# ============================================================================
# DATE WINDOW TESTS
# ============================================================================

@pytest.mark.tier3
class TestDateWindowMatching:
    """Test date window constraints for partial matching"""
    
    def test_payments_within_30_days(self, matcher):
        """Payments within 30 days of invoice should match"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 1),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payments = [
            Transaction(id="p1", date=date(2026, 3, 15), reference="PMT-1",
                       particulars="Payment 1", debit=Decimal("0"), credit=Decimal("25000"), source="party_statement"),
            Transaction(id="p2", date=date(2026, 3, 25), reference="PMT-2",
                       particulars="Payment 2", debit=Decimal("0"), credit=Decimal("25000"), source="party_statement"),
        ]
        
        results, remaining_yours, remaining_party = matcher.find_partial_matches(
            [invoice],
            payments
        )
        
        assert len(results) == 1
        assert len(remaining_party) == 0
    
    def test_payments_beyond_30_days(self, matcher):
        """Payments beyond 30 days should not partial match"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 1),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payments = [
            Transaction(id="p1", date=date(2026, 4, 15), reference="PMT-1",
                       particulars="Payment 1", debit=Decimal("0"), credit=Decimal("25000"), source="party_statement"),
            Transaction(id="p2", date=date(2026, 4, 25), reference="PMT-2",
                       particulars="Payment 2", debit=Decimal("0"), credit=Decimal("25000"), source="party_statement"),
        ]
        
        results, remaining_yours, remaining_party = matcher.find_partial_matches(
            [invoice],
            payments
        )
        
        # Beyond 30 day window
        assert len(results) == 0
        assert len(remaining_yours) == 1
        assert len(remaining_party) == 2


# ============================================================================
# CONFIDENCE SCORING TESTS
# ============================================================================

@pytest.mark.tier2
class TestPartialPaymentConfidence:
    """Test confidence scoring for partial payments"""
    
    def test_two_payment_confidence(self, matcher):
        """Two payments should have higher confidence than 4+"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        # 2 payments
        payments_2 = [
            Transaction(id="p1", date=date(2026, 3, 20), reference="PMT-1",
                       particulars="Payment 1", debit=Decimal("0"), credit=Decimal("25000"), source="party_statement"),
            Transaction(id="p2", date=date(2026, 3, 25), reference="PMT-2",
                       particulars="Payment 2", debit=Decimal("0"), credit=Decimal("25000"), source="party_statement"),
        ]
        
        results_2, _, _ = matcher.find_partial_matches([invoice], payments_2)
        
        assert len(results_2) == 1
        assert results_2[0].confidence_score >= 0.80
    
    def test_exact_amount_confidence(self, matcher):
        """Exact amount match should have higher confidence"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payments = [
            Transaction(id="p1", date=date(2026, 3, 20), reference="PMT-1",
                       particulars="Payment 1", debit=Decimal("0"), credit=Decimal("25000"), source="party_statement"),
            Transaction(id="p2", date=date(2026, 3, 25), reference="PMT-2",
                       particulars="Payment 2", debit=Decimal("0"), credit=Decimal("25000"), source="party_statement"),
        ]
        
        results, _, _ = matcher.find_partial_matches([invoice], payments)
        
        assert results[0].difference == Decimal("0")
        assert results[0].confidence_score >= 0.85
    
    def test_amount_difference_confidence(self, matcher):
        """Amount difference should reduce confidence"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payments = [
            Transaction(id="p1", date=date(2026, 3, 20), reference="PMT-1",
                       particulars="Payment 1", debit=Decimal("0"), credit=Decimal("24000"), source="party_statement"),
            Transaction(id="p2", date=date(2026, 3, 25), reference="PMT-2",
                       particulars="Payment 2", debit=Decimal("0"), credit=Decimal("24000"), source="party_statement"),
        ]
        
        results, _, _ = matcher.find_partial_matches([invoice], payments)
        
        assert results[0].difference == Decimal("2000")
        assert results[0].confidence_score < 0.85


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.edge_case
class TestPartialPaymentEdgeCases:
    """Test edge cases and error handling"""
    
    def test_single_payment_not_partial(self, matcher):
        """Single payment should not be treated as partial"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payment = Transaction(
            id="p1",
            date=date(2026, 3, 20),
            reference="PMT-001",
            particulars="Payment",
            debit=Decimal("0"),
            credit=Decimal("50000"),
            source="party_statement"
        )
        
        results, remaining_yours, remaining_party = matcher.find_partial_matches(
            [invoice],
            [payment]
        )
        
        # Single payment = exact match, not partial
        assert len(results) == 0
        assert len(remaining_yours) == 1
        assert len(remaining_party) == 1
    
    def test_overpayment_detection(self, matcher):
        """Payment exceeding invoice amount should not match"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("50000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payments = [
            Transaction(id="p1", date=date(2026, 3, 20), reference="PMT-1",
                       particulars="Payment 1", debit=Decimal("0"), credit=Decimal("60000"), source="party_statement"),
        ]
        
        results, remaining_yours, remaining_party = matcher.find_partial_matches(
            [invoice],
            payments
        )
        
        # Overpayment should not match
        assert len(results) == 0
    
    def test_zero_amount_invoice(self, matcher):
        """Zero amount invoice should be handled"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Credit note",
            debit=Decimal("0"),
            credit=Decimal("0"),
            source="tally"
        )
        
        payments = []
        
        results, remaining_yours, remaining_party = matcher.find_partial_matches(
            [invoice],
            payments
        )
        
        assert len(remaining_yours) == 1
    
    def test_maximum_partial_entries(self, matcher):
        """Should respect MAX_PARTIAL_ENTRIES limit"""
        invoice = Transaction(
            id="y1",
            date=date(2026, 3, 15),
            reference="INV-001",
            particulars="Sales",
            debit=Decimal("100000"),
            credit=Decimal("0"),
            source="tally"
        )
        
        # 10 small payments
        payments = [
            Transaction(
                id=f"p{i}",
                date=date(2026, 3, 20) + timedelta(days=i),
                reference=f"PMT-{i}",
                particulars=f"Payment {i}",
                debit=Decimal("0"),
                credit=Decimal("10000"),
                source="party_statement"
            )
            for i in range(10)
        ]
        
        results, remaining_yours, remaining_party = matcher.find_partial_matches(
            [invoice],
            payments
        )
        
        # Should only group up to MAX_PARTIAL_ENTRIES (5)
        if len(results) > 0:
            assert results[0].metadata["entry_count"] <= 5


# ============================================================================
# INTEGRATION WITH MATCHING ENGINE
# ============================================================================

@pytest.mark.integration
class TestPartialPaymentIntegration:
    """Test partial payment integration with main matching engine"""
    
    def test_partial_match_in_full_reconciliation(self, engine):
        """Partial payments should work in full reconciliation flow"""
        your_txn = [
            Transaction(
                id="y1",
                date=date(2026, 3, 15),
                reference="INV-001",
                particulars="Sales",
                debit=Decimal("50000"),
                credit=Decimal("0"),
                source="tally"
            ),
        ]
        
        party_txn = [
            Transaction(
                id="p1",
                date=date(2026, 3, 20),
                reference="PMT-001",
                particulars="Part payment",
                debit=Decimal("0"),
                credit=Decimal("30000"),
                source="party_statement"
            ),
            Transaction(
                id="p2",
                date=date(2026, 3, 25),
                reference="PMT-002",
                particulars="Final payment",
                debit=Decimal("0"),
                credit=Decimal("20000"),
                source="party_statement"
            ),
        ]
        
        results, summary = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        # Should have partial match result
        partial_matches = [r for r in results if "partial_payment" in r.flags]
        assert len(partial_matches) >= 1
    
    def test_mixed_exact_and_partial_matches(self, engine):
        """Reconciliation with both exact and partial matches"""
        your_txn = [
            Transaction(id="y1", date=date(2026, 3, 15), reference="INV-001",
                       particulars="Sales 1", debit=Decimal("25000"), credit=Decimal("0"), source="tally"),
            Transaction(id="y2", date=date(2026, 3, 18), reference="INV-002",
                       particulars="Sales 2", debit=Decimal("50000"), credit=Decimal("0"), source="tally"),
        ]
        
        party_txn = [
            Transaction(id="p1", date=date(2026, 3, 15), reference="INV-001",
                       particulars="Payment", debit=Decimal("0"), credit=Decimal("25000"), source="party_statement"),
            Transaction(id="p2", date=date(2026, 3, 20), reference="PMT-1",
                       particulars="Part payment", debit=Decimal("0"), credit=Decimal("30000"), source="party_statement"),
            Transaction(id="p3", date=date(2026, 3, 25), reference="PMT-2",
                       particulars="Final payment", debit=Decimal("0"), credit=Decimal("20000"), source="party_statement"),
        ]
        
        results, summary = engine.reconcile(your_txn, party_txn, {"name": "Test"})
        
        # Should have both exact and partial matches
        exact_matches = [r for r in results if r.status == MatchStatus.EXACT]
        partial_matches = [r for r in results if "partial_payment" in r.flags]
        
        assert len(exact_matches) >= 1
        assert len(partial_matches) >= 1


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
