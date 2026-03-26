# backend/services/reconciliation/confidence_scorer.py

from typing import List
from decimal import Decimal

from .types import MatchResult, MatchStatus, MatchTier

class ConfidenceScorer:
    """
    Calculates confidence scores for match results.
    Used to determine auto-post eligibility and review priority.
    """
    
    # Base scores by tier
    TIER_BASE_SCORES = {
        MatchTier.GSTIN_EXACT: 0.98,
        MatchTier.REFERENCE_EXACT: 0.92,
        MatchTier.AMOUNT_DATE_EXACT: 0.85,
        MatchTier.AMOUNT_DATE_FUZZY: 0.75,
        MatchTier.AMOUNT_ONLY: 0.55,
        MatchTier.MANUAL_REVIEW: 0.50,
    }
    
    # Modifiers
    DATE_DIFF_PENALTY = 0.02  # Per day
    AMOUNT_DIFF_PENALTY = 0.05  # If difference > ₹100
    TDS_DETECTED_BONUS = 0.10  # If TDS pattern detected
    DUPLICATE_PENALTY = 0.30  # If duplicate suspected
    
    def calculate(self, result: MatchResult, context: dict = None) -> float:
        """
        Calculate final confidence score with all modifiers.
        
        Args:
            result: MatchResult to score
            context: Additional context (historical patterns, etc.)
        
        Returns:
            Confidence score 0.0-1.0
        """
        # Start with base score
        score = self.TIER_BASE_SCORES.get(result.tier, 0.50)
        
        # Apply date difference penalty
        if result.your_transaction and result.party_transaction:
            date_diff = abs((result.your_transaction.date - result.party_transaction.date).days)
            score -= date_diff * self.DATE_DIFF_PENALTY
        
        # Apply amount difference penalty
        if result.difference > Decimal("100"):
            score -= self.AMOUNT_DIFF_PENALTY
        
        # Apply flag-based modifiers
        if "tds_detected" in result.flags:
            score += self.TDS_DETECTED_BONUS
        if "duplicate_suspected" in result.flags:
            score -= self.DUPLICATE_PENALTY
        if "timing_difference" in result.flags:
            score += 0.05  # Timing diffs are common and acceptable
        
        # Ensure bounds
        score = max(0.0, min(1.0, score))
        
        # Update result
        result.confidence_score = round(score, 2)
        result.auto_postable = (
            score >= 0.95 and
            result.status == MatchStatus.EXACT and
            "duplicate_suspected" not in result.flags
        )
        
        return score
    
    def batch_calculate(self, results: List[MatchResult], context: dict = None) -> List[MatchResult]:
        """Calculate scores for multiple results"""
        for result in results:
            self.calculate(result, context)
        return results
