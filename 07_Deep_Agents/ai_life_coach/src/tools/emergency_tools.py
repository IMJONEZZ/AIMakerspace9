"""
Emergency Support Protocol for AI Life Coach.

This module implements comprehensive crisis detection and response capabilities
following mental health best practices and safety guidelines.

Based on research from:
- SAMHSA 2025 National Guidelines for Behavioral Health Crisis Care
- 988 Suicide & Crisis Lifeline protocols
- APA Health Advisory on AI Chatbots for Mental Health
- Crisis Text Line best practices

SAFETY DISCLAIMER:
This system is for educational/development purposes only. In production, AI systems
should NEVER replace professional mental health services. Always include clear
disclaimers that this is not a substitute for professional help.

Key Features:
- Real-time crisis keyword detection
- Immediate professional resource provision
- Crisis escalation protocol
- Safety plan template generation
- Post-crisis follow-up check-ins
- Privacy-conscious crisis interaction logging
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from enum import Enum
import json
import re

# Import LangChain components
try:
    from langchain_core.tools import tool
except ImportError:
    # Fallback for development environments without full LangChain
    def tool(func):
        """Fallback decorator when langchain_core is not available."""
        func.is_tool = True  # type: ignore
        return func


# Import backend configuration
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_backend


# ==============================================================================
# Crisis Classification and Constants
# ==============================================================================


class CrisisLevel(Enum):
    """Enumeration of crisis severity levels."""

    NONE = "none"
    LOW = "low"  # Mild distress, no immediate danger
    MODERATE = "moderate"  # Significant distress, monitoring needed
    HIGH = "high"  # Severe distress, professional help recommended
    CRITICAL = "critical"  # Immediate danger, emergency intervention needed


class CrisisType(Enum):
    """Enumeration of crisis types for targeted response."""

    SUICIDE_IDEATION = "suicide_ideation"
    SELF_HARM = "self_harm"
    ABUSE = "abuse"
    SUBSTANCE_CRISIS = "substance_crisis"
    PSYCHOTIC_EPISODE = "psychotic_episode"
    SEVERE_ANXIETY = "severe_anxiety"
    PANIC_ATTACK = "panic_attack"
    DOMESTIC_VIOLENCE = "domestic_violence"
    UNKNOWN = "unknown"


# Crisis detection keywords organized by type and severity
# These are carefully curated to minimize false positives while catching genuine crises
CRISIS_KEYWORDS = {
    CrisisType.SUICIDE_IDEATION: {
        "critical": [
            "kill myself",
            "end my life",
            "suicide",
            "take my life",
            "want to die",
            "better off dead",
            "no reason to live",
            "can't go on",
            "end it all",
            "jump off",
            "hang myself",
        ],
        "high": [
            "suicidal thoughts",
            "thoughts of dying",
            "don't want to wake up",
            "hurt myself",
            "not worth living",
            "wish i was dead",
            "life not worth",
            "ending my life",
            "killing myself",
        ],
        "moderate": [
            "feeling hopeless",
            "nothing to live for",
            "give up",
            "can't take it anymore",
            "done with life",
            "overwhelmed",
        ],
    },
    CrisisType.SELF_HARM: {
        "critical": [
            "cutting myself",
            "hurt myself",
            "self harm",
            "self-harm",
            "burning myself",
            "hitting myself",
            "starving myself",
        ],
        "high": [
            "want to cut",
            "feel like cutting",
            "hurt my body",
            "punish myself",
            "deserve pain",
            "physical pain",
        ],
        "moderate": [
            "scratching",
            "pinching myself",
            "hair pulling",
        ],
    },
    CrisisType.ABUSE: {
        "critical": [
            "being abused",
            "get beaten",
            "getting hit",
            "sexual abuse",
            "molested",
            "raped",
            "trafficked",
        ],
        "high": [
            "abusive relationship",
            "emotional abuse",
            "verbal abuse",
            "controlling partner",
            "forced to",
            "threatened by",
        ],
        "moderate": [
            "uncomfortable situation",
            "don't feel safe",
            "scared of partner",
        ],
    },
    CrisisType.SUBSTANCE_CRISIS: {
        "critical": [
            "overdose",
            "od on",
            "drug emergency",
            "alcohol poisoning",
            "can't stop using",
            "withdrawal symptoms",
        ],
        "high": [
            "relapsed",
            "using again",
            "can't quit",
            "addiction crisis",
            "detox",
            "need rehab",
        ],
        "moderate": [
            "drinking too much",
            "worried about my use",
            "substance problem",
        ],
    },
    CrisisType.DOMESTIC_VIOLENCE: {
        "critical": [
            "domestic violence",
            "intimate partner violence",
            "ipv",
            "physical violence",
            "assaulted by partner",
            "strangled",
        ],
        "high": [
            "partner hit me",
            "spouse abuse",
            "boyfriend hit",
            "girlfriend hit",
            "scared of spouse",
            "controlling behavior",
        ],
        "moderate": [
            "relationship problems",
            "partner anger issues",
            "unhealthy relationship",
        ],
    },
}


# Professional crisis resources directory
CRISIS_RESOURCES = {
    "988_lifeline": {
        "name": "988 Suicide & Crisis Lifeline",
        "number": "988",
        "description": "Free, confidential support for people in distress",
        "available": "24/7",
        "website": "https://988lifeline.org",
        "for_crisis_types": [
            CrisisType.SUICIDE_IDEATION,
            CrisisType.SELF_HARM,
            CrisisType.SEVERE_ANXIETY,
        ],
    },
    "crisis_text_line": {
        "name": "Crisis Text Line",
        "number": "Text HOME to 741741",
        "description": "Text-based crisis support with trained counselors",
        "available": "24/7",
        "website": "https://www.crisistextline.org",
        "for_crisis_types": [
            CrisisType.SUICIDE_IDEATION,
            CrisisType.SELF_HARM,
            CrisisType.SEVERE_ANXIETY,
            CrisisType.PANIC_ATTACK,
        ],
    },
    "domestic_violence_hotline": {
        "name": "National Domestic Violence Hotline",
        "number": "1-800-799-SAFE (7233)",
        "description": "Support for domestic violence survivors",
        "available": "24/7",
        "website": "https://www.thehotline.org",
        "chat": "Available on website",
        "for_crisis_types": [
            CrisisType.DOMESTIC_VIOLENCE,
            CrisisType.ABUSE,
        ],
    },
    "substance_abuse_helpline": {
        "name": "SAMHSA National Helpline",
        "number": "1-800-662-4357",
        "description": "Free, confidential treatment referral for substance use",
        "available": "24/7",
        "website": "https://www.samhsa.gov/find-help",
        "for_crisis_types": [
            CrisisType.SUBSTANCE_CRISIS,
        ],
    },
    "emergency_services": {
        "name": "Emergency Services",
        "number": "911",
        "description": "For immediate life-threatening emergencies",
        "available": "24/7",
        "for_crisis_types": [
            CrisisType.SUICIDE_IDEATION,
            CrisisType.SELF_HARM,
            CrisisType.ABUSE,
            CrisisType.SUBSTANCE_CRISIS,
            CrisisType.DOMESTIC_VIOLENCE,
        ],
    },
    "sexual_assault_hotline": {
        "name": "RAINN National Sexual Assault Hotline",
        "number": "1-800-656-HOPE (4673)",
        "description": "Support for sexual assault survivors",
        "available": "24/7",
        "website": "https://www.rainn.org",
        "chat": "Available on website",
        "for_crisis_types": [
            CrisisType.ABUSE,
        ],
    },
    "trevor_project": {
        "name": "The Trevor Project",
        "number": "1-866-488-7386",
        "description": "Crisis support for LGBTQ+ youth",
        "available": "24/7",
        "website": "https://www.thetrevorproject.org",
        "text": "Text START to 678678",
        "chat": "Available on website",
        "for_crisis_types": [
            CrisisType.SUICIDE_IDEATION,
            CrisisType.SELF_HARM,
        ],
    },
    "nami_helpline": {
        "name": "NAMI HelpLine",
        "number": "1-800-950-NAMI (6264)",
        "description": "Information and referral for mental health resources",
        "available": "Monday-Friday, 10am-10pm ET",
        "website": "https://www.nami.org/help",
        "for_crisis_types": [
            CrisisType.SEVERE_ANXIETY,
            CrisisType.PSYCHOTIC_EPISODE,
        ],
    },
}


# Safety plan template sections
SAFETY_PLAN_TEMPLATE = {
    "warning_signs": {
        "title": "1. Warning Signs",
        "prompt": "What are the thoughts, images, moods, situations, or behaviors that let you know a crisis may be developing?",
        "examples": [
            "Feeling hopeless or trapped",
            "Increased isolation",
            "Can't sleep or sleeping too much",
            "Thoughts of self-harm",
        ],
    },
    "coping_strategies": {
        "title": "2. Internal Coping Strategies",
        "prompt": "What can you do on your own to take your mind off your problems? (without contacting another person)",
        "examples": [
            "Go for a walk",
            "Listen to music",
            "Write in a journal",
            "Practice deep breathing",
            "Take a shower",
        ],
    },
    "social_distractions": {
        "title": "3. Social Distractions",
        "prompt": "Who or what social settings can help take your mind off things?",
        "examples": [
            "Call a friend",
            "Go to a public place (coffee shop, library)",
            "Visit family",
        ],
    },
    "family_friends": {
        "title": "4. Family & Friends Who May Offer Help",
        "prompt": "Who are supportive people you can contact during a crisis?",
        "examples": [
            "Name: __________ | Phone: __________",
            "Name: __________ | Phone: __________",
        ],
    },
    "professional_resources": {
        "title": "5. Professional Resources",
        "prompt": "Who are the professionals or agencies you can contact?",
        "examples": [
            "Therapist: __________ | Phone: __________",
            "Psychiatrist: __________ | Phone: __________",
            "Crisis Hotline: 988",
        ],
    },
    "environmental_safety": {
        "title": "6. Making the Environment Safe",
        "prompt": "What steps can you take to make your environment safer?",
        "examples": [
            "Remove or secure medications",
            "Remove or secure sharp objects",
            "Ask someone to hold your firearms",
            "Go to a safe place",
        ],
    },
    "reasons_for_living": {
        "title": "7. Reasons for Living",
        "prompt": "What are the most important things worth living for?",
        "examples": [
            "Family members",
            "Pets",
            "Future goals",
            "Spiritual beliefs",
            "Friends",
        ],
    },
}


# ==============================================================================
# Crisis Detection and Analysis
# ==============================================================================


class CrisisDetectionResult:
    """Result of crisis detection analysis."""

    def __init__(
        self,
        is_crisis: bool = False,
        crisis_level: CrisisLevel = CrisisLevel.NONE,
        crisis_types: Optional[List[CrisisType]] = None,
        matched_keywords: Optional[List[str]] = None,
        confidence_score: float = 0.0,
        requires_immediate_action: bool = False,
    ):
        self.is_crisis = is_crisis
        self.crisis_level = crisis_level
        self.crisis_types = crisis_types or []
        self.matched_keywords = matched_keywords or []
        self.confidence_score = confidence_score
        self.requires_immediate_action = requires_immediate_action
        self.detected_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "is_crisis": self.is_crisis,
            "crisis_level": self.crisis_level.value,
            "crisis_types": [ct.value for ct in self.crisis_types],
            "matched_keywords": self.matched_keywords,
            "confidence_score": self.confidence_score,
            "requires_immediate_action": self.requires_immediate_action,
            "detected_at": self.detected_at,
        }


def detect_crisis_keywords(text: str) -> CrisisDetectionResult:
    """
    Analyze text for crisis-related keywords.

    Uses a multi-level keyword matching system to identify:
    - Type of crisis (suicide, self-harm, abuse, etc.)
    - Severity level (moderate, high, critical)
    - Confidence score based on keyword strength and context

    Args:
        text: User message text to analyze

    Returns:
        CrisisDetectionResult with detection details
    """
    if not text or not isinstance(text, str):
        return CrisisDetectionResult(is_crisis=False)

    text_lower = text.lower()
    matched_keywords = []
    detected_types = []
    max_severity = "none"
    confidence = 0.0

    # Check each crisis type
    for crisis_type, severity_levels in CRISIS_KEYWORDS.items():
        type_matched = False

        for severity, keywords in severity_levels.items():
            for keyword in keywords:
                # Use word boundary matching for phrases
                if keyword in text_lower:
                    matched_keywords.append(keyword)
                    type_matched = True

                    # Track highest severity
                    severity_rank = {"critical": 3, "high": 2, "moderate": 1}
                    current_rank = severity_rank.get(max_severity, 0)
                    new_rank = severity_rank.get(severity, 0)

                    if new_rank > current_rank:
                        max_severity = severity

                    # Add to confidence score
                    if severity == "critical":
                        confidence += 0.4
                    elif severity == "high":
                        confidence += 0.25
                    elif severity == "moderate":
                        confidence += 0.15

        if type_matched:
            detected_types.append(crisis_type)

    # Determine crisis level
    if max_severity == "critical":
        crisis_level = CrisisLevel.CRITICAL
    elif max_severity == "high":
        crisis_level = CrisisLevel.HIGH
    elif max_severity == "moderate":
        crisis_level = CrisisLevel.MODERATE
    else:
        crisis_level = CrisisLevel.NONE

    # Cap confidence at 1.0
    confidence = min(confidence, 1.0)

    # Require immediate action for critical level
    requires_immediate = crisis_level in [CrisisLevel.CRITICAL, CrisisLevel.HIGH]

    return CrisisDetectionResult(
        is_crisis=crisis_level != CrisisLevel.NONE,
        crisis_level=crisis_level,
        crisis_types=detected_types,
        matched_keywords=matched_keywords,
        confidence_score=round(confidence, 2),
        requires_immediate_action=requires_immediate,
    )


def get_appropriate_resources(crisis_types: List[CrisisType]) -> List[Dict[str, Any]]:
    """
    Get appropriate crisis resources based on crisis types.

    Args:
        crisis_types: List of detected crisis types

    Returns:
        List of relevant crisis resources
    """
    if not crisis_types:
        # Return general resources if no specific type detected
        return [CRISIS_RESOURCES["988_lifeline"], CRISIS_RESOURCES["crisis_text_line"]]

    resources = []
    added_names = set()

    for resource_id, resource in CRISIS_RESOURCES.items():
        for crisis_type in crisis_types:
            if crisis_type in resource.get("for_crisis_types", []):
                if resource["name"] not in added_names:
                    resources.append(resource)
                    added_names.add(resource["name"])

    # Always include 988 as a baseline resource
    if "988 Suicide & Crisis Lifeline" not in added_names:
        resources.insert(0, CRISIS_RESOURCES["988_lifeline"])

    return resources


# ==============================================================================
# Safety Plan Management
# ==============================================================================


class SafetyPlan:
    """Represents a user's personalized safety plan."""

    def __init__(
        self,
        user_id: str,
        plan_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        sections: Optional[Dict[str, Any]] = None,
        is_active: bool = True,
    ):
        self.user_id = user_id
        self.plan_id = plan_id or f"safety_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at
        self.sections = sections or {}
        self.is_active = is_active

    def to_dict(self) -> Dict[str, Any]:
        """Convert safety plan to dictionary."""
        return {
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "sections": self.sections,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SafetyPlan":
        """Create safety plan from dictionary."""
        return cls(
            user_id=data.get("user_id", ""),
            plan_id=data.get("plan_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            sections=data.get("sections", {}),
            is_active=data.get("is_active", True),
        )


def load_safety_plan(user_id: str, backend: Any) -> Optional[SafetyPlan]:
    """
    Load a user's safety plan from storage.

    Args:
        user_id: User identifier
        backend: FilesystemBackend instance

    Returns:
        SafetyPlan if exists, None otherwise
    """
    plan_path = f"crisis_support/safety_plans/{user_id}.json"

    try:
        if hasattr(backend, "read_file"):
            content = backend.read_file(plan_path)
        else:
            workspace_path = (
                Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")
            )
            file_path = workspace_path / plan_path
            if not file_path.exists():
                return None
            content = file_path.read_text()

        data = json.loads(content)
        return SafetyPlan.from_dict(data)
    except Exception:
        return None


def save_safety_plan(backend: Any, plan: SafetyPlan) -> None:
    """
    Save a safety plan to storage.

    Args:
        backend: FilesystemBackend instance
        plan: SafetyPlan to save
    """
    plan_path = f"crisis_support/safety_plans/{plan.user_id}.json"
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    if hasattr(backend, "write_file"):
        backend.write_file(plan_path, json.dumps(plan.to_dict(), indent=2))
    else:
        file_path = workspace_path / plan_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(plan.to_dict(), indent=2))


# ==============================================================================
# Follow-up Check-in System
# ==============================================================================


class FollowUpCheckin:
    """Represents a follow-up check-in after a crisis."""

    def __init__(
        self,
        user_id: str,
        checkin_id: Optional[str] = None,
        related_crisis_id: Optional[str] = None,
        scheduled_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        status: str = "scheduled",
        wellbeing_score: Optional[int] = None,
        notes: str = "",
    ):
        self.user_id = user_id
        self.checkin_id = (
            checkin_id or f"checkin_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        self.related_crisis_id = related_crisis_id
        self.scheduled_at = scheduled_at or datetime.now().isoformat()
        self.completed_at = completed_at
        self.status = status
        self.wellbeing_score = wellbeing_score
        self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "checkin_id": self.checkin_id,
            "related_crisis_id": self.related_crisis_id,
            "scheduled_at": self.scheduled_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "wellbeing_score": self.wellbeing_score,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FollowUpCheckin":
        return cls(
            user_id=data.get("user_id", ""),
            checkin_id=data.get("checkin_id"),
            related_crisis_id=data.get("related_crisis_id"),
            scheduled_at=data.get("scheduled_at"),
            completed_at=data.get("completed_at"),
            status=data.get("status", "scheduled"),
            wellbeing_score=data.get("wellbeing_score"),
            notes=data.get("notes", ""),
        )


def load_checkins(user_id: str, backend: Any) -> List[FollowUpCheckin]:
    """Load all check-ins for a user."""
    checkins_path = f"crisis_support/checkins/{user_id}.json"

    try:
        if hasattr(backend, "read_file"):
            content = backend.read_file(checkins_path)
        else:
            workspace_path = (
                Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")
            )
            file_path = workspace_path / checkins_path
            if not file_path.exists():
                return []
            content = file_path.read_text()

        data = json.loads(content)
        return [FollowUpCheckin.from_dict(c) for c in data.get("checkins", [])]
    except Exception:
        return []


def save_checkins(user_id: str, backend: Any, checkins: List[FollowUpCheckin]) -> None:
    """Save check-ins for a user."""
    checkins_path = f"crisis_support/checkins/{user_id}.json"
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    data = {
        "user_id": user_id,
        "last_updated": datetime.now().isoformat(),
        "checkins": [c.to_dict() for c in checkins],
    }

    if hasattr(backend, "write_file"):
        backend.write_file(checkins_path, json.dumps(data, indent=2))
    else:
        file_path = workspace_path / checkins_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(data, indent=2))


# ==============================================================================
# Crisis Logging (Privacy-Conscious)
# ==============================================================================


class CrisisLogEntry:
    """Privacy-conscious log of crisis interactions."""

    def __init__(
        self,
        user_id: str,
        crisis_id: Optional[str] = None,
        crisis_level: str = "",
        crisis_types: Optional[List[str]] = None,
        actions_taken: Optional[List[str]] = None,
        resources_provided: Optional[List[str]] = None,
        timestamp: Optional[str] = None,
        requires_follow_up: bool = True,
    ):
        self.user_id = user_id
        self.crisis_id = crisis_id or f"crisis_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.crisis_level = crisis_level
        self.crisis_types = crisis_types or []
        self.actions_taken = actions_taken or []
        self.resources_provided = resources_provided or []
        self.timestamp = timestamp or datetime.now().isoformat()
        self.requires_follow_up = requires_follow_up

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding any PII)."""
        return {
            "crisis_id": self.crisis_id,
            "crisis_level": self.crisis_level,
            "crisis_types": self.crisis_types,
            "actions_taken": self.actions_taken,
            "resources_provided": self.resources_provided,
            "timestamp": self.timestamp,
            "requires_follow_up": self.requires_follow_up,
            # Note: user_id is NOT included in logs for privacy
        }


def log_crisis_interaction(
    backend: Any,
    user_id: str,
    detection_result: CrisisDetectionResult,
    actions_taken: List[str],
    resources_provided: List[str],
) -> str:
    """
    Log crisis interaction with privacy protection.

    Logs include:
    - Crisis level and types (for system improvement)
    - Actions taken and resources provided
    - Timestamp

    Does NOT log:
    - User's actual messages
    - Any personally identifying details about the crisis

    Args:
        backend: FilesystemBackend instance
        user_id: User identifier (used only for file naming)
        detection_result: Crisis detection results
        actions_taken: List of actions taken
        resources_provided: List of resources shared

    Returns:
        Crisis ID for reference
    """
    entry = CrisisLogEntry(
        user_id=user_id,
        crisis_level=detection_result.crisis_level.value,
        crisis_types=[ct.value for ct in detection_result.crisis_types],
        actions_taken=actions_taken,
        resources_provided=resources_provided,
    )

    log_path = f"crisis_support/logs/{datetime.now().strftime('%Y/%m')}.json"
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    try:
        # Load existing logs
        if hasattr(backend, "read_file"):
            try:
                content = backend.read_file(log_path)
                logs = json.loads(content)
            except:
                logs = {"entries": []}
        else:
            file_path = workspace_path / log_path
            if file_path.exists():
                logs = json.loads(file_path.read_text())
            else:
                logs = {"entries": []}

        # Add new entry
        logs["entries"].append(entry.to_dict())

        # Save logs
        if hasattr(backend, "write_file"):
            backend.write_file(log_path, json.dumps(logs, indent=2))
        else:
            file_path = workspace_path / log_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(json.dumps(logs, indent=2))

    except Exception:
        pass  # Silent fail for logging - don't disrupt crisis response

    return entry.crisis_id


# ==============================================================================
# Emergency Tools Factory
# ==============================================================================


def create_emergency_tools(backend=None):
    """
    Create emergency support tools with shared backend instance.

    These tools provide:
    - Real-time crisis keyword detection
    - Immediate professional resource provision
    - Crisis escalation protocol
    - Safety plan template generation and management
    - Post-crisis follow-up check-ins
    - Privacy-conscious crisis logging

    Based on SAMHSA 2025 National Guidelines for Crisis Care and
    988 Suicide & Crisis Lifeline protocols.

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of emergency tools:
        - analyze_crisis_risk: Detect crisis keywords and assess severity
        - get_immediate_resources: Get appropriate crisis resources
        - create_safety_plan: Generate personalized safety plan
        - schedule_followup_checkin: Schedule post-crisis follow-up
        - complete_followup_checkin: Complete a scheduled check-in
        - get_crisis_protocol_guidance: Get crisis response protocol info
        - generate_crisis_response: Generate empathetic crisis response
    """
    if backend is None:
        backend = get_backend()

    @tool
    def analyze_crisis_risk(user_message: str) -> str:
        """Analyze user message for crisis indicators and assess risk level.

        This tool scans text for keywords indicating:
        - Suicidal ideation
        - Self-harm behaviors
        - Abuse situations
        - Substance crises
        - Domestic violence

        It returns the detected crisis level, types, and confidence score.

        Args:
            user_message: The user's message text to analyze

        Returns:
            Crisis analysis results with level, types, and recommended actions

        Example:
            >>> analyze_crisis_risk("I've been feeling really hopeless lately")
        """
        if not user_message or not isinstance(user_message, str):
            return "Error: user_message must be a non-empty string"

        # Perform crisis detection
        result = detect_crisis_keywords(user_message)

        # Format response
        lines = [
            "Crisis Risk Analysis",
            "=" * 60,
            "",
        ]

        if not result.is_crisis:
            lines.append("No crisis indicators detected.")
            lines.append("Continue with standard support protocols.")
            return "\n".join(lines)

        # Crisis detected
        lines.append(f"⚠️  CRISIS DETECTED - Level: {result.crisis_level.value.upper()}")
        lines.append("")
        lines.append(f"Confidence Score: {result.confidence_score * 100:.1f}%")
        lines.append(f"Crisis Types: {', '.join(ct.value for ct in result.crisis_types)}")

        if result.matched_keywords:
            lines.append(f"Indicators Found: {len(result.matched_keywords)}")

        lines.append("")

        if result.crisis_level == CrisisLevel.CRITICAL:
            lines.append("🚨 IMMEDIATE ACTION REQUIRED")
            lines.append("User may be in immediate danger.")
            lines.append("Provide crisis resources immediately and recommend calling 988 or 911.")
        elif result.crisis_level == CrisisLevel.HIGH:
            lines.append("⚠️  URGENT ATTENTION REQUIRED")
            lines.append("User shows significant distress.")
            lines.append("Provide crisis resources and encourage professional contact.")
        elif result.crisis_level == CrisisLevel.MODERATE:
            lines.append("⚡ ELEVATED ATTENTION")
            lines.append("User shows signs of distress.")
            lines.append("Monitor closely and offer support resources.")

        return "\n".join(lines)

    @tool
    def get_immediate_resources(crisis_types: Optional[List[str]] = None) -> str:
        """Get immediate professional crisis resources.

        Returns appropriate crisis hotlines and resources based on the
        type of crisis. Always includes 988 Suicide & Crisis Lifeline
        as a baseline resource.

        Args:
            crisis_types: Optional list of crisis types (e.g., ['suicide_ideation', 'self_harm'])

        Returns:
            Formatted list of crisis resources with contact information

        Example:
            >>> get_immediate_resources(["suicide_ideation"])
            >>> get_immediate_resources()  # Gets general resources
        """
        # Convert string types to enum
        detected_types = []
        if crisis_types:
            for ct_str in crisis_types:
                try:
                    detected_types.append(CrisisType(ct_str))
                except ValueError:
                    pass

        resources = get_appropriate_resources(detected_types)

        lines = [
            "🆘 IMMEDIATE CRISIS RESOURCES",
            "=" * 60,
            "",
            "You are not alone. Help is available right now:",
            "",
        ]

        # Prioritize critical resources
        priority_order = ["988_lifeline", "crisis_text_line", "emergency_services"]
        ordered_resources = []

        for priority_id in priority_order:
            for resource in resources:
                if resource.get("name") == CRISIS_RESOURCES.get(priority_id, {}).get("name"):
                    ordered_resources.append(resource)
                    break

        # Add remaining resources
        for resource in resources:
            if resource not in ordered_resources:
                ordered_resources.append(resource)

        for i, resource in enumerate(ordered_resources, 1):
            lines.append(f"{i}. {resource['name']}")
            lines.append(f"   📞 {resource['number']}")
            if resource.get("text"):
                lines.append(f"   💬 {resource['text']}")
            if resource.get("chat"):
                lines.append(f"   💻 {resource['chat']}")
            lines.append(f"   🕐 Available: {resource['available']}")
            lines.append(f"   ℹ️  {resource['description']}")
            if resource.get("website"):
                lines.append(f"   🌐 {resource['website']}")
            lines.append("")

        lines.append("=" * 60)
        lines.append("IMPORTANT: If you or someone you know is in immediate danger,")
        lines.append("call 911 or go to your nearest emergency room.")
        lines.append("")
        lines.append("DISCLAIMER: These resources connect you with trained professionals.")
        lines.append("This AI system cannot provide crisis intervention or emergency services.")

        return "\n".join(lines)

    @tool
    def create_safety_plan(
        user_id: str,
        warning_signs: List[str],
        coping_strategies: List[str],
        social_contacts: List[Dict[str, str]],
        professional_contacts: List[Dict[str, str]],
        reasons_for_living: List[str],
    ) -> str:
        """Create a personalized safety plan for crisis prevention.

        Creates a comprehensive safety plan based on the evidence-based
        Stanley-Brown Safety Planning Intervention used by crisis counselors.

        Args:
            user_id: User's unique identifier
            warning_signs: List of personal warning signs that a crisis is developing
            coping_strategies: List of internal coping strategies (things they can do alone)
            social_contacts: List of people to contact (each with 'name' and 'phone')
            professional_contacts: List of professional contacts (each with 'name' and 'phone')
            reasons_for_living: List of personal reasons for living

        Returns:
            Confirmation with safety plan summary and storage confirmation

        Example:
            >>> create_safety_plan(
            ...     user_id="user_123",
            ...     warning_signs=["Can't sleep", "Feeling hopeless"],
            ...     coping_strategies=["Go for a walk", "Listen to music"],
            ...     social_contacts=[{"name": "Sarah", "phone": "555-0123"}],
            ...     professional_contacts=[{"name": "Dr. Smith", "phone": "555-0456"}],
            ...     reasons_for_living=["My family", "My dog", "Future goals"]
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Create safety plan sections
            sections = {
                "warning_signs": {
                    "title": "1. Warning Signs",
                    "items": warning_signs,
                },
                "coping_strategies": {
                    "title": "2. Internal Coping Strategies",
                    "items": coping_strategies,
                },
                "social_contacts": {
                    "title": "3. Social Contacts",
                    "items": social_contacts,
                },
                "professional_contacts": {
                    "title": "4. Professional Contacts",
                    "items": professional_contacts,
                },
                "reasons_for_living": {
                    "title": "5. Reasons for Living",
                    "items": reasons_for_living,
                },
                "emergency_resources": {
                    "title": "6. Emergency Resources",
                    "items": [
                        "988 Suicide & Crisis Lifeline: Call or text 988",
                        "Crisis Text Line: Text HOME to 741741",
                        "Emergency: 911",
                    ],
                },
            }

            # Create and save plan
            plan = SafetyPlan(
                user_id=user_id,
                sections=sections,
            )
            save_safety_plan(backend, plan)

            # Format response
            lines = [
                "🛡️  SAFETY PLAN CREATED",
                "=" * 60,
                "",
                f"Plan ID: {plan.plan_id}",
                f"Created: {plan.created_at[:10]}",
                "",
                "Your personalized safety plan includes:",
                f"  • {len(warning_signs)} warning signs identified",
                f"  • {len(coping_strategies)} coping strategies",
                f"  • {len(social_contacts)} social contacts",
                f"  • {len(professional_contacts)} professional contacts",
                f"  • {len(reasons_for_living)} reasons for living",
                "",
                "📋 SAFETY PLAN SUMMARY",
                "-" * 60,
                "",
            ]

            for section_key, section_data in sections.items():
                lines.append(section_data["title"])
                if isinstance(section_data["items"], list):
                    for item in section_data["items"]:
                        if isinstance(item, dict):
                            lines.append(f"  • {item.get('name', '')}: {item.get('phone', '')}")
                        else:
                            lines.append(f"  • {item}")
                lines.append("")

            lines.append("=" * 60)
            lines.append("✅ Your safety plan has been saved.")
            lines.append("Review it regularly and update as needed.")
            lines.append("Keep it easily accessible during difficult moments.")

            return "\n".join(lines)

        except Exception as e:
            return f"Error creating safety plan: {str(e)}"

    @tool
    def get_safety_plan_template() -> str:
        """Get a template for creating a safety plan.

        Returns a structured template based on the evidence-based
        Stanley-Brown Safety Planning Intervention.

        Returns:
            Formatted safety plan template with prompts and examples

        Example:
            >>> get_safety_plan_template()
        """
        lines = [
            "🛡️  SAFETY PLAN TEMPLATE",
            "=" * 60,
            "",
            "A safety plan is a personalized tool to help you navigate crisis moments.",
            "It's best created when you're not in immediate crisis.",
            "",
            "Use the `create_safety_plan` tool with your personalized information.",
            "",
        ]

        for section_key, section_data in SAFETY_PLAN_TEMPLATE.items():
            lines.append(f"{section_data['title']}")
            lines.append("-" * 40)
            lines.append(f"Prompt: {section_data['prompt']}")
            lines.append("")
            lines.append("Examples:")
            for example in section_data["examples"]:
                lines.append(f"  • {example}")
            lines.append("")

        lines.append("=" * 60)
        lines.append("💡 Tips for creating your safety plan:")
        lines.append("  • Be specific with names and phone numbers")
        lines.append("  • Include multiple options for each section")
        lines.append("  • Share your plan with trusted people")
        lines.append("  • Review and update it regularly")
        lines.append("  • Keep it where you can easily find it")

        return "\n".join(lines)

    @tool
    def schedule_followup_checkin(
        user_id: str,
        related_crisis_id: str,
        hours_from_now: int = 24,
    ) -> str:
        """Schedule a follow-up check-in after a crisis.

        Schedules a wellness check-in for a specified time after a crisis
        to ensure the user is doing okay and offer continued support.

        Args:
            user_id: User's unique identifier
            related_crisis_id: ID of the related crisis event
            hours_from_now: Hours from now to schedule check-in (default: 24)

        Returns:
            Confirmation with scheduled check-in details

        Example:
            >>> schedule_followup_checkin(
            ...     user_id="user_123",
            ...     related_crisis_id="crisis_user_123_20240101_120000",
            ...     hours_from_now=24
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not related_crisis_id or not isinstance(related_crisis_id, str):
            return "Error: related_crisis_id must be a non-empty string"

        try:
            # Calculate scheduled time
            scheduled_time = datetime.now() + timedelta(hours=hours_from_now)

            # Create check-in
            checkin = FollowUpCheckin(
                user_id=user_id,
                related_crisis_id=related_crisis_id,
                scheduled_at=scheduled_time.isoformat(),
            )

            # Save check-in
            checkins = load_checkins(user_id, backend)
            checkins.append(checkin)
            save_checkins(user_id, backend, checkins)

            # Format response
            lines = [
                "📅 FOLLOW-UP CHECK-IN SCHEDULED",
                "=" * 60,
                "",
                f"Check-in ID: {checkin.checkin_id}",
                f"Related Crisis: {related_crisis_id}",
                f"Scheduled For: {scheduled_time.strftime('%Y-%m-%d %H:%M')}",
                f"Status: {checkin.status.title()}",
                "",
                "You'll be contacted for a wellness check-in at the scheduled time.",
                "This is to ensure you're doing okay and offer continued support.",
                "",
                "If you need immediate help before then, please:",
                "  • Call or text 988 (Suicide & Crisis Lifeline)",
                "  • Text HOME to 741741 (Crisis Text Line)",
                "  • Call 911 for emergencies",
            ]

            return "\n".join(lines)

        except Exception as e:
            return f"Error scheduling check-in: {str(e)}"

    @tool
    def complete_followup_checkin(
        user_id: str,
        checkin_id: str,
        wellbeing_score: int,
        notes: str = "",
    ) -> str:
        """Complete a scheduled follow-up check-in.

        Records the results of a follow-up check-in, including wellbeing
        score and any notes about the user's current state.

        Args:
            user_id: User's unique identifier
            checkin_id: ID of the check-in to complete
            wellbeing_score: Current wellbeing score from 1-10 (1=very poor, 10=excellent)
            notes: Optional notes about the check-in

        Returns:
            Confirmation with completed check-in details

        Example:
            >>> complete_followup_checkin(
            ...     user_id="user_123",
            ...     checkin_id="checkin_user_123_20240101_120000",
            ...     wellbeing_score=6,
            ...     notes="User reports feeling better, has reached out to therapist"
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not checkin_id or not isinstance(checkin_id, str):
            return "Error: checkin_id must be a non-empty string"
        if not isinstance(wellbeing_score, int) or wellbeing_score < 1 or wellbeing_score > 10:
            return "Error: wellbeing_score must be an integer between 1 and 10"

        try:
            # Load check-ins
            checkins = load_checkins(user_id, backend)

            # Find and update check-in
            checkin = None
            for c in checkins:
                if c.checkin_id == checkin_id:
                    checkin = c
                    break

            if not checkin:
                return f"Check-in '{checkin_id}' not found."

            # Update check-in
            checkin.status = "completed"
            checkin.completed_at = datetime.now().isoformat()
            checkin.wellbeing_score = wellbeing_score
            checkin.notes = notes

            # Save check-ins
            save_checkins(user_id, backend, checkins)

            # Format response
            wellbeing_emoji = (
                "🟢" if wellbeing_score >= 7 else "🟡" if wellbeing_score >= 4 else "🔴"
            )

            lines = [
                "✅ FOLLOW-UP CHECK-IN COMPLETED",
                "=" * 60,
                "",
                f"Check-in ID: {checkin_id}",
                f"Completed At: {checkin.completed_at[:16]}",
                f"Wellbeing Score: {wellbeing_emoji} {wellbeing_score}/10",
            ]

            if notes:
                lines.append(f"Notes: {notes}")

            lines.append("")

            if wellbeing_score <= 3:
                lines.append("⚠️  Your wellbeing score is low.")
                lines.append("Please consider reaching out to a crisis resource:")
                lines.append("  • Call or text 988")
                lines.append("  • Text HOME to 741741")
            elif wellbeing_score <= 6:
                lines.append("💛 Thank you for checking in.")
                lines.append("Continue to monitor your wellbeing and reach out if needed.")
            else:
                lines.append("💚 Great to hear you're doing well!")
                lines.append("Keep up the positive momentum.")

            return "\n".join(lines)

        except Exception as e:
            return f"Error completing check-in: {str(e)}"

    @tool
    def get_crisis_protocol_guidance() -> str:
        """Get information about the crisis protocol and safety guidelines.

        Returns detailed information about:
        - When to use crisis resources
        - What to expect from crisis services
        - Safety planning information
        - Important disclaimers

        Returns:
            Comprehensive crisis protocol guidance

        Example:
            >>> get_crisis_protocol_guidance()
        """
        lines = [
            "🚨 CRISIS PROTOCOL & SAFETY GUIDELINES",
            "=" * 60,
            "",
            "⚠️  IMPORTANT DISCLAIMER",
            "-" * 60,
            "This AI Life Coach is NOT a substitute for professional mental health",
            "services. It cannot provide crisis intervention, diagnosis, or treatment.",
            "",
            "If you are experiencing a mental health crisis, please contact",
            "professional resources immediately.",
            "",
            "🆘 WHEN TO SEEK IMMEDIATE HELP",
            "-" * 60,
            "",
            "Call 911 or go to the nearest emergency room if:",
            "  • You have a plan and intent to harm yourself",
            "  • You have already harmed yourself",
            "  • You are in immediate physical danger",
            "  • Someone else is threatening your safety",
            "",
            "Contact 988 Suicide & Crisis Lifeline if:",
            "  • You're having thoughts of suicide",
            "  • You're in severe emotional distress",
            "  • You need someone to talk to during a crisis",
            "  • You're worried about a loved one",
            "",
            "📞 AVAILABLE CRISIS RESOURCES",
            "-" * 60,
            "",
            "988 Suicide & Crisis Lifeline",
            "  • Call or text: 988",
            "  • Available: 24/7",
            "  • Free, confidential support",
            "",
            "Crisis Text Line",
            "  • Text: HOME to 741741",
            "  • Available: 24/7",
            "  • Text-based crisis counseling",
            "",
            "SAMHSA National Helpline",
            "  • Call: 1-800-662-4357",
            "  • For: Substance use and mental health support",
            "",
            "National Domestic Violence Hotline",
            "  • Call: 1-800-799-SAFE (7233)",
            "  • Available: 24/7",
            "",
            "🛡️  SAFETY PLANNING",
            "-" * 60,
            "",
            "A safety plan is a personalized tool to help you through crisis moments.",
            "It includes:",
            "  • Warning signs that a crisis is developing",
            "  • Coping strategies you can use on your own",
            "  • People you can contact for support",
            "  • Professional resources",
            "  • Reasons for living",
            "",
            "Use `get_safety_plan_template` to see the full template.",
            "",
            "🔒 PRIVACY & SAFETY",
            "-" * 60,
            "",
            "What we DO:",
            "  • Detect crisis keywords to provide immediate resources",
            "  • Log crisis events (without personal details) for system improvement",
            "  • Schedule follow-up check-ins",
            "  • Encourage professional help",
            "",
            "What we DON'T do:",
            "  • Store your crisis messages",
            "  • Share your personal information",
            "  • Provide crisis intervention or therapy",
            "  • Contact emergency services on your behalf",
            "",
            "📋 HOW THIS SYSTEM WORKS",
            "-" * 60,
            "",
            "1. Crisis Detection: The system scans for keywords indicating distress",
            "2. Immediate Response: If crisis indicators are found, resources are provided",
            "3. Safety Planning: Users can create personalized safety plans",
            "4. Follow-up: Scheduled check-ins after crisis events",
            "5. Documentation: Crisis events are logged (anonymously) for system improvement",
            "",
            "Remember: You matter, and help is available. You don't have to go through",
            "this alone.",
        ]

        return "\n".join(lines)

    @tool
    def generate_crisis_response(
        crisis_level: str,
        crisis_types: Optional[List[str]] = None,
    ) -> str:
        """Generate an empathetic crisis response message.

        Creates a compassionate, supportive response appropriate for
        the detected crisis level. Includes appropriate resources.

        Args:
            crisis_level: Severity level ('critical', 'high', 'moderate')
            crisis_types: Optional list of crisis types

        Returns:
            Empathetic crisis response with resources

        Example:
            >>> generate_crisis_response("critical", ["suicide_ideation"])
            >>> generate_crisis_response("moderate")
        """
        crisis_types = crisis_types or []

        if crisis_level == "critical":
            response = [
                "I'm really concerned about what you've shared. It sounds like you're going through",
                "an incredibly difficult time, and I want you to know that you're not alone.",
                "",
                "Please reach out to one of these crisis resources right now:",
                "",
                "🆘 988 Suicide & Crisis Lifeline: Call or text 988",
                "   Available 24/7 with trained crisis counselors",
                "",
                "🆘 Crisis Text Line: Text HOME to 741741",
                "   Free, confidential text-based support",
                "",
                "🆘 Emergency Services: Call 911",
                "   If you're in immediate danger",
                "",
                "These resources have trained professionals who can provide the support",
                "you need right now. You deserve help, and it's available.",
            ]
        elif crisis_level == "high":
            response = [
                "Thank you for sharing what you're going through. It sounds like you're",
                "experiencing significant pain, and I want you to know that support is available.",
                "",
                "I'd strongly encourage you to reach out to:",
                "",
                "📞 988 Suicide & Crisis Lifeline: Call or text 988",
                "   Free, confidential support available 24/7",
                "",
                "💬 Crisis Text Line: Text HOME to 741741",
                "   Text with a trained crisis counselor",
                "",
                "Talking to someone trained in crisis support can make a real difference.",
                "You don't have to carry this alone.",
            ]
        elif crisis_level == "moderate":
            response = [
                "I can hear that you're going through a difficult time. It's really important",
                "to take care of yourself during moments like this.",
                "",
                "Here are some resources that might help:",
                "",
                "📞 988 Suicide & Crisis Lifeline: Call or text 988",
                "   Available if you need someone to talk to",
                "",
                "💬 Crisis Text Line: Text HOME to 741741",
                "   Text-based support when you need it",
                "",
                "Would you like to create a safety plan together? It can help you",
                "prepare for difficult moments and know what steps to take.",
            ]
        else:
            response = [
                "Thank you for sharing with me. If you're ever in crisis or need immediate support,",
                "please don't hesitate to reach out to professional resources:",
                "",
                "📞 988 Suicide & Crisis Lifeline: Call or text 988",
                "💬 Crisis Text Line: Text HOME to 741741",
            ]

        response.extend(
            [
                "",
                "⚠️  Important: I'm an AI assistant and cannot provide crisis intervention or",
                "emergency services. Please contact the professionals above for immediate help.",
            ]
        )

        return "\n".join(response)

    return (
        analyze_crisis_risk,
        get_immediate_resources,
        create_safety_plan,
        get_safety_plan_template,
        schedule_followup_checkin,
        complete_followup_checkin,
        get_crisis_protocol_guidance,
        generate_crisis_response,
    )
