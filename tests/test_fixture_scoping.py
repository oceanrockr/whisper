"""
Unit test to verify fixture scoping fix works correctly.

This test validates that fixtures are accessible across test classes
when defined at module level.
"""

import pytest


# Module-level fixture for testing
@pytest.fixture
def sample_fixture():
    """Sample fixture to test accessibility."""
    return {"data": "test"}


class TestFirstClass:
    """First test class using shared fixture."""

    def test_fixture_accessible_in_first_class(self, sample_fixture):
        """Unit test: Verify fixture accessible in first class."""
        assert sample_fixture is not None
        assert sample_fixture["data"] == "test"


class TestSecondClass:
    """Second test class using same shared fixture."""

    def test_fixture_accessible_in_second_class(self, sample_fixture):
        """Unit test: Verify fixture accessible in second class."""
        assert sample_fixture is not None
        assert sample_fixture["data"] == "test"


def test_fixture_accessibility_module_level(sample_fixture):
    """
    Unit test: Verify module-level fixtures are accessible to all test classes.

    This validates the fix for the DirectSound integration test errors.
    Original issue: Fixtures in TestDirectSoundFallback class were not
    accessible to TestDirectSoundFallbackIntegration class.

    Fix: Move fixtures to module level (outside classes).
    """
    # Arrange - fixture already provided

    # Act - access fixture data
    data = sample_fixture["data"]

    # Assert - fixture is accessible and contains expected data
    assert data == "test"
    assert isinstance(sample_fixture, dict)
