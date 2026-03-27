"""
Test Suite: Party Matcher
==========================

Tests GSTIN-first party matching logic:
- GSTIN exact match
- PAN match
- GSTIN → PAN extraction
- Fuzzy name matching
- Batch matching

Coverage: 90%+
"""

import pytest
from typing import List, Dict

from services.reconciliation.party_matcher import PartyMatcher


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_ledgers():
    """Sample Tally ledgers for testing"""
    return [
        {"name": "Sharma Private Limited", "gstin": "27AABCS1234M1Z5", "pan": "AABCS1234M"},
        {"name": "Mehta Traders", "gstin": "27AABCM5678N1Z3", "pan": "AABCM5678N"},
        {"name": "ABC & Co. Enterprises", "gstin": None, "pan": "AABCA9876P"},
        {"name": "Gupta and Sons", "gstin": "27AABCG1111M1Z1", "pan": "AABCG1111M"},
        {"name": "Rajan Industries Pvt Ltd", "gstin": "27AABCR2222M1Z9", "pan": "AABCR2222M"},
    ]


@pytest.fixture
def matcher(sample_ledgers):
    """Create PartyMatcher instance"""
    return PartyMatcher(sample_ledgers)


# ============================================================================
# GSTIN MATCHING TESTS
# ============================================================================

@pytest.mark.tier1
class TestGSTINMatching:
    """Test GSTIN-based party matching"""
    
    def test_gstin_exact_match(self, matcher):
        """Exact GSTIN match should return 100% confidence"""
        party_info = {"name": "Test", "gstin": "27AABCS1234M1Z5", "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert ledger["name"] == "Sharma Private Limited"
        assert method == "gstin_exact"
        assert confidence == 1.0
    
    def test_gstin_case_insensitive(self, matcher):
        """GSTIN match should be case insensitive"""
        party_info = {"name": "Test", "gstin": "27aabcS1234m1z5", "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert ledger["name"] == "Sharma Private Limited"
        assert confidence == 1.0
    
    def test_gstin_with_spaces(self, matcher):
        """GSTIN with spaces should be trimmed"""
        party_info = {"name": "Test", "gstin": "  27AABCS1234M1Z5  ", "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert confidence == 1.0
    
    def test_invalid_gstin_format(self, matcher):
        """Invalid GSTIN format should not match"""
        party_info = {"name": "Sharma", "gstin": "INVALID123", "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is None
        assert method == "no_match"
        assert confidence == 0.0
    
    def test_gstin_wrong_length(self, matcher):
        """GSTIN with wrong length should not match"""
        party_info = {"name": "Sharma", "gstin": "27AABCS1234M1", "pan": None}  # 13 chars
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is None
        assert confidence == 0.0


# ============================================================================
# PAN MATCHING TESTS
# ============================================================================

@pytest.mark.tier2
class TestPANMatching:
    """Test PAN-based party matching"""
    
    def test_pan_exact_match(self, matcher):
        """Exact PAN match should return 95% confidence"""
        party_info = {"name": "Test", "gstin": None, "pan": "AABCM5678N"}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert ledger["name"] == "Mehta Traders"
        assert method == "pan_exact"
        assert confidence == 0.95
    
    def test_pan_case_insensitive(self, matcher):
        """PAN match should be case insensitive"""
        party_info = {"name": "Test", "gstin": None, "pan": "aabcm5678n"}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert confidence == 0.95
    
    def test_pan_invalid_length(self, matcher):
        """PAN with wrong length should not match"""
        party_info = {"name": "Test", "gstin": None, "pan": "AABCM567"}  # 8 chars
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is None
        assert confidence == 0.0
    
    def test_gstin_pan_extraction(self, matcher):
        """PAN extracted from GSTIN should match"""
        party_info = {"name": "Test", "gstin": "27AABCR2222M1Z9", "pan": None}
        
        # GSTIN not in ledgers, but PAN (AABCR2222M) is
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert ledger["name"] == "Rajan Industries Pvt Ltd"
        assert method == "gstin_pan_extract"
        assert confidence == 0.90


# ============================================================================
# FUZZY NAME MATCHING TESTS
# ============================================================================

@pytest.mark.tier3
class TestFuzzyNameMatching:
    """Test fuzzy name matching logic"""
    
    def test_exact_name_match(self, matcher):
        """Exact name match should return 95% confidence"""
        party_info = {"name": "Sharma Private Limited", "gstin": None, "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert method == "name_fuzzy"
        assert confidence >= 0.90
    
    def test_name_with_stop_words_removed(self, matcher):
        """Name matching should ignore common words like Pvt, Ltd, etc."""
        party_info = {"name": "Sharma Pvt Ltd", "gstin": None, "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert ledger["name"] == "Sharma Private Limited"
        assert confidence >= 0.85
    
    def test_name_with_ampersand(self, matcher):
        """Name with & should match 'and'"""
        party_info = {"name": "ABC and Co Enterprises", "gstin": None, "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert ledger["name"] == "ABC & Co. Enterprises"
        assert confidence >= 0.70
    
    def test_name_partial_match(self, matcher):
        """Partial name match should return lower confidence"""
        party_info = {"name": "Gupta Sons", "gstin": None, "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert ledger["name"] == "Gupta and Sons"
        assert 0.60 <= confidence <= 0.85
    
    def test_name_no_match(self, matcher):
        """Completely different name should not match"""
        party_info = {"name": "Completely Different Corp", "gstin": None, "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is None
        assert confidence < 0.70
    
    def test_name_with_special_chars(self, matcher):
        """Name with special characters should be normalized"""
        party_info = {"name": "Rajan Industries (P) Ltd.", "gstin": None, "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert ledger["name"] == "Rajan Industries Pvt Ltd"


# ============================================================================
# BATCH MATCHING TESTS
# ============================================================================

@pytest.mark.tier2
class TestBatchMatching:
    """Test batch party matching"""
    
    def test_batch_match_multiple_parties(self, matcher):
        """Batch match should process multiple parties efficiently"""
        parties = [
            {"name": "Sharma Pvt Ltd", "gstin": "27AABCS1234M1Z5", "pan": None},
            {"name": "Mehta Traders", "gstin": None, "pan": "AABCM5678N"},
            {"name": "Unknown Party", "gstin": None, "pan": None},
        ]
        
        results = matcher.batch_match(parties)
        
        assert len(results) == 3
        assert results[0]["matched_ledger"] is not None
        assert results[0]["match_method"] == "gstin_exact"
        assert results[1]["matched_ledger"] is not None
        assert results[1]["match_method"] == "pan_exact"
        assert results[2]["matched_ledger"] is None
        assert results[2]["match_method"] == "no_match"
    
    def test_batch_match_requires_review_flag(self, matcher):
        """Batch match should flag low confidence matches for review"""
        parties = [
            {"name": "Sharma Pvt Ltd", "gstin": "27AABCS1234M1Z5", "pan": None},
            {"name": "Similar Name Corp", "gstin": None, "pan": None},
        ]
        
        results = matcher.batch_match(parties)
        
        assert results[0]["requires_review"] == False  # High confidence
        assert results[1]["requires_review"] == True  # Low confidence


# ============================================================================
# GSTIN VALIDATION TESTS
# ============================================================================

@pytest.mark.edge_case
class TestGSTINValidation:
    """Test GSTIN format validation"""
    
    def test_valid_gstin_format(self, matcher):
        """Valid GSTIN format should pass validation"""
        assert matcher.validate_gstin("27AABCS1234M1Z5") == True
        assert matcher.validate_gstin("27AABCM5678N1Z3") == True
    
    def test_invalid_gstin_characters(self, matcher):
        """GSTIN with invalid characters should fail"""
        assert matcher.validate_gstin("27AABCS1234M1Z@") == False
        assert matcher.validate_gstin("27AABCS1234M1Z ") == False
    
    def test_invalid_gstin_state_code(self, matcher):
        """GSTIN with invalid state code should fail"""
        assert matcher.validate_gstin("99AABCS1234M1Z5") == False  # 99 is not valid
        assert matcher.validate_gstin("00AABCS1234M1Z5") == False  # 00 is not valid
    
    def test_empty_gstin(self, matcher):
        """Empty GSTIN should fail validation"""
        assert matcher.validate_gstin("") == False
        assert matcher.validate_gstin(None) == False


# ============================================================================
# NAME NORMALIZATION TESTS
# ============================================================================

@pytest.mark.edge_case
class TestNameNormalization:
    """Test name normalization logic"""
    
    def test_normalize_removes_stop_words(self, matcher):
        """Normalization should remove common stop words"""
        normalized = matcher._normalize_name("Sharma Private Limited")
        assert "private" not in normalized
        assert "limited" not in normalized
        assert "sharma" in normalized
    
    def test_normalize_removes_special_chars(self, matcher):
        """Normalization should remove special characters"""
        normalized = matcher._normalize_name("ABC & Co. (P) Ltd!")
        assert "&" not in normalized
        assert "." not in normalized
        assert "(" not in normalized
    
    def test_normalize_lowercase(self, matcher):
        """Normalization should convert to lowercase"""
        normalized = matcher._normalize_name("SHARMA TRADERS")
        assert normalized == normalized.lower()
    
    def test_normalize_extra_spaces(self, matcher):
        """Normalization should remove extra spaces"""
        normalized = matcher._normalize_name("Sharma    Traders")
        assert "  " not in normalized  # No double spaces


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.edge_case
class TestPartyMatcherEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_ledgers(self):
        """Empty ledger list should return no matches"""
        matcher = PartyMatcher([])
        party_info = {"name": "Test", "gstin": "27AABCS1234M1Z5", "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is None
        assert confidence == 0.0
    
    def test_party_info_empty(self, matcher):
        """Empty party info should return no match"""
        party_info = {"name": "", "gstin": "", "pan": ""}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is None
        assert confidence == 0.0
    
    def test_party_info_none_values(self, matcher):
        """None values in party info should be handled"""
        party_info = {"name": None, "gstin": None, "pan": None}
        
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is None
    
    def test_multiple_ledgers_same_gstin(self):
        """Multiple ledgers with same GSTIN - first should win"""
        ledgers = [
            {"name": "Sharma Pvt Ltd", "gstin": "27AABCS1234M1Z5", "pan": "AABCS1234M"},
            {"name": "Sharma Enterprises", "gstin": "27AABCS1234M1Z5", "pan": "AABCS1234M"},
        ]
        matcher = PartyMatcher(ledgers)
        
        party_info = {"name": "Test", "gstin": "27AABCS1234M1Z5", "pan": None}
        ledger, method, confidence = matcher.match(party_info)
        
        assert ledger is not None
        assert ledger["name"] == "Sharma Pvt Ltd"  # First match


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
