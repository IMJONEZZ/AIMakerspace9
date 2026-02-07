"""
Simplified integration tests for assessment tools.

This test suite demonstrates that the multi-domain assessment tools work correctly
when invoked through their LangChain tool interface.
"""

import pytest
from datetime import date

# Import and initialize config
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config, get_backend
from src.tools.assessment_tools import (
    create_assessment_tools,
    LIFE_DOMAINS,
    CROSS_DOMAIN_IMPACTS,
)

# Initialize environment
config.initialize_environment()

# Get backend and create tools
backend = get_backend()
assessment_tools_tuple = create_assessment_tools(backend=backend)

(
    conduct_initial_assessment,
    prioritize_domains_by_urgency,
    assess_cross_domain_impacts,
    generate_integrated_report,
    design_follow_up_questions,
) = assessment_tools_tuple


class TestAssessmentToolsIntegration:
    """Integration tests for all assessment tools."""

    def test_01_initial_assessment(self):
        """Test initial baseline assessment tool."""
        result = conduct_initial_assessment.invoke(
            {
                "user_id": "test_user_001",
                "goals": ["Get promoted to manager", "Improve physical fitness"],
                "current_situation": "Software engineer at mid-sized tech company",
            }
        )

        print("\n=== Initial Assessment Result ===")
        print(result)
        print("=" * 60)

        assert "Initial Multi-Domain Assessment" in result
        assert "test_user_001" in result
        assert "Get promoted to manager" in result
        assert "Improve physical fitness" in result
        assert all(domain_info["name"] in result for domain_info in LIFE_DOMAINS.values()), (
            "All domains should be mentioned"
        )

    def test_02_domain_prioritization(self):
        """Test domain prioritization algorithm."""
        result = prioritize_domains_by_urgency.invoke(
            {
                "user_id": "test_user_001",
                "domain_scores": {"career": 6, "wellness": 4, "finance": 5, "relationship": 7},
                "urgency_factors": {"finance": ["rent due soon", "unexpected car repair"]},
                "user_goals": ["Get promoted to manager", "Improve physical fitness"],
            }
        )

        print("\n=== Domain Prioritization Result ===")
        print(result)
        print("=" * 60)

        assert "Domain Prioritization Analysis" in result
        assert "Prioritized Domains" in result
        assert "rent due soon" in result or "unexpected car repair" in result

    def test_03_cross_domain_impacts(self):
        """Test cross-domain impact analysis."""
        result = assess_cross_domain_impacts.invoke(
            {
                "user_id": "test_user_001",
                "domain_changes": {
                    "career": "Accept promotion requiring more hours and responsibility"
                },
                "current_domain_scores": {"wellness": 4, "relationship": 6},
            }
        )

        print("\n=== Cross-Domain Impact Result ===")
        print(result)
        print("=" * 60)

        assert "Cross-Domain Impact Analysis" in result
        # Should identify potential negative impacts or positive synergies
        assert "Positive Impacts" in result or "Negative Risks" in result

    def test_04_integrated_report(self):
        """Test integrated report generation."""
        domain_assessments = {
            "career": {
                "score": 6,
                "strengths": ["Good technical skills", "Strong work ethic"],
                "challenges": ["Needs leadership experience", "Limited visibility"],
            },
            "wellness": {
                "score": 4,
                "strengths": ["Regular exercise"],
                "challenges": ["Poor sleep quality", "High stress levels"],
            },
            "finance": {
                "score": 5,
                "strengths": ["Steady income"],
                "challenges": ["No emergency fund", "High monthly expenses"],
            },
            "relationship": {
                "score": 7,
                "strengths": ["Supportive partner", "Good family relationships"],
                "challenges": ["Limited social circle outside work"],
            },
        }

        priority_data = {
            "domain_priorities": {
                "career": {"total_priority_score": 7.5},
                "wellness": {"total_priority_score": 8.2},
            }
        }

        result = generate_integrated_report.invoke(
            {
                "user_id": "test_user_001",
                "domain_assessments": domain_assessments,
                "priotization_data": priority_data,
            }
        )

        print("\n=== Integrated Report Result ===")
        print(result)
        print("=" * 60)

        assert "Integrated Assessment Report Generated" in result
        assert "Overall Balance Score" in result
        # Should include both JSON and Markdown file mentions
        assert ".json" in result.lower()
        assert ".md" in result.lower()

    def test_05_follow_up_questions(self):
        """Test follow-up question design."""
        result = design_follow_up_questions.invoke(
            {
                "user_id": "test_user_001",
                "assessment_gaps": {
                    "wellness": ["sleep quality habits", "specific stress triggers"],
                    "finance": ["monthly spending breakdown", "savings goals timeline"],
                },
            }
        )

        print("\n=== Follow-Up Questions Result ===")
        print(result)
        print("=" * 60)

        assert "Follow-Up Questions Plan" in result
        # Should have questions for the identified gaps
        assert "?" in result  # At least some question marks should be present

    def test_06_complete_workflow(self):
        """Test complete assessment workflow from start to finish."""
        print("\n=== Complete Assessment Workflow Test ===")

        # Step 1: Initial Assessment
        print("\nStep 1: Conducting initial assessment...")
        step1 = conduct_initial_assessment.invoke(
            {
                "user_id": "workflow_test_001",
                "goals": ["Advance career to senior role", "Improve work-life balance"],
                "current_situation": "Mid-level software engineer feeling burned out",
            }
        )
        assert "Initial Multi-Domain Assessment" in step1
        print("✓ Initial assessment completed")

        # Step 2: Prioritize Domains
        print("\nStep 2: Prioritizing domains by urgency...")
        step2 = prioritize_domains_by_urgency.invoke(
            {
                "user_id": "workflow_test_001",
                "domain_scores": {"career": 5, "wellness": 3, "finance": 6, "relationship": 4},
                "urgency_factors": {"wellness": ["burnout symptoms", "sleep issues"]},
            }
        )
        assert "Domain Prioritization Analysis" in step2
        print("✓ Domain prioritization completed")

        # Step 3: Cross-Domain Impact
        print("\nStep 3: Analyzing cross-domain impacts...")
        step3 = assess_cross_domain_impacts.invoke(
            {
                "user_id": "workflow_test_001",
                "domain_changes": {
                    "career": "Seek less demanding role",
                    "wellness": "Prioritize self-care",
                },
            }
        )
        assert "Cross-Domain Impact Analysis" in step3
        print("✓ Cross-domain impact analysis completed")

        # Step 4: Generate Report
        print("\nStep 4: Generating integrated report...")
        step4 = generate_integrated_report.invoke(
            {
                "user_id": "workflow_test_001",
                "domain_assessments": {
                    "career": {"score": 5, "strengths": ["Good skills"], "challenges": ["Burnout"]},
                    "wellness": {
                        "score": 3,
                        "strengths": [],
                        "challenges": ["High stress", "Poor sleep"],
                    },
                    "finance": {"score": 6, "strengths": [], "challenges": []},
                    "relationship": {"score": 4, "strengths": [], "challenges": ["Limited time"]},
                },
            }
        )
        assert "Integrated Assessment Report Generated" in step4
        print("✓ Integrated report generated")

        # Step 5: Follow-Up Questions
        print("\nStep 5: Designing follow-up questions...")
        step5 = design_follow_up_questions.invoke(
            {
                "user_id": "workflow_test_001",
                "assessment_gaps": {
                    "wellness": ["stress management strategies"],
                    "career": ["role preferences"],
                },
            }
        )
        assert "Follow-Up Questions Plan" in step5
        print("✓ Follow-up questions designed")

        print("\n=== Complete Workflow Test PASSED ===\n")
        print("All assessment tools successfully integrated and working together!")


class TestFrameworkStructure:
    """Test framework structures and constants."""

    def test_life_domains_defined(self):
        """Test that all life domains are properly defined."""
        expected_keys = {"career", "wellness", "finance", "relationship"}
        assert set(LIFE_DOMAINS.keys()) == expected_keys

    def test_domain_structure(self):
        """Test that each domain has required fields."""
        for domain_key, domain_info in LIFE_DOMAINS.items():
            assert "name" in domain_info
            assert "description" in domain_info
            assert "specialist" in domain_info
            assert "key_indicators" in domain_info
            assert isinstance(domain_info["key_indicators"], list)

    def test_cross_domain_impacts_defined(self):
        """Test that cross-domain impacts are properly defined."""
        assert len(CROSS_DOMAIN_IMPACTS) > 0

        for (domain_a, domain_b), impact_data in CROSS_DOMAIN_IMPACTS.items():
            assert domain_a in LIFE_DOMAINS
            assert domain_b in LIFE_DOMAINS
            assert "impact_type" in impact_data
            assert "strength" in impact_data
            assert 0 <= impact_data["strength"] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
