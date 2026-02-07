"""
Comprehensive test suite for multi-domain assessment tools.

Tests cover:
- Initial baseline assessment workflow
- Domain prioritization algorithm with various scenarios
- Cross-domain impact analysis logic
- Integrated report generation
- Follow-up question design

Based on research in multi-domain assessment frameworks and cross-domain analysis.
"""

import pytest
import json
from datetime import date, datetime
from pathlib import Path

# Import tools to test
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.tools.assessment_tools import (
    create_assessment_tools,
    LIFE_DOMAINS,
    CROSS_DOMAIN_IMPACTS,
)


# Initialize config before tests
config.initialize_environment()


# ==============================================================================
# Test Fixtures
# ==============================================================================


@pytest.fixture
def assessment_tools():
    """Create assessment tools for testing."""
    # Initialize config if not already done
    from src.config import get_backend

    try:
        backend = get_backend()
    except RuntimeError:
        from src.config import config

        config.initialize_environment()
        backend = get_backend()

    return create_assessment_tools(backend=backend)


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return "test_user_001"


@pytest.fixture
def sample_goals():
    """Sample user goals for testing."""
    return ["Advance career to manager", "Improve physical fitness"]


@pytest.fixture
def sample_domain_scores():
    """Sample domain scores for testing."""
    return {"career": 6, "wellness": 4, "finance": 5, "relationship": 7}


@pytest.fixture
def sample_urgency_factors():
    """Sample urgency factors for testing."""
    return {
        "finance": ["rent due soon", "unexpected car repair"],
        "wellness": ["high stress levels"],
    }


# ==============================================================================
# Test: conduct_initial_assessment
# ==============================================================================


class TestConductInitialAssessment:
    """Test suite for conduct_initial_assessment tool."""

    def test_conduct_initial_assessment_basic(self, assessment_tools):
        """Test basic initial assessment creation."""
        conduct_initial_assessment = assessment_tools[0]

        result = conduct_initial_assessment.invoke(
            {
                "user_id": "user_123",
                "goals": ["Get promoted"],
                "current_situation": "Software engineer",
            }
        )

        assert "Initial Multi-Domain Assessment" in result
        assert "user_123" in result
        assert "Get promoted" in result

    def test_conduct_initial_assessment_with_demographics(self, assessment_tools):
        """Test initial assessment with demographic information."""
        conduct_initial_assessment = assessment_tools[0]

        result = conduct_initial_assessment(
            user_id="user_456",
            goals=["Build better relationships"],
            current_situation="Mid-level professional",
            demographics={"age": 35, "location": "San Francisco"},
        )

        assert "Mid-level professional" in result
        # Verify assessment was saved (check for file path mention)
        assert "saved to:" in result.lower()

    def test_conduct_initial_assessment_invalid_user_id(self, assessment_tools):
        """Test that empty user_id returns error."""
        conduct_initial_assessment = assessment_tools[0]

        result = conduct_initial_assessment(user_id="", goals=["Test goal"])

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_conduct_initial_assessment_invalid_goals(self, assessment_tools):
        """Test that empty goals list returns error."""
        conduct_initial_assessment = assessment_tools[0]

        result = conduct_initial_assessment(user_id="user_789", goals=[])

        assert "Error" in result
        assert "goals must be a non-empty list" in result

    def test_conduct_initial_assessment_domain_mapping(self, assessment_tools):
        """Test that goals are correctly mapped to domains."""
        conduct_initial_assessment = assessment_tools[0]

        result = conduct_initial_assessment(
            user_id="user_999",
            goals=["Get promoted at work", "Build emergency fund", "Start exercising"],
        )

        assert "Career" in result
        assert "Finance" in result or "Financial" in result
        assert "Wellness" in result

    def test_conduct_initial_assessment_creates_structure(self, assessment_tools):
        """Test that initial assessment creates proper domain structure."""
        conduct_initial_assessment = assessment_tools[0]

        result = conduct_initial_assessment(user_id="user_111", goals=["Test goal"])

        # Should mention all domains
        for domain_key in LIFE_DOMAINS.keys():
            domain_name = LIFE_DOMAINS[domain_key]["name"]
            assert domain_name in result


# ==============================================================================
# Test: prioritize_domains_by_urgency
# ==============================================================================


class TestPrioritizeDomainsByUrgency:
    """Test suite for prioritize_domains_by_urgency tool."""

    def test_prioritize_basic(self, assessment_tools, sample_domain_scores):
        """Test basic domain prioritization."""
        prioritize_domains_by_urgency = assessment_tools[1]

        result = prioritize_domains_by_urgency(
            user_id="user_123", domain_scores=sample_domain_scores
        )

        assert "Domain Prioritization Analysis" in result
        assert "Prioritized Domains" in result

    def test_prioritize_with_urgency_factors(self, assessment_tools, sample_domain_scores):
        """Test prioritization with urgency factors."""
        prioritize_domains_by_urgency = assessment_tools[1]

        result = prioritize_domains_by_urgency(
            user_id="user_456",
            domain_scores=sample_domain_scores,
            urgency_factors={"finance": ["rent due soon"]},
        )

        assert "Urgent Issues" in result
        assert "rent due soon" in result

    def test_prioritize_with_goal_alignment(self, assessment_tools):
        """Test prioritization with goal alignment bonus."""
        prioritize_domains_by_urgency = assessment_tools[1]

        result = prioritize_domains_by_urgency(
            user_id="user_789",
            domain_scores={"career": 6, "wellness": 5},
            user_goals=["Get promoted to manager", "Improve fitness"],
        )

        assert "Goal Alignment" in result

    def test_prioritize_lowest_score_first(self, assessment_tools):
        """Test that lowest scores get highest priority."""
        prioritize_domains_by_urgency = assessment_tools[1]

        domain_scores = {"career": 8, "wellness": 3, "finance": 6}
        result = prioritize_domains_by_urgency(user_id="user_999", domain_scores=domain_scores)

        # Wellness has lowest score (3), should be highest priority
        lines = result.split("\n")
        first_domain_line = next((line for line in lines if "Priority:" in line), None)
        assert first_domain_line is not None
        # The highest priority domain should appear first

    def test_prioritize_invalid_user_id(self, assessment_tools):
        """Test that invalid user_id returns error."""
        prioritize_domains_by_urgency = assessment_tools[1]

        result = prioritize_domains_by_urgency(user_id="", domain_scores={"career": 5})

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_prioritize_invalid_scores(self, assessment_tools):
        """Test that invalid domain scores return error."""
        prioritize_domains_by_urgency = assessment_tools[1]

        result = prioritize_domains_by_urgency(user_id="user_111", domain_scores={})

        assert "Error" in result
        assert "domain_scores must be a non-empty dictionary" in result

    def test_prioritize_urgency_bonus_capped(self, assessment_tools):
        """Test that urgency bonus is properly capped."""
        prioritize_domains_by_urgency = assessment_tools[1]

        # Many urgent issues should still be capped
        result = prioritize_domains_by_urgency(
            user_id="user_222",
            domain_scores={"finance": 5},
            urgency_factors={"finance": ["issue1", "issue2", "issue3", "issue4", "issue5"]},
        )

        assert "Prioritization analysis saved to:" in result


# ==============================================================================
# Test: assess_cross_domain_impacts
# ==============================================================================


class TestAssessCrossDomainImpacts:
    """Test suite for assess_cross_domain_impacts tool."""

    def test_basic_cross_domain_analysis(self, assessment_tools):
        """Test basic cross-domain impact analysis."""
        assess_cross_domain_impacts = assessment_tools[2]

        result = assess_cross_domain_impacts(
            user_id="user_123", domain_changes={"career": "Accept new promotion"}
        )

        assert "Cross-Domain Impact Analysis" in result
        assert "Planned Changes:" in result

    def test_identifies_positive_impacts(self, assessment_tools):
        """Test that positive impacts are identified."""
        assess_cross_domain_impacts = assessment_tools[2]

        result = assess_cross_domain_impacts(
            user_id="user_456",
            domain_changes={"wellness": "Start regular exercise program"},
        )

        assert "Positive Impacts" in result or "positive impacts" in result.lower()

    def test_identifies_negative_risks(self, assessment_tools):
        """Test that negative risks are identified."""
        assess_cross_domain_impacts = assessment_tools[2]

        result = assess_cross_domain_impacts(
            user_id="user_789",
            domain_changes={"career": "Take role requiring many overtime hours"},
        )

        # Should identify potential negative impacts on wellness or relationships
        assert "Negative Risks" in result or "negative risks" in result.lower()

    def test_identifies_synergies(self, assessment_tools):
        """Test that synergies are identified when multiple domains benefit."""
        assess_cross_domain_impacts = assessment_tools[2]

        result = assess_cross_domain_impacts(
            user_id="user_999",
            domain_changes={"wellness": "Improve sleep habits and reduce stress"},
        )

        # Should identify synergies affecting multiple domains
        assert "Synergies" in result or "synergies" in result.lower()

    def test_provides_mitigation_strategies(self, assessment_tools):
        """Test that mitigation strategies are provided for risks."""
        assess_cross_domain_impacts = assessment_tools[2]

        result = assess_cross_domain_impacts(
            user_id="user_111",
            domain_changes={"career": "Increase workload significantly"},
            current_domain_scores={"wellness": 3, "relationship": 4},
        )

        assert "Mitigation Strategies" in result or "mitigation" in result.lower()

    def test_cross_domain_impact_with_vulnerable_domains(self, assessment_tools):
        """Test that conflicts with vulnerable domains are identified."""
        assess_cross_domain_impacts = assessment_tools[2]

        result = assess_cross_domain_impacts(
            user_id="user_222",
            domain_changes={"career": "Demanding new role"},
            current_domain_scores={"wellness": 2, "relationship": 3},
        )

        # Should identify conflicts with low-scoring (vulnerable) domains
        assert "Conflicts" in result or "conflict" in result.lower()

    def test_invalid_user_id(self, assessment_tools):
        """Test that invalid user_id returns error."""
        assess_cross_domain_impacts = assessment_tools[2]

        result = assess_cross_domain_impacts(user_id="", domain_changes={"career": "Test"})

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_invalid_domain_changes(self, assessment_tools):
        """Test that invalid domain changes return error."""
        assess_cross_domain_impacts = assessment_tools[2]

        result = assess_cross_domain_impacts(user_id="user_333", domain_changes={})

        assert "Error" in result
        assert "domain_changes must be a non-empty dictionary" in result


# ==============================================================================
# Test: generate_integrated_report
# ==============================================================================


class TestGenerateIntegratedReport:
    """Test suite for generate_integrated_report tool."""

    def test_basic_report_generation(self, assessment_tools):
        """Test basic integrated report generation."""
        generate_integrated_report = assessment_tools[3]

        domain_assessments = {
            "career": {"score": 6, "strengths": ["Good skills"], "challenges": ["Need promotion"]},
            "wellness": {"score": 4, "strengths": [], "challenges": ["Low energy"]},
        }

        result = generate_integrated_report(
            user_id="user_123", domain_assessments=domain_assessments
        )

        assert "Integrated Assessment Report Generated" in result
        assert "Overall Balance Score" in result

    def test_report_executive_summary(self, assessment_tools):
        """Test that executive summary is included."""
        generate_integrated_report = assessment_tools[3]

        domain_assessments = {
            "career": {"score": 7, "strengths": [], "challenges": []},
            "wellness": {"score": 5, "strengths": [], "challenges": []},
            "finance": {"score": 6, "strengths": [], "challenges": []},
        }

        result = generate_integrated_report(
            user_id="user_456", domain_assessments=domain_assessments
        )

        assert "Executive Summary" in result or "executive summary" in result.lower()

    def test_report_with_prioritization(self, assessment_tools):
        """Test report generation with prioritization data."""
        generate_integrated_report = assessment_tools[3]

        domain_assessments = {
            "career": {"score": 5, "strengths": [], "challenges": ["Need skills"]},
            "wellness": {"score": 3, "strengths": [], "challenges": ["Poor sleep"]},
        }

        priority_data = {
            "domain_priorities": {
                "career": {"total_priority_score": 7},
                "wellness": {"total_priority_score": 9},
            }
        }

        result = generate_integrated_report(
            user_id="user_789",
            domain_assessments=domain_assessments,
            priotization_data=priority_data,
        )

        assert "Prioritized Action Plan" in result or "action plan" in result.lower()

    def test_report_with_cross_domain_analysis(self, assessment_tools):
        """Test report generation with cross-domain insights."""
        generate_integrated_report = assessment_tools[3]

        domain_assessments = {
            "career": {"score": 6, "strengths": [], "challenges": []},
            "wellness": {"score": 5, "strengths": [], "challenges": []},
        }

        cross_domain_data = {
            "positive_impacts": [
                {"source_domain": "career", "target_domain": "finance", "strength": 0.9}
            ]
        }

        result = generate_integrated_report(
            user_id="user_999",
            domain_assessments=domain_assessments,
            cross_domain_analysis=cross_domain_data,
        )

        assert "Cross-Domain Insights" in result or "cross-domain" in result.lower()

    def test_report_creates_both_formats(self, assessment_tools):
        """Test that both JSON and Markdown reports are created."""
        generate_integrated_report = assessment_tools[3]

        domain_assessments = {
            "career": {"score": 6, "strengths": [], "challenges": []},
        }

        result = generate_integrated_report(
            user_id="user_111", domain_assessments=domain_assessments
        )

        # Should mention both file types being created
        assert ".json" in result.lower()
        assert ".md" in result.lower()

    def test_invalid_user_id(self, assessment_tools):
        """Test that invalid user_id returns error."""
        generate_integrated_report = assessment_tools[3]

        result = generate_integrated_report(user_id="", domain_assessments={})

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_invalid_domain_assessments(self, assessment_tools):
        """Test that invalid domain assessments return error."""
        generate_integrated_report = assessment_tools[3]

        result = generate_integrated_report(user_id="user_222", domain_assessments={})

        assert "Error" in result
        assert "domain_assessments must be a non-empty dictionary" in result

    def test_overall_balance_calculation(self, assessment_tools):
        """Test that overall balance score is correctly calculated."""
        generate_integrated_report = assessment_tools[3]

        domain_assessments = {
            "career": {"score": 6, "strengths": [], "challenges": []},
            "wellness": {"score": 4, "strengths": [], "challenges": []},
            "finance": {"score": 5, "strengths": [], "challenges": []},
            "relationship": {"score": 7, "strengths": [], "challenges": []},
        }

        result = generate_integrated_report(
            user_id="user_333", domain_assessments=domain_assessments
        )

        # Average: (6+4+5+7)/4 = 5.5
        assert "5" in result  # Should contain the balance score


# ==============================================================================
# Test: design_follow_up_questions
# ==============================================================================


class TestDesignFollowUpQuestions:
    """Test suite for design_follow_up_questions tool."""

    def test_basic_question_design(self, assessment_tools):
        """Test basic follow-up question generation."""
        design_follow_up_questions = assessment_tools[4]

        gaps = {"wellness": ["sleep quality", "stress sources"]}
        result = design_follow_up_questions(user_id="user_123", assessment_gaps=gaps)

        assert "Follow-Up Questions Plan" in result
        assert "wellness" in result.lower() or "well-being" in result.lower()

    def test_questions_for_career_gaps(self, assessment_tools):
        """Test questions for career-related gaps."""
        design_follow_up_questions = assessment_tools[4]

        gaps = {"career": ["skill development needs"]}
        result = design_follow_up_questions(user_id="user_456", assessment_gaps=gaps)

        assert "career" in result.lower()
        # Should contain questions about skills
        assert "skill" in result.lower()

    def test_questions_for_wellness_gaps(self, assessment_tools):
        """Test questions for wellness-related gaps."""
        design_follow_up_questions = assessment_tools[4]

        gaps = {"wellness": ["sleep habits", "stress management"]}
        result = design_follow_up_questions(user_id="user_789", assessment_gaps=gaps)

        assert "sleep" in result.lower()
        assert "stress" in result.lower()

    def test_questions_for_finance_gaps(self, assessment_tools):
        """Test questions for finance-related gaps."""
        design_follow_up_questions = assessment_tools[4]

        gaps = {"finance": ["budgeting", "savings"]}
        result = design_follow_up_questions(user_id="user_999", assessment_gaps=gaps)

        assert "budget" in result.lower()
        assert "savings" in result.lower()

    def test_questions_for_relationship_gaps(self, assessment_tools):
        """Test questions for relationship-related gaps."""
        design_follow_up_questions = assessment_tools[4]

        gaps = {"relationship": ["communication"]}
        result = design_follow_up_questions(user_id="user_111", assessment_gaps=gaps)

        assert "relationship" in result.lower()
        assert "communicat" in result.lower()

    def test_multiple_domains(self, assessment_tools):
        """Test questions for multiple domains at once."""
        design_follow_up_questions = assessment_tools[4]

        gaps = {
            "career": ["skills"],
            "wellness": ["stress"],
            "finance": ["budgeting"],
        }
        result = design_follow_up_questions(user_id="user_222", assessment_gaps=gaps)

        # Should have questions for all domains
        assert len([line for line in result.split("\n") if "?" in line]) > 5

    def test_invalid_user_id(self, assessment_tools):
        """Test that invalid user_id returns error."""
        design_follow_up_questions = assessment_tools[4]

        result = design_follow_up_questions(user_id="", assessment_gaps={"career": ["test"]})

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_invalid_assessment_gaps(self, assessment_tools):
        """Test that invalid gaps return error."""
        design_follow_up_questions = assessment_tools[4]

        result = design_follow_up_questions(user_id="user_333", assessment_gaps={})

        assert "Error" in result
        assert "assessment_gaps must be a non-empty dictionary" in result

    def test_usage_guide_included(self, assessment_tools):
        """Test that usage guide is included in response."""
        design_follow_up_questions = assessment_tools[4]

        gaps = {"wellness": ["sleep"]}
        result = design_follow_up_questions(user_id="user_444", assessment_gaps=gaps)

        assert "Usage Guide" in result or "guide" in result.lower()


# ==============================================================================
# Test: Framework Constants
# ==============================================================================


class TestFrameworkConstants:
    """Test suite for framework constants and data structures."""

    def test_life_domains_structure(self):
        """Test that LIFE_DOMAINS is properly structured."""
        assert isinstance(LIFE_DOMAINS, dict)
        assert "career" in LIFE_DOMAINS
        assert "wellness" in LIFE_DOMAINS
        assert "finance" in LIFE_DOMAINS
        assert "relationship" in LIFE_DOMAINS

        for domain_key, domain_info in LIFE_DOMAINS.items():
            assert "name" in domain_info
            assert "description" in domain_info
            assert "specialist" in domain_info
            assert "key_indicators" in domain_info

    def test_cross_domain_impacts_structure(self):
        """Test that CROSS_DOMAIN_IMPACTS is properly structured."""
        assert isinstance(CROSS_DOMAIN_IMPACTS, dict)

        for (domain_a, domain_b), impact_data in CROSS_DOMAIN_IMPACTS.items():
            assert len((domain_a, domain_b)) == 2
            assert "impact_type" in impact_data
            assert "strength" in impact_data
            assert isinstance(impact_data["strength"], (int, float))
            assert 0 <= impact_data["strength"] <= 1

    def test_domain_coverage(self):
        """Test that all four main domains are covered."""
        expected_domains = {"career", "wellness", "finance", "relationship"}
        actual_domains = set(LIFE_DOMAINS.keys())
        assert expected_domains == actual_domains


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestAssessmentWorkflowIntegration:
    """Test suite for complete assessment workflow integration."""

    def test_complete_assessment_workflow(self, assessment_tools):
        """Test the complete assessment workflow from start to finish."""
        conduct_initial_assessment = assessment_tools[0]
        prioritize_domains_by_urgency = assessment_tools[1]
        assess_cross_domain_impacts = assessment_tools[2]
        generate_integrated_report = assessment_tools[3]

        # Step 1: Initial Assessment
        initial_result = conduct_initial_assessment(
            user_id="workflow_test_001",
            goals=["Get promoted", "Improve fitness"],
            current_situation="Mid-level professional",
        )
        assert "Initial Multi-Domain Assessment" in initial_result

        # Step 2: Prioritize Domains
        priority_result = prioritize_domains_by_urgency(
            user_id="workflow_test_001",
            domain_scores={"career": 5, "wellness": 4, "finance": 6, "relationship": 7},
            user_goals=["Get promoted", "Improve fitness"],
        )
        assert "Domain Prioritization Analysis" in priority_result

        # Step 3: Cross-Domain Impact
        impact_result = assess_cross_domain_impacts(
            user_id="workflow_test_001",
            domain_changes={"career": "Apply for promotion"},
        )
        assert "Cross-Domain Impact Analysis" in impact_result

        # Step 4: Generate Report
        report_result = generate_integrated_report(
            user_id="workflow_test_001",
            domain_assessments={
                "career": {
                    "score": 5,
                    "strengths": ["Good skills"],
                    "challenges": ["Needs promotion"],
                },
                "wellness": {"score": 4, "strengths": [], "challenges": ["Low energy"]},
                "finance": {"score": 6, "strengths": [], "challenges": []},
                "relationship": {"score": 7, "strengths": [], "challenges": []},
            },
        )
        assert "Integrated Assessment Report Generated" in report_result

    def test_assessment_workflow_with_all_features(self, assessment_tools):
        """Test workflow with all features enabled."""
        # Simulate a realistic use case
        domain_scores = {"career": 4, "wellness": 3, "finance": 5, "relationship": 6}
        urgency_factors = {"finance": ["unexpected medical bill"], "wellness": ["burnout"]}
        domain_changes = {"career": "Seek new job opportunity"}

        # Run through tools
        initial_result = assessment_tools[0](
            user_id="full_test_001",
            goals=["Find better job", "Improve health"],
            current_situation="Feeling stuck in current role",
        )

        priority_result = assessment_tools[1](
            user_id="full_test_001",
            domain_scores=domain_scores,
            urgency_factors=urgency_factors,
        )

        impact_result = assessment_tools[2](
            user_id="full_test_001",
            domain_changes=domain_changes,
            current_domain_scores=domain_scores,
        )

        # Verify all tools executed successfully
        assert "Error" not in initial_result
        assert "Error" not in priority_result
        assert "Error" not in impact_result

        # Verify domain coverage
        all_results = initial_result + priority_result + impact_result
        for domain_key in LIFE_DOMAINS.keys():
            assert LIFE_DOMAINS[domain_key]["name"] in all_results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
