"""Pytest configuration and shared fixtures."""

import pytest
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_vault_path():
    """Path to the test vault used across all tests."""
    return str(project_root / "test_vault")


@pytest.fixture(autouse=True)
def suppress_prints(capfd):
    """Suppress print statements during tests unless they fail."""
    yield
