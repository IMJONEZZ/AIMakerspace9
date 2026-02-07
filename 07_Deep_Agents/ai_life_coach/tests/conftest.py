"""
Pytest configuration and shared fixtures for comprehensive test scenarios.

This file provides:
- Shared fixtures for all test scenarios
- pytest hooks for test execution
- Custom markers for test categorization
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def pytest_configure(config):
    """Configure custom markers for test categorization."""
    config.addinivalue_line("markers", "single_domain: tests for single-domain scenarios")
    config.addinivalue_line("markers", "multi_domain: tests for multi-domain integration")
    config.addinivalue_line("markers", "edge_case: tests for edge cases and error handling")
    config.addinivalue_line("markers", "regression: tests for regression prevention")
    config.addinivalue_line("markers", "career: tests for career domain")
    config.addinivalue_line("markers", "relationship: tests for relationship domain")
    config.addinivalue_line("markers", "finance: tests for finance domain")
    config.addinivalue_line("markers", "wellness: tests for wellness domain")
    config.addinivalue_line("markers", "crisis: tests for crisis detection and response")
    config.addinivalue_line("markers", "slow: tests that take longer to run")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Auto-mark based on test class name
        if "Career" in item.nodeid:
            item.add_marker(pytest.mark.career)
            item.add_marker(pytest.mark.single_domain)
        if "Relationship" in item.nodeid:
            item.add_marker(pytest.mark.relationship)
            item.add_marker(pytest.mark.single_domain)
        if "Financial" in item.nodeid or "Finance" in item.nodeid:
            item.add_marker(pytest.mark.finance)
            item.add_marker(pytest.mark.single_domain)
        if "Wellness" in item.nodeid:
            item.add_marker(pytest.mark.wellness)
            item.add_marker(pytest.mark.single_domain)
        if "Crisis" in item.nodeid:
            item.add_marker(pytest.mark.crisis)
            item.add_marker(pytest.mark.edge_case)
        if "Integration" in item.nodeid or "Multi" in item.nodeid:
            item.add_marker(pytest.mark.multi_domain)
        if "Regression" in item.nodeid:
            item.add_marker(pytest.mark.regression)
        if "Conflict" in item.nodeid or "Failure" in item.nodeid:
            item.add_marker(pytest.mark.edge_case)


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "test_mode": True,
        "mock_external_apis": True,
        "cleanup_after_tests": True,
        "log_level": "DEBUG",
    }


@pytest.fixture(scope="function")
def isolated_workspace(tmp_path):
    """Create an isolated workspace for a single test."""
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace
