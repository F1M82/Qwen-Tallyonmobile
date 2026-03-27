# FILE: backend/services/reconciliation/matching_engine.py
"""
from typing import List, Dict, Optional, Tuple
from datetime import date, timedelta
from decimal import Decimal
from difflib import SequenceMatcher
import re
import uuid

class Transaction:
    def __init__(self, id: str, date: date, reference: str, particulars: str, 
                 debit: Decimal, credit: Decimal, gstin: str = None, source: str = ""):
        self.id = id
        self.date = date
        self.reference = reference or ""
        self.particulars = particulars
        self.debit = debit
        self.credit = credit
        self.gstin = gstin
        self.source = source
    
    @property
    def amount(self) -> Decimal:
        return self.debit if self.debit > 0 else self.credit
    
    @property
    def entry_type(self) -> str:
        return "Dr" if self.debit > 0 else "Cr"

class MatchResult:
    def __init__(self, your_txn: Optional[Transaction], party_txn: Optional[Transaction],
                 status: str, tier: str, confidence: float, reason: str):
        self.id = str(uuid.uuid4())
        self.your_transaction = your_txn
        self.party_transaction = party_txn
        self.status = status
        self.tier = tier
        self.confidence_score = confidence
        self.difference = Decimal("0")
        self.reason = reason
        self.flags = []
        self.suggested_action = ""
        self.requires_review = confidence < 0.95
        self.auto_postable = confidence >= 0.95
        self.created_at = date.today().isoformat()

class ReconciliationMatchingEngine:
    DATE_TOLERANCE_FUZZY = 5
    DATE_TOLERANCE_AMOUNT_ONLY = 15
    AMOUNT_TOLERANCE = Decimal("1.00")
    
    def __init__(self):
        pass
    
    def reconcile(self, your_transactions: List[Transaction], 
                  party_transactions: List[Transaction]) -> Tuple[List[MatchResult], Dict]:
        unmatched_yours = list(your_transactions)
        unmatched_party = list(party_transactions)
        results = []
        
        # Tier 1: Exact match (ref + amount + date)
        tier1, unmatched_yours, unmatched_party = self._exact_match(unmatched_yours, unmatched_party)
        results.extend(tier1)
        
        # Tier 2: Fuzzy reference match
        tier2, unmatched_yours, unmatched_party = self._fuzzy_ref_match(unmatched_yours, unmatched_party)
        results.extend(tier2)
        
        # Tier 3: Amount + date fuzzy
        tier3, unmatched_yours, unmatched_party = self._amount_date_match(unmatched_yours, unmatched_party)
        results.extend(tier3)
        
        # Tier 4: Unmatched
        for txn in unmatched_yours:
            results.append(MatchResult(txn, None, "missing_in_party", "manual_review", 
                                      1.0, "In your books but not in party statement"))
        for txn in unmatched_party:
            results.append(MatchResult(None, txn, "missing_in_books", "manual_review",
                                      1.0, "In party statement but not in your books"))
        
        summary = self._calculate_summary(results, your_transactions, party_transactions)
        return results, summary
    
    def _exact_match(self, yours, party):
        matched = []
        remaining_yours = []
        remaining_party = list(party)
        
        for y in yours:
            found = False
            for p in remaining_party:
                if (self._amounts_equal(y.amount, p.amount) and
                    self._refs_match(y.reference, p.reference) and
                    y.date == p.date):
                    matched.append(MatchResult(y, p, "exact", "reference_exact",
                                              0.98, "Exact match on reference, amount and date"))
                    remaining_party.remove(p)
                    found = True
                    break
            if not found:
                remaining_yours.append(y)
        
        return matched, remaining_yours, remaining_party
    
    def _fuzzy_ref_match(self, yours, party):
        matched = []
        remaining_yours = []
        remaining_party = list(party)
        
        for y in yours:
            best_score = 0
            best_p = None
            
            for p in remaining_party:
                if self._amounts_equal(y.amount, p.amount):
                    ref_similarity = SequenceMatcher(None, 
                        self._clean_ref(y.reference), 
                        self._clean_ref(p.reference)).ratio()
                    
                    if ref_similarity > 0.75:
                        date_diff = abs((y.date - p.date).days)
                        if date_diff <= 7:
                            score = ref_similarity * 0.7 + (1 - date_diff/7) * 0.3
                            if score > best_score:
                                best_score = score
                                best_p = p
            
            if best_p:
                matched.append(MatchResult(y, best_p, "fuzzy", "fuzzy_reference",
                                          best_score, f"Reference similarity {best_score:.0%}"))
                remaining_party.remove(best_p)
            else:
                remaining_yours.append(y)
        
        return matched, remaining_yours, remaining_party
    
    def _amount_date_match(self, yours, party):
        matched = []
        remaining_yours = []
        remaining_party = list(party)
        
        for y in yours:
            best_score = 0
            best_p = None
            
            for p in remaining_party:
                if self._amounts_equal(y.amount, p.amount):
                    date_diff = abs((y.date - p.date).days)
                    if date_diff <= self.DATE_TOLERANCE_FUZZY:
                        score = 0.80 - (date_diff * 0.02)
                        if score > best_score:
                            best_score = score
                            best_p = p
            
            if best_p:
                result = MatchResult(y, best_p, "fuzzy", "amount_date_fuzzy",
                                    max(best_score, 0.70), "Amount match with date difference")
                result.flags.append("timing_difference")
                matched.append(result)
                remaining_party.remove(best_p)
            else:
                remaining_yours.append(y)
        
        return matched, remaining_yours, remaining_party
    
    def _amounts_equal(self, a: Decimal, b: Decimal) -> bool:
        return abs(a - b) <= self.AMOUNT_TOLERANCE
    
    def _refs_match(self, r1: str, r2: str) -> bool:
        return self._clean_ref(r1) == self._clean_ref(r2)
    
    def _clean_ref(self, ref: str) -> str:
        if not ref:
            return ""
        ref = re.sub(r'[^0-9]', '', ref).lstrip('0')
        return ref
    
    def _calculate_summary(self, results, your_txns, party_txns):
        matched = [r for r in results if r.status == "exact"]
        fuzzy = [r for r in results if r.status == "fuzzy"]
        missing_party = [r for r in results if r.status == "missing_in_party"]
        missing_books = [r for r in results if r.status == "missing_in_books"]
        
        your_balance = sum((t.debit - t.credit) for t in your_txns)
        party_balance = sum((t.debit - t.credit) for t in party_txns)
        
        return {
            "matched_count": len(matched),
            "fuzzy_count": len(fuzzy),
            "missing_in_party_count": len(missing_party),
            "missing_in_books_count": len(missing_books),
            "your_balance": str(your_balance),
            "party_balance": str(party_balance),
            "difference": str(abs(your_balance - party_balance)),
            "auto_postable_count": len([r for r in results if r.auto_postable])
        }
"""
