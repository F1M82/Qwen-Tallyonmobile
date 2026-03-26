# backend/services/reconciliation/party_matcher.py

from typing import Optional, List, Tuple
from difflib import SequenceMatcher
import re

class PartyMatcher:
    """
    Matches party names across different sources using hierarchical approach.
    This is CRITICAL — wrong party matching breaks entire reconciliation.
    """
    
    # Common words to ignore in name matching
    STOP_WORDS = {
        'pvt', 'ltd', 'private', 'limited', 'and', '&', 'co', 'company',
        'enterprises', 'trading', 'traders', 'associates', 'partners',
        'sons', 'daughters', 'firm', 'llp', 'corp', 'corporation',
        'india', 'indian', 'the', 'a', 'an'
    }
    
    # GSTIN validation regex
    GSTIN_PATTERN = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')
    
    def __init__(self, tally_ledgers: List[dict]):
        """
        Initialize with all ledgers from Tally.
        Expected format: [{"name": "ABC", "gstin": "27XXX", "pan": "XXX"}, ...]
        """
        self.ledgers = tally_ledgers
        self.gstin_index = self._build_gstin_index()
        self.pan_index = self._build_pan_index()
        self.name_index = self._build_name_index()
    
    def _build_gstin_index(self) -> dict:
        """Build O(1) lookup by GSTIN"""
        index = {}
        for ledger in self.ledgers:
            gstin = ledger.get('gstin', '').upper().strip()
            if gstin and self.validate_gstin(gstin):
                index[gstin] = ledger
        return index
    
    def _build_pan_index(self) -> dict:
        """Build O(1) lookup by PAN"""
        index = {}
        for ledger in self.ledgers:
            pan = ledger.get('pan', '').upper().strip()
            if pan and len(pan) == 10:
                index[pan] = ledger
        return index
    
    def _build_name_index(self) -> dict:
        """Build normalized name index for fuzzy matching"""
        index = {}
        for ledger in self.ledgers:
            normalized = self._normalize_name(ledger['name'])
            index[normalized] = ledger
        return index
    
    @classmethod
    def validate_gstin(cls, gstin: str) -> bool:
        """Validate GSTIN format and checksum"""
        if not gstin or len(gstin) != 15:
            return False
        if not cls.GSTIN_PATTERN.match(gstin):
            return False
        # Additional checksum validation can be added here
        return True
    
    @classmethod
    def _normalize_name(cls, name: str) -> str:
        """
        Normalize party name for comparison.
        "Sharma Private Limited" → "sharma"
        "ABC & Co. Traders" → "abc co traders"
        """
        if not name:
            return ""
        
        # Lowercase
        name = name.lower()
        
        # Remove special chars
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # Remove stop words
        words = name.split()
        words = [w for w in words if w not in cls.STOP_WORDS]
        
        # Remove extra spaces
        return ' '.join(words).strip()
    
    def match(self, party_identifier: dict) -> Tuple[Optional[dict], str, float]:
        """
        Match party using hierarchical approach.
        
        Args:
            party_identifier: {"name": str, "gstin": str, "pan": str}
        
        Returns:
            (matched_ledger, match_method, confidence_score)
        """
        gstin = party_identifier.get('gstin', '').upper().strip()
        pan = party_identifier.get('pan', '').upper().strip()
        name = party_identifier.get('name', '')
        
        # TIER 1: GSTIN Exact Match (100% confidence)
        if gstin and self.validate_gstin(gstin):
            if gstin in self.gstin_index:
                return self.gstin_index[gstin], "gstin_exact", 1.0
        
        # TIER 2: PAN Match (95% confidence)
        if pan and len(pan) == 10:
            if pan in self.pan_index:
                return self.pan_index[pan], "pan_exact", 0.95
        
        # TIER 3: GSTIN Partial Match (first 10 chars = PAN + state)
        if gstin and len(gstin) >= 10:
            pan_from_gstin = gstin[2:12]  # Characters 2-11 are PAN
            if pan_from_gstin in self.pan_index:
                return self.pan_index[pan_from_gstin], "gstin_pan_extract", 0.90
        
        # TIER 4: Fuzzy Name Match (variable confidence)
        if name:
            ledger, confidence = self._fuzzy_name_match(name)
            if ledger and confidence >= 0.70:
                return ledger, "name_fuzzy", confidence
        
        # TIER 5: No Match
        return None, "no_match", 0.0
    
    def _fuzzy_name_match(self, name: str) -> Tuple[Optional[dict], float]:
        """
        Fuzzy match against all ledger names.
        Uses multiple strategies and returns best match.
        """
        normalized_input = self._normalize_name(name)
        
        best_ledger = None
        best_score = 0.0
        
        for ledger in self.ledgers:
            normalized_ledger = self._normalize_name(ledger['name'])
            
            # Strategy 1: Exact normalized match
            if normalized_input == normalized_ledger:
                return ledger, 0.95
            
            # Strategy 2: Token overlap (Jaccard similarity)
            input_tokens = set(normalized_input.split())
            ledger_tokens = set(normalized_ledger.split())
            
            if input_tokens and ledger_tokens:
                intersection = input_tokens & ledger_tokens
                union = input_tokens | ledger_tokens
                token_score = len(intersection) / len(union)
            else:
                token_score = 0.0
            
            # Strategy 3: String similarity (SequenceMatcher)
            string_score = SequenceMatcher(
                None, normalized_input, normalized_ledger
            ).ratio()
            
            # Strategy 4: Contains check (one name contains the other)
            contains_score = 0.0
            if normalized_input in normalized_ledger or normalized_ledger in normalized_input:
                contains_score = 0.85
            
            # Weighted combination
            combined_score = (
                token_score * 0.4 +
                string_score * 0.4 +
                contains_score * 0.2
            )
            
            if combined_score > best_score:
                best_score = combined_score
                best_ledger = ledger
        
        return best_ledger, best_score
    
    def batch_match(self, parties: List[dict]) -> List[dict]:
        """
        Match multiple parties efficiently.
        Returns list of match results for audit trail.
        """
        results = []
        for party in parties:
            ledger, method, confidence = self.match(party)
            results.append({
                "input": party,
                "matched_ledger": ledger,
                "match_method": method,
                "confidence": confidence,
                "requires_review": confidence < 0.90
            })
        return results
