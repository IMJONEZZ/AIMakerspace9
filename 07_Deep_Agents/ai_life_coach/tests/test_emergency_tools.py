"""
Test suite for Emergency Support Protocol.

This module tests all emergency tools including:
- Crisis keyword detection
- Resource provision
- Safety plan generation
- Follow-up check-ins
- Crisis logging
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.emergency_tools import (
    create_emergency_tools,
    detect_crisis_keywords,
    CrisisDetectionResult,
    CrisisLevel,
    CrisisType,
    CrisisLogEntry,
    SafetyPlan,
    FollowUpCheckin,
    get_appropriate_resources,
    CRISIS_RESOURCES,
    SAFETY_PLAN_TEMPLATE,
)


class MockBackend:
    """Mock backend for testing."""

    def __init__(self, temp_dir):
        self.root_dir = temp_dir
        self.files = {}

    def read_file(self, path):
        if path in self.files:
            return self.files[path]
        raise FileNotFoundError(f"File not found: {path}")

    def write_file(self, path, content):
        self.files[path] = content

    def file_exists(self, path):
        return path in self.files


class TestCrisisDetection(unittest.TestCase):
    """Test crisis keyword detection."""

    def test_no_crisis_detected(self):
        """Test that normal messages don't trigger crisis detection."""
        result = detect_crisis_keywords("I'm having a good day today!")

        self.assertFalse(result.is_crisis)
        self.assertEqual(result.crisis_level, CrisisLevel.NONE)
        self.assertEqual(len(result.crisis_types), 0)
        self.assertFalse(result.requires_immediate_action)

    def test_suicide_ideation_critical(self):
        """Test detection of critical suicide ideation keywords."""
        result = detect_crisis_keywords("I want to kill myself")

        self.assertTrue(result.is_crisis)
        self.assertEqual(result.crisis_level, CrisisLevel.CRITICAL)
        self.assertIn(CrisisType.SUICIDE_IDEATION, result.crisis_types)
        self.assertTrue(result.requires_immediate_action)
        self.assertIn("kill myself", result.matched_keywords)

    def test_suicide_ideation_high(self):
        """Test detection of high-severity suicide keywords."""
        result = detect_crisis_keywords("I'm having suicidal thoughts")

        self.assertTrue(result.is_crisis)
        self.assertEqual(result.crisis_level, CrisisLevel.HIGH)
        self.assertIn(CrisisType.SUICIDE_IDEATION, result.crisis_types)
        self.assertTrue(result.requires_immediate_action)

    def test_self_harm_detection(self):
        """Test detection of self-harm keywords."""
        result = detect_crisis_keywords("I've been cutting myself")

        self.assertTrue(result.is_crisis)
        self.assertEqual(result.crisis_level, CrisisLevel.CRITICAL)
        self.assertIn(CrisisType.SELF_HARM, result.crisis_types)

    def test_abuse_detection(self):
        """Test detection of abuse keywords."""
        result = detect_crisis_keywords("I'm being abused by my partner")

        self.assertTrue(result.is_crisis)
        self.assertEqual(result.crisis_level, CrisisLevel.CRITICAL)
        self.assertIn(CrisisType.ABUSE, result.crisis_types)

    def test_domestic_violence_detection(self):
        """Test detection of domestic violence keywords."""
        result = detect_crisis_keywords("I'm experiencing domestic violence")

        self.assertTrue(result.is_crisis)
        self.assertEqual(result.crisis_level, CrisisLevel.CRITICAL)
        self.assertIn(CrisisType.DOMESTIC_VIOLENCE, result.crisis_types)

    def test_multiple_crisis_types(self):
        """Test detection of multiple crisis types."""
        result = detect_crisis_keywords("I've been cutting myself and I want to kill myself")

        self.assertTrue(result.is_crisis)
        self.assertEqual(result.crisis_level, CrisisLevel.CRITICAL)
        self.assertIn(CrisisType.SELF_HARM, result.crisis_types)
        self.assertIn(CrisisType.SUICIDE_IDEATION, result.crisis_types)

    def test_confidence_scoring(self):
        """Test that confidence scores are calculated correctly."""
        # Single moderate keyword
        result = detect_crisis_keywords("I'm feeling hopeless")
        self.assertTrue(result.confidence_score > 0)

        # Multiple critical keywords
        result = detect_crisis_keywords("I want to kill myself and end my life")
        self.assertTrue(result.confidence_score > 0.5)

    def test_empty_input(self):
        """Test handling of empty input."""
        result = detect_crisis_keywords("")
        self.assertFalse(result.is_crisis)

        result = detect_crisis_keywords(None)
        self.assertFalse(result.is_crisis)


class TestResourceProvision(unittest.TestCase):
    """Test crisis resource provision."""

    def test_get_appropriate_resources_suicide(self):
        """Test getting resources for suicide ideation."""
        resources = get_appropriate_resources([CrisisType.SUICIDE_IDEATION])

        resource_names = [r["name"] for r in resources]
        self.assertIn("988 Suicide & Crisis Lifeline", resource_names)
        self.assertIn("Crisis Text Line", resource_names)

    def test_get_appropriate_resources_self_harm(self):
        """Test getting resources for self-harm."""
        resources = get_appropriate_resources([CrisisType.SELF_HARM])

        resource_names = [r["name"] for r in resources]
        self.assertIn("988 Suicide & Crisis Lifeline", resource_names)

    def test_get_appropriate_resources_domestic_violence(self):
        """Test getting resources for domestic violence."""
        resources = get_appropriate_resources([CrisisType.DOMESTIC_VIOLENCE])

        resource_names = [r["name"] for r in resources]
        self.assertIn("National Domestic Violence Hotline", resource_names)

    def test_get_appropriate_resources_no_types(self):
        """Test getting default resources when no types specified."""
        resources = get_appropriate_resources([])

        resource_names = [r["name"] for r in resources]
        self.assertIn("988 Suicide & Crisis Lifeline", resource_names)
        self.assertTrue(len(resources) > 0)


class TestSafetyPlan(unittest.TestCase):
    """Test safety plan functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backend = MockBackend(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_safety_plan_creation(self):
        """Test creating a safety plan."""
        plan = SafetyPlan(
            user_id="user_123",
            sections={
                "warning_signs": {"title": "Warning Signs", "items": ["Can't sleep"]},
                "coping_strategies": {"title": "Coping", "items": ["Go for walks"]},
            },
        )

        self.assertEqual(plan.user_id, "user_123")
        self.assertTrue(plan.plan_id.startswith("safety_user_123_"))
        self.assertTrue(plan.is_active)
        self.assertEqual(len(plan.sections), 2)

    def test_safety_plan_to_dict(self):
        """Test converting safety plan to dictionary."""
        plan = SafetyPlan(
            user_id="user_123",
            sections={"test": {"title": "Test", "items": []}},
        )

        data = plan.to_dict()

        self.assertEqual(data["user_id"], "user_123")
        self.assertIn("plan_id", data)
        self.assertIn("created_at", data)
        self.assertIn("sections", data)

    def test_safety_plan_from_dict(self):
        """Test creating safety plan from dictionary."""
        data = {
            "user_id": "user_123",
            "plan_id": "safety_test_123",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "sections": {"test": {"title": "Test", "items": []}},
            "is_active": True,
        }

        plan = SafetyPlan.from_dict(data)

        self.assertEqual(plan.user_id, "user_123")
        self.assertEqual(plan.plan_id, "safety_test_123")
        self.assertTrue(plan.is_active)


class TestFollowUpCheckin(unittest.TestCase):
    """Test follow-up check-in functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backend = MockBackend(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_checkin_creation(self):
        """Test creating a follow-up check-in."""
        checkin = FollowUpCheckin(
            user_id="user_123",
            related_crisis_id="crisis_123",
        )

        self.assertEqual(checkin.user_id, "user_123")
        self.assertEqual(checkin.related_crisis_id, "crisis_123")
        self.assertEqual(checkin.status, "scheduled")
        self.assertIsNone(checkin.wellbeing_score)

    def test_checkin_completion(self):
        """Test completing a check-in."""
        checkin = FollowUpCheckin(
            user_id="user_123",
            related_crisis_id="crisis_123",
        )

        checkin.status = "completed"
        checkin.wellbeing_score = 7
        checkin.completed_at = datetime.now().isoformat()

        self.assertEqual(checkin.status, "completed")
        self.assertEqual(checkin.wellbeing_score, 7)
        self.assertIsNotNone(checkin.completed_at)


class TestCrisisLogEntry(unittest.TestCase):
    """Test crisis log entry functionality."""

    def test_log_entry_creation(self):
        """Test creating a crisis log entry."""
        entry = CrisisLogEntry(
            user_id="user_123",
            crisis_level="critical",
            crisis_types=["suicide_ideation"],
            actions_taken=["provided_resources"],
            resources_provided=["988_lifeline"],
        )

        self.assertEqual(entry.crisis_level, "critical")
        self.assertEqual(len(entry.crisis_types), 1)
        self.assertTrue(entry.requires_follow_up)
        self.assertIn("crisis_user_123_", entry.crisis_id)

    def test_log_entry_to_dict(self):
        """Test converting log entry to dictionary."""
        entry = CrisisLogEntry(
            user_id="user_123",
            crisis_level="high",
            crisis_types=["self_harm"],
            actions_taken=["provided_resources", "scheduled_followup"],
            resources_provided=["988_lifeline", "crisis_text_line"],
        )

        data = entry.to_dict()

        self.assertEqual(data["crisis_level"], "high")
        self.assertEqual(data["crisis_types"], ["self_harm"])
        self.assertEqual(len(data["actions_taken"]), 2)
        self.assertEqual(len(data["resources_provided"]), 2)
        # user_id should NOT be in the log for privacy
        self.assertNotIn("user_id", data)


class TestEmergencyToolsIntegration(unittest.TestCase):
    """Integration tests for emergency tools."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backend = MockBackend(self.temp_dir)

        # Create emergency tools
        (
            self.analyze_crisis_risk,
            self.get_immediate_resources,
            self.create_safety_plan,
            self.get_safety_plan_template,
            self.schedule_followup_checkin,
            self.complete_followup_checkin,
            self.get_crisis_protocol_guidance,
            self.generate_crisis_response,
        ) = create_emergency_tools(self.backend)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_analyze_crisis_risk_critical(self):
        """Test analyzing crisis risk with critical message."""
        result = self.analyze_crisis_risk.invoke({"user_message": "I want to kill myself"})

        self.assertIn("CRISIS DETECTED", result)
        self.assertIn("CRITICAL", result)
        self.assertIn("IMMEDIATE ACTION REQUIRED", result)

    def test_analyze_crisis_risk_no_crisis(self):
        """Test analyzing message with no crisis indicators."""
        result = self.analyze_crisis_risk.invoke({"user_message": "I'm having a good day!"})

        self.assertIn("No crisis indicators detected", result)

    def test_analyze_crisis_risk_invalid_input(self):
        """Test analyzing with invalid input."""
        result = self.analyze_crisis_risk.invoke({"user_message": ""})
        self.assertIn("Error", result)

    def test_get_immediate_resources(self):
        """Test getting immediate crisis resources."""
        result = self.get_immediate_resources.invoke({"crisis_types": ["suicide_ideation"]})

        self.assertIn("988 Suicide & Crisis Lifeline", result)
        self.assertIn("Crisis Text Line", result)
        self.assertIn("911", result)
        self.assertIn("DISCLAIMER", result)

    def test_get_immediate_resources_default(self):
        """Test getting resources without specifying crisis types."""
        result = self.get_immediate_resources.invoke({})

        self.assertIn("988 Suicide & Crisis Lifeline", result)
        self.assertTrue(len(result) > 0)

    def test_create_safety_plan(self):
        """Test creating a safety plan."""
        result = self.create_safety_plan.invoke(
            {
                "user_id": "user_123",
                "warning_signs": ["Can't sleep", "Feeling hopeless"],
                "coping_strategies": ["Go for a walk", "Listen to music"],
                "social_contacts": [{"name": "Sarah", "phone": "555-0123"}],
                "professional_contacts": [{"name": "Dr. Smith", "phone": "555-0456"}],
                "reasons_for_living": ["My family", "My dog"],
            }
        )

        self.assertIn("SAFETY PLAN CREATED", result)
        self.assertIn("Warning Signs", result)
        self.assertIn("Sarah", result)
        self.assertIn("Dr. Smith", result)
        self.assertIn("2 warning signs", result)

        # Verify plan was saved
        plan_path = "crisis_support/safety_plans/user_123.json"
        self.assertTrue(self.backend.file_exists(plan_path))

    def test_create_safety_plan_invalid_input(self):
        """Test creating safety plan with invalid input."""
        result = self.create_safety_plan.invoke(
            {
                "user_id": "",
                "warning_signs": [],
                "coping_strategies": [],
                "social_contacts": [],
                "professional_contacts": [],
                "reasons_for_living": [],
            }
        )

        self.assertIn("Error", result)

    def test_get_safety_plan_template(self):
        """Test getting safety plan template."""
        result = self.get_safety_plan_template.invoke({})

        self.assertIn("SAFETY PLAN TEMPLATE", result)
        self.assertIn("Warning Signs", result)
        self.assertIn("Internal Coping Strategies", result)
        self.assertIn("Social Distractions", result)
        self.assertIn("Reasons for Living", result)

    def test_schedule_followup_checkin(self):
        """Test scheduling a follow-up check-in."""
        result = self.schedule_followup_checkin.invoke(
            {
                "user_id": "user_123",
                "related_crisis_id": "crisis_user_123_20240101_120000",
                "hours_from_now": 24,
            }
        )

        self.assertIn("FOLLOW-UP CHECK-IN SCHEDULED", result)
        self.assertIn("crisis_user_123_20240101_120000", result)
        self.assertIn("Status: Scheduled", result)

        # Verify check-in was saved
        checkin_path = "crisis_support/checkins/user_123.json"
        self.assertTrue(self.backend.file_exists(checkin_path))

    def test_schedule_followup_checkin_invalid_input(self):
        """Test scheduling check-in with invalid input."""
        result = self.schedule_followup_checkin.invoke(
            {
                "user_id": "",
                "related_crisis_id": "crisis_123",
                "hours_from_now": 24,
            }
        )

        self.assertIn("Error", result)

    def test_complete_followup_checkin(self):
        """Test completing a follow-up check-in."""
        # First schedule a check-in
        self.schedule_followup_checkin.invoke(
            {
                "user_id": "user_123",
                "related_crisis_id": "crisis_123",
                "hours_from_now": 24,
            }
        )

        # Get the check-in ID from saved data
        checkin_data = json.loads(self.backend.files["crisis_support/checkins/user_123.json"])
        checkin_id = checkin_data["checkins"][0]["checkin_id"]

        # Complete the check-in
        result = self.complete_followup_checkin.invoke(
            {
                "user_id": "user_123",
                "checkin_id": checkin_id,
                "wellbeing_score": 7,
                "notes": "User is feeling better",
            }
        )

        self.assertIn("FOLLOW-UP CHECK-IN COMPLETED", result)
        self.assertIn("7/10", result)
        self.assertIn("User is feeling better", result)

    def test_complete_followup_checkin_invalid_score(self):
        """Test completing check-in with invalid wellbeing score."""
        result = self.complete_followup_checkin.invoke(
            {
                "user_id": "user_123",
                "checkin_id": "checkin_123",
                "wellbeing_score": 15,  # Invalid: should be 1-10
                "notes": "",
            }
        )

        self.assertIn("Error", result)

    def test_get_crisis_protocol_guidance(self):
        """Test getting crisis protocol guidance."""
        result = self.get_crisis_protocol_guidance.invoke({})

        self.assertIn("CRISIS PROTOCOL", result)
        self.assertIn("DISCLAIMER", result)
        self.assertIn("988", result)
        self.assertIn("SAFETY PLANNING", result)
        self.assertIn("PRIVACY", result)

    def test_generate_crisis_response_critical(self):
        """Test generating crisis response for critical level."""
        result = self.generate_crisis_response.invoke(
            {"crisis_level": "critical", "crisis_types": ["suicide_ideation"]}
        )

        self.assertIn("really concerned", result)
        self.assertIn("988", result)
        self.assertIn("911", result)
        self.assertIn("crisis counselors", result)

    def test_generate_crisis_response_high(self):
        """Test generating crisis response for high level."""
        result = self.generate_crisis_response.invoke(
            {"crisis_level": "high", "crisis_types": ["self_harm"]}
        )

        self.assertIn("significant pain", result)
        self.assertIn("988", result)
        self.assertIn("confidential support", result)

    def test_generate_crisis_response_moderate(self):
        """Test generating crisis response for moderate level."""
        result = self.generate_crisis_response.invoke(
            {"crisis_level": "moderate", "crisis_types": []}
        )

        self.assertIn("difficult time", result)
        self.assertIn("988", result)
        self.assertIn("safety plan", result)

    def test_generate_crisis_response_low(self):
        """Test generating response for low/unknown level."""
        result = self.generate_crisis_response.invoke({"crisis_level": "low", "crisis_types": []})

        self.assertIn("Thank you for sharing", result)
        self.assertIn("988", result)


class TestSafetyPlanTemplate(unittest.TestCase):
    """Test safety plan template constants."""

    def test_template_structure(self):
        """Test that template has all required sections."""
        required_sections = [
            "warning_signs",
            "coping_strategies",
            "social_distractions",
            "family_friends",
            "professional_resources",
            "environmental_safety",
            "reasons_for_living",
        ]

        for section in required_sections:
            self.assertIn(section, SAFETY_PLAN_TEMPLATE)
            self.assertIn("title", SAFETY_PLAN_TEMPLATE[section])
            self.assertIn("prompt", SAFETY_PLAN_TEMPLATE[section])
            self.assertIn("examples", SAFETY_PLAN_TEMPLATE[section])


class TestCrisisResources(unittest.TestCase):
    """Test crisis resources directory."""

    def test_988_lifeline(self):
        """Test 988 Lifeline resource."""
        resource = CRISIS_RESOURCES["988_lifeline"]

        self.assertEqual(resource["name"], "988 Suicide & Crisis Lifeline")
        self.assertEqual(resource["number"], "988")
        self.assertEqual(resource["available"], "24/7")
        self.assertIn(CrisisType.SUICIDE_IDEATION, resource["for_crisis_types"])

    def test_crisis_text_line(self):
        """Test Crisis Text Line resource."""
        resource = CRISIS_RESOURCES["crisis_text_line"]

        self.assertEqual(resource["name"], "Crisis Text Line")
        self.assertEqual(resource["number"], "Text HOME to 741741")
        self.assertEqual(resource["available"], "24/7")

    def test_emergency_services(self):
        """Test Emergency Services resource."""
        resource = CRISIS_RESOURCES["emergency_services"]

        self.assertEqual(resource["name"], "Emergency Services")
        self.assertEqual(resource["number"], "911")
        self.assertEqual(resource["available"], "24/7")


if __name__ == "__main__":
    unittest.main()
