# backend/services/reconciliation/edge_cases.py

from typing import List
from decimal import Decimal

from .types import MatchResult, MatchStatus

class EdgeCaseDetector:
    """
    Detects common edge cases in reconciliation.
    These flags help CAs understand WHY there's a difference.
    """
    
    # TDS rates commonly seen in India
    TDS_RATES = [0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30]
    
    # Section 40A(3) cash payment limit
    CASH_PAYMENT_LIMIT = Decimal("10000")
    
    def detect(self, result: MatchResult) -> List[str]:
        """
        Detect edge cases for a single match result.
        Returns list of flag strings.
        """
        flags = []
        
        # TDS Detection
        if self._is_tds_difference(result):
            flags.append("tds_detected")
            section = self._infer_tds_section(result.difference, result)
            if section:
                flags.append(f"tds_section_{section}")
        
        # Timing Difference
        if self._is_timing_difference(result):
            flags.append("timing_difference")
        
        # Duplicate Detection
        if self._is_duplicate_suspected(result):
            flags.append("duplicate_suspected")
        
        # Round Number Bias
        if self._is_round_number(result):
            flags.append("round_number")
        
        # Cash Payment Above Limit
        if self._is_cash_above_limit(result):
            flags.append("section_40a3_risk")
        
        # Backdated Entry
        if self._is_backdated(result):
            flags.append("backdated_entry")
        
        return flags
    
    def _is_tds_difference(self, result: MatchResult) -> bool:
        """Check if difference matches common TDS rates"""
        if not result.your_transaction or not result.party_transaction:
            return False
        
        larger = max(result.your_transaction.amount, result.party_transaction.amount)
        smaller = min(result.your_transaction.amount, result.party_transaction.amount)
        
        if larger == 0:
            return False
        
        diff_ratio = float(abs(larger - smaller) / larger)
        
        # Check if difference matches any TDS rate (within 0.5% tolerance)
        for rate in self.TDS_RATES:
            if abs(diff_ratio - rate) < 0.005:
                return True
        
        return False
    
    def _infer_tds_section(self, difference: Decimal, result: MatchResult) -> str:
        """Infer TDS section based on amount and context"""
        # This is simplified — in production, use more context
        if result.your_transaction and "professional" in result.your_transaction.particulars.lower():
            return "194J"
        if result.your_transaction and "contractor" in result.your_transaction.particulars.lower():
            return "194C"
        if result.your_transaction and "rent" in result.your_transaction.particulars.lower():
            return "194I"
        return "unknown"
    
    def _is_timing_difference(self, result: MatchResult) -> bool:
        """Check if this is likely a timing difference"""
        if not result.your_transaction or not result.party_transaction:
            return False
        
        date_diff = abs((result.your_transaction.date - result.party_transaction.date).days)
        return 1 <= date_diff <= 5  # 1-5 days is common for bank clearing
    
    def _is_duplicate_suspected(self, result: MatchResult) -> bool:
        """Check if duplicate entry is suspected"""
        # Check if same amount + same party appears multiple times
        # This requires context from other results
        if "duplicate_check" in result.metadata:
            return result.metadata["duplicate_check"]
        return False
    
    def _is_round_number(self, result: MatchResult) -> bool:
        """Check if amount is suspiciously round"""
        amount = result.your_transaction.amount if result.your_transaction else result.party_transaction.amount
        if not amount:
            return False
        
        # Check if amount ends in 000
        return float(amount) % 1000 == 0 and float(amount) >= 10000
    
    def _is_cash_above_limit(self, result: MatchResult) -> bool:
        """Check Section 40A(3) risk — cash payment > ₹10,000"""
        if not result.your_transaction:
            return False
        
        if "cash" in result.your_transaction.particulars.lower():
            if result.your_transaction.amount > self.CASH_PAYMENT_LIMIT:
                return True
        
        return False
    
    def _is_backdated(self, result: MatchResult) -> bool:
        """Check if entry appears backdated"""
        if not result.your_transaction:
            return False
        
        # Compare transaction date with metadata created date
        if "created_at" in result.your_transaction.metadata:
            from datetime import datetime
            created = datetime.fromisoformat(result.your_transaction.metadata["created_at"]).date()
            date_diff = abs((created - result.your_transaction.date).days)
            return date_diff > 30  # More than 30 days gap
        
        return False
