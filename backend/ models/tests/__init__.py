"""
TaxMind Reconciliation Test Suite
==================================

Comprehensive tests for the reconciliation engine.

Run all tests:
    pytest backend/services/reconciliation/tests/ -v

Run specific test file:
    pytest backend/services/reconciliation/tests/test_matching_engine.py -v

Run with coverage:
    pytest backend/services/reconciliation/tests/ --cov=services/reconciliation
"""

# Markers for test categorization
import pytest

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "tier1: Tier 1 exact match tests")
    config.addinivalue_line("markers", "tier2: Tier 2 fuzzy match tests")
    config.addinivalue_line("markers", "tier3: Tier 3 amount-date match tests")
    config.addinivalue_line("markers", "tier4: Tier 4 amount-only match tests")
    config.addinivalue_line("markers", "edge_case: Edge case and anomaly tests")
    config.addinivalue_line("markers", "integration: Integration tests with DB")
    config.addinivalue_line("markers", "slow: Slow running tests")
