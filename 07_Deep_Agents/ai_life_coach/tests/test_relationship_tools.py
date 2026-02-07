"""
Test suite for Relationship Coach tools.

Tests all functionality in src/tools/relationship_tools.py.
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.relationship_tools import create_relationship_tools


class TestRelationshipTools:
    """Test suite for relationship coaching tools."""

    def setup_method(self):
        """Set up test fixtures before each test method."""

        # Create a mock backend class for testing
        class MockBackend:
            def __init__(self, root_dir):
                self.root_dir = root_dir
                self.files = {}

            def write_file(self, path: str, content: str) -> str:
                self.files[path] = content
                return f"File written to {path}"

            def read_file(self, path: str) -> str:
                if path not in self.files:
                    raise FileNotFoundError(f"File not found: {path}")
                return self.files[path]

        # Set up the mock backend
        self.backend = MockBackend(root_dir="/tmp/test_workspace")
        os.environ["WORKSPACE_DIR"] = "/tmp/test_workspace"

        # Create the relationship tools
        (
            self.analyze_communication_style,
            self.create_boundary_setting_plan,
            self.apply_dear_man_technique,
            self.assess_relationship_quality,
            self.develop_social_connection_plan,
            self.calculate_relationship_score,
            self.assess_communication_compatibility,
        ) = create_relationship_tools(backend=self.backend)

    def test_analyze_communication_style_basic(self):
        """Test basic communication style analysis."""
        result = self.analyze_communication_style.invoke(
            {
                "user_id": "test_user",
                "scenario_descriptions": [
                    "I often say 'yes' when I want to say 'no'",
                    "When people criticize me, I shut down",
                    "I rarely express my true feelings to others",
                ],
            }
        )
        assert result is not None and len(result) > 0
        assert "Communication Style Analysis" in result or "passive" in result.lower()
        print("✓ test_analyze_communication_style_basic passed")

    def test_create_boundary_setting_plan_basic(self):
        """Test basic boundary setting plan creation."""
        result = self.create_boundary_setting_plan.invoke(
            {
                "user_id": "test_user",
                "boundary_areas": ["work hours", "personal space"],
                "relationship_type": "workplace",
            }
        )
        assert result is not None and len(result) > 0
        assert "boundary" in result.lower() or "Boundary" in result
        print("✓ test_create_boundary_setting_plan_basic passed")

    def test_apply_dear_man_technique_basic(self):
        """Test basic DEAR MAN technique application."""
        result = self.apply_dear_man_technique.invoke(
            {
                "user_id": "test_user",
                "situation_description": "My coworker keeps interrupting me in meetings",
            }
        )
        assert result is not None and len(result) > 0
        assert "DEAR" in result or "Dear" in result
        print("✓ test_apply_dear_man_technique_basic passed")

    def test_assess_relationship_quality_basic(self):
        """Test basic relationship quality assessment."""
        result = self.assess_relationship_quality.invoke(
            {
                "user_id": "test_user",
                "relationship_type": "romantic",
                "ratings": {"trust": 7, "communication": 5},
            }
        )
        assert result is not None and len(result) > 0
        print("✓ test_assess_relationship_quality_basic passed")

    def test_develop_social_connection_plan_basic(self):
        """Test basic social connection plan development."""
        result = self.develop_social_connection_plan.invoke(
            {
                "user_id": "test_user",
                "current_situation": "I work from home and rarely see people",
                "goals": ["make new friends"],
            }
        )
        assert result is not None and len(result) > 0
        print("✓ test_develop_social_connection_plan_basic passed")

    def test_calculate_relationship_score_basic(self):
        """Test basic relationship score calculation."""
        result = self.calculate_relationship_score.invoke(
            {
                "user_id": "test_user",
                "quality_metrics": {"trust": 7, "communication": 6, "support": 8, "intimacy": 5},
                "relationship_type": "romantic",
            }
        )
        assert result is not None and len(result) > 0
        assert "score" in result.lower()
        print("✓ test_calculate_relationship_score_basic passed")

    def test_assess_communication_compatibility_basic(self):
        """Test basic communication compatibility assessment."""
        result = self.assess_communication_compatibility.invoke(
            {
                "user_id": "test_user",
                "style_a_description": "I prefer direct communication and getting straight to the point",
                "style_b_description": "My colleague likes to discuss things at length and build consensus",
            }
        )
        assert result is not None and len(result) > 0
        assert "compatibility" in result.lower()
        print("✓ test_assess_communication_compatibility_basic passed")

    def test_sample_scenario_struggle_with_boundaries(self):
        """Test sample scenario: 'I struggle with setting boundaries at work'."""
        # Analyze communication style
        comm_analysis = self.analyze_communication_style.invoke(
            {
                "user_id": "user_work",
                "scenario_descriptions": [
                    "I often say 'yes' when I want to say 'no'",
                    "My coworkers frequently ask me for help on their work",
                ],
                "relationship_context": "workplace",
            }
        )

        # Create boundary setting plan
        boundary_plan = self.create_boundary_setting_plan.invoke(
            {
                "user_id": "user_work",
                "boundary_areas": ["work hours"],
                "relationship_type": "workplace",
            }
        )

        # Verify both tools provide useful guidance
        assert len(comm_analysis) > 100
        assert "boundary" in boundary_plan.lower()
        print("✓ test_sample_scenario_struggle_with_boundaries passed")


def run_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 70)
    print("Running Relationship Tools Test Suite")
    print("=" * 70 + "\n")

    test_class = TestRelationshipTools()
    methods = [m for m in dir(test_class) if m.startswith("test_")]

    passed = 0
    failed = 0

    for method_name in methods:
        try:
            test_class.setup_method()
            method = getattr(test_class, method_name)
            method()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {method_name} FAILED: {e}")

    # Print summary
    print("\n" + "=" * 70)
    print(f"Test Summary: {passed} passed, {failed} failed out of {len(methods)} total")
    print("=" * 70 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
