"""
Career Coach tools for AI Life Coach.

This module provides LangChain tools specialized for career development coaching.
All tools use the @tool decorator and follow best practices for validation,
error handling, and user-friendly output.

Tools:
- analyze_skill_gap: Compare current skills to target role requirements
- create_career_path_plan: Generate structured career progression plans with milestones
- optimize_resume: Provide actionable resume/CV improvement recommendations
- generate_interview_prep: Create interview preparation guidance tailored to role
- research_salary_benchmarks: Provide salary range information and negotiation tips

Based on career coaching frameworks including:
- GROW Model (Goal, Reality, Options, Will)
- Skill Gap Analysis 5-point framework
- Career Pathing best practices (short/medium/long-term goals)
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

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
# Career Tool Factory
# ==============================================================================


def create_career_tools(backend=None) -> tuple:
    """
    Create career tools with shared FilesystemBackend instance.

    These tools enable the Career Specialist to:
    - Analyze skill gaps between current capabilities and target roles
    - Create comprehensive career path plans with milestones
    - Provide resume/CV optimization recommendations
    - Generate interview preparation materials
    - Research salary benchmarks and provide negotiation guidance

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of career tools (analyze_skill_gap, create_career_path_plan,
                               optimize_resume, generate_interview_prep,
                               research_salary_benchmarks)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_career_tools()
        >>> result = analyze_skill_gap(
        ...     user_id="user_123",
        ...     current_skills=["Python", "Project Management"],
        ...     target_role="Data Scientist"
        ... )
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def analyze_skill_gap(
        user_id: str,
        current_skills: List[str],
        target_role: str,
        experience_level: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> str:
        """Analyze skill gaps between current capabilities and target role requirements.

        This tool performs a comprehensive skill gap analysis using a 5-point framework:
        1. Assess current skills inventory
        2. Identify target role requirements
        3. Compare and categorize gaps (critical, important, nice-to-have)
        4. Prioritize development needs
        5. Recommend learning resources and timeline

        Args:
            user_id: The user's unique identifier
            current_skills: List of skills the user currently possesses (e.g.,
                           ["Python", "Project Management", "SQL"])
            target_role: Target role or job title (e.g., "Data Scientist", "Product Manager")
            experience_level: Optional target experience level (entry/mid/senior/executive)
            industry: Optional target industry for specialized context

        Returns:
            Structured skill gap analysis with categories, priorities,
            and learning recommendations. Saved to career_assessments/{user_id}/

        Raises:
            ValueError: If user_id or required parameters are invalid

        Example:
            >>> analyze_skill_gap(
            ...     "user_123",
            ...     ["Marketing", "Content Writing"],
            ...     "Data Scientist",
            ...     "entry"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not current_skills or not isinstance(current_skills, list):
            return "Error: current_skills must be a non-empty list"
        if not target_role or not isinstance(target_role, str):
            return "Error: target_role must be a non-empty string"

        try:
            # Define common role requirements (knowledge base)
            role_requirements = {
                "Data Scientist": [
                    {"skill": "Python", "category": "critical"},
                    {"skill": "Machine Learning", "category": "critical"},
                    {"skill": "Statistics", "category": "critical"},
                    {"skill": "SQL", "category": "important"},
                    {"skill": "Data Visualization", "category": "important"},
                    {"skill": "Deep Learning", "category": "nice-to-have"},
                ],
                "Product Manager": [
                    {"skill": "Product Strategy", "category": "critical"},
                    {"skill": "User Research", "category": "critical"},
                    {"skill": "Data Analysis", "category": "important"},
                    {"skill": "Stakeholder Management", "category": "important"},
                    {"skill": "Technical Writing", "category": "nice-to-have"},
                ],
            }

            # Get requirements for target role (use defaults if not in knowledge base)
            reqs = role_requirements.get(
                target_role,
                [
                    {"skill": "Communication", "category": "critical"},
                    {"skill": "Problem Solving", "category": "critical"},
                ],
            )

            # Analyze gaps
            analysis = {
                "user_id": user_id,
                "target_role": target_role,
                "experience_level": experience_level or "not specified",
                "industry": industry or "general",
                "timestamp": datetime.now().isoformat(),
                "current_skills": current_skills,
                "required_skills": [r["skill"] for r in reqs],
                "gap_analysis": {
                    "critical_gaps": [],
                    "important_gaps": [],
                    "nice_to_have_gaps": [],
                },
                "skills_already_having": [],
            }

            # Categorize skills
            current_skill_lower = [s.lower() for s in current_skills]
            for req in reqs:
                skill_lower = req["skill"].lower()
                if any(skill_lower in cs for cs in current_skill_lower):
                    analysis["skills_already_having"].append(req["skill"])
                elif req["category"] == "critical":
                    analysis["gap_analysis"]["critical_gaps"].append(req["skill"])
                elif req["category"] == "important":
                    analysis["gap_analysis"]["important_gaps"].append(req["skill"])
                else:
                    analysis["gap_analysis"]["nice_to_have_gaps"].append(req["skill"])

            # Generate recommendations
            total_critical = len(analysis["gap_analysis"]["critical_gaps"])
            total_important = len(analysis["gap_analysis"]["important_gaps"])

            recommendations = []
            if total_critical > 0:
                recommendations.append(
                    f"Priority 1: Focus on {total_critical} critical skill gap(s) first"
                )
            if total_important > 0:
                recommendations.append(f"Priority 2: Develop {total_important} important skill(s)")
            if analysis["skills_already_having"]:
                recommendations.append(
                    f"Strength: You already have {len(analysis['skills_already_having'])} required skill(s)"
                )

            analysis["recommendations"] = recommendations

            # Save to file
            json_content = json.dumps(analysis, indent=2)
            today = date.today()
            path = f"career_assessments/{user_id}/{today}_skill_gap_{target_role.replace(' ', '_')}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Skill Gap Analysis for '{target_role}'",
                "=" * 60,
                f"\nCurrent Skills: {', '.join(current_skills)}",
                f"Target Role: {target_role}",
                f"Experience Level: {experience_level or 'not specified'}",
            ]

            if analysis["skills_already_having"]:
                response_parts.append(
                    f"\n✓ Skills Already Having: {', '.join(analysis['skills_already_having'])}"
                )

            if analysis["gap_analysis"]["critical_gaps"]:
                response_parts.append(
                    f"\n⚠ Critical Gaps (Priority 1): {', '.join(analysis['gap_analysis']['critical_gaps'])}"
                )

            if analysis["gap_analysis"]["important_gaps"]:
                response_parts.append(
                    f"\n◐ Important Gaps (Priority 2): {', '.join(analysis['gap_analysis']['important_gaps'])}"
                )

            if analysis["gap_analysis"]["nice_to_have_gaps"]:
                response_parts.append(
                    f"\n○ Nice-to-Have: {', '.join(analysis['gap_analysis']['nice_to_have_gaps'])}"
                )

            response_parts.append("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                response_parts.append(f"  {i}. {rec}")

            response_parts.append(f"\nAnalysis saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error analyzing skill gap: {str(e)}"

    @tool
    def create_career_path_plan(
        user_id: str, current_role: str, target_role: str, timeline_years: int = 3
    ) -> str:
        """Create a structured career path plan with milestones and action steps.

        This tool generates a comprehensive career progression plan using best practices
        from modern career pathing frameworks, including:
        - Short-term goals (0-1 year)
        - Medium-term milestones (1-3 years)
        - Long-term vision (3+ years)
        - Actionable steps for each phase
        - Progress tracking metrics

        Args:
            user_id: The user's unique identifier
            current_role: Current job title or role (e.g., "Marketing Manager")
            target_role: Desired future role (e.g., "Data Scientist", "VP of Marketing")
            timeline_years: Timeline in years for achieving target role (default: 3)

        Returns:
            Structured career path plan with phases, milestones, and action steps.
            Saved to career_plans/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> create_career_path_plan(
            ...     "user_123",
            ...     "Marketing Coordinator",
            ...     "Data Scientist",
            ...     3
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not current_role or not isinstance(current_role, str):
            return "Error: current_role must be a non-empty string"
        if not target_role or not isinstance(target_role, str):
            return "Error: target_role must be a non-empty string"
        if timeline_years < 1 or timeline_years > 10:
            return "Error: timeline_years must be between 1 and 10"

        try:
            # Create career path structure
            plan = {
                "user_id": user_id,
                "current_role": current_role,
                "target_role": target_role,
                "timeline_years": timeline_years,
                "created_at": datetime.now().isoformat(),
                "phases": [],
            }

            # Calculate phase durations
            short_term_months = 12  # First year
            medium_term_months = (timeline_years - 1) * 6  # Remaining years split
            long_term_months = (timeline_years - 1) * 6

            # Phase 1: Foundation (0-12 months)
            plan["phases"].append(
                {
                    "phase": 1,
                    "name": "Foundation Building",
                    "duration_months": short_term_months,
                    "goals": [
                        f"Understand requirements for {target_role}",
                        "Identify skill gaps and create learning plan",
                        "Build foundational knowledge in target domain",
                    ],
                    "milestones": [
                        f"Complete introductory coursework for {target_role}",
                        "Network with professionals in target field",
                        "Apply foundational skills to current role projects",
                    ],
                }
            )

            # Phase 2: Skill Development (12-24 months or mid-timeline)
            if timeline_years >= 2:
                plan["phases"].append(
                    {
                        "phase": 2,
                        "name": "Skill Development",
                        "duration_months": min(12, timeline_years * 4),
                        "goals": [
                            f"Develop core competencies for {target_role}",
                            "Gain hands-on experience through projects",
                            "Build portfolio demonstrating relevant skills",
                        ],
                        "milestones": [
                            f"Complete 2-3 major projects related to {target_role}",
                            "Obtain relevant certifications if applicable",
                            "Secure mentor or advocate in target field",
                        ],
                    }
                )

            # Phase 3: Transition & Positioning (remaining timeline)
            if timeline_years >= 3:
                plan["phases"].append(
                    {
                        "phase": 3,
                        "name": "Transition Preparation",
                        "duration_months": max(6, (timeline_years - 2) * 12),
                        "goals": [
                            f"Prepare for transition to {target_role}",
                            "Apply for internal opportunities or external positions",
                            "Demonstrate readiness through achievements",
                        ],
                        "milestones": [
                            f"Apply for {target_role} positions (internal/external)",
                            "Complete interview preparation and mock interviews",
                            "Secure offer or promotion to target role",
                        ],
                    }
                )

            # Save as JSON
            json_content = json.dumps(plan, indent=2)
            path = f"career_plans/{user_id}/path_{current_role.replace(' ', '_')}_to_{target_role.replace(' ', '_')}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Create readable markdown version
            markdown_content = f"""# Career Path Plan

**User:** {user_id}
**From:** {current_role}
**To:** {target_role}
**Timeline:** {timeline_years} years
**Created:** {datetime.now().strftime("%Y-%m-%d")}

## Overview

This plan outlines your journey from **{current_role}** to **{target_role}**
over a {timeline_years}-year period. Each phase builds on the previous one,
creating a structured path toward your goal.

"""
            for phase in plan["phases"]:
                markdown_content += f"""---

## Phase {phase["phase"]}: {phase["name"]}
**Duration:** {phase["duration_months"]} months

### Goals
"""
                for i, goal in enumerate(phase["goals"], 1):
                    markdown_content += f"{i}. {goal}\n"

                markdown_content += "\n### Key Milestones\n"
                for i, milestone in enumerate(phase["milestones"], 1):
                    markdown_content += f"{i}. {milestone}\n"

            markdown_content += f"""

---

## Success Metrics

Track your progress with these indicators:
- **Completion of milestones** as outlined above
- **Skill development** demonstrated through projects and certifications
- **Networking progress** building relationships in target field
- **Application success** securing interviews and offers

## Review Schedule

Review this plan quarterly to:
- Assess progress against milestones
- Adjust timeline if needed based on opportunities/challenges
- Celebrate achievements and learn from setbacks

---
*Plan saved to: {path}*
"""

            # Save markdown version
            md_path = path.replace(".json", ".md")
            if hasattr(backend, "write_file"):
                backend.write_file(md_path, markdown_content)
            else:
                file_path = workspace_path / md_path
                file_path.write_text(markdown_content)

            # Return summary
            return f"""Career Path Plan Created

From: {current_role}
To: {target_role}
Timeline: {timeline_years} years

Phases defined:
{chr(10).join([f"  - Phase {p['phase']}: {p['name']} ({p['duration_months']} months)" for p in plan["phases"]])}

Plan saved to: {md_path}

Next steps:
  1. Review the detailed plan
  2. Set your first milestone for Phase 1
  3. Begin foundational learning identified in the plan
"""

        except Exception as e:
            return f"Error creating career path plan: {str(e)}"

    @tool
    def optimize_resume(
        user_id: str, target_role: str, current_experience_summary: Optional[str] = None
    ) -> str:
        """Provide actionable resume/CV optimization recommendations for target role.

        This tool analyzes resume best practices and provides specific improvements
        tailored to the target role, including:
        - Impact metrics and quantifiable achievements
        - Action verbs and strong language
        - ATS optimization with relevant keywords
        - Structure and formatting recommendations

        Args:
            user_id: The user's unique identifier
            target_role: Target job title for tailoring (e.g., "Data Scientist")
            current_experience_summary: Optional brief summary of experience to
                                       provide context (e.g., "5 years in marketing")

        Returns:
            Structured resume optimization recommendations with before/after examples
            and specific action items. Saved to career_guidance/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> optimize_resume(
            ...     "user_123",
            ...     "Data Scientist",
            ...     "5 years in marketing, looking to transition"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not target_role or not isinstance(target_role, str):
            return "Error: target_role must be a non-empty string"

        try:
            # Define role-specific keywords and impact metrics
            role_guidance = {
                "Data Scientist": {
                    "keywords": [
                        "Machine Learning",
                        "Python",
                        "SQL",
                        "Statistics",
                        "Data Analysis",
                    ],
                    "impact_metrics": [
                        "Improved model accuracy by X%",
                        "Reduced processing time by Y hours",
                        "Generated $Z in revenue/revenue impact",
                    ],
                },
            }

            guidance = role_guidance.get(
                target_role,
                {
                    "keywords": ["Leadership", "Project Management", "Communication"],
                    "impact_metrics": [
                        "Improved efficiency by X%",
                        "Saved $Y through process improvements",
                        "Led team of Z people to achieve goals",
                    ],
                },
            )

            recommendations = {
                "user_id": user_id,
                "target_role": target_role,
                "experience_context": current_experience_summary or "Not provided",
                "timestamp": datetime.now().isoformat(),
                "recommendations": [
                    {
                        "category": "Impact Metrics",
                        "description": "Quantify achievements with specific numbers and outcomes",
                        "examples": guidance["impact_metrics"],
                    },
                    {
                        "category": "Action Verbs",
                        "description": "Use strong, specific verbs to describe accomplishments",
                        "examples": [
                            "Spearheaded",
                            "Developed",
                            "Implemented",
                            "Optimized",
                            "Led",
                            "Designed",
                            "Analyzed",
                            "Achieved",
                        ],
                    },
                    {
                        "category": "ATS Keywords",
                        "description": f"Include these keywords for {target_role} roles",
                        "examples": guidance["keywords"],
                    },
                ],
            }

            # Save recommendations
            json_content = json.dumps(recommendations, indent=2)
            path = f"career_guidance/{user_id}/resume_optimization_{target_role.replace(' ', '_')}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            action_verbs = [
                "Spearheaded",
                "Developed",
                "Implemented",
                "Optimized",
                "Led",
                "Designed",
                "Analyzed",
                "Achieved",
            ]

            response = f"""Resume Optimization for {target_role}

{"=" * 60}

Experience Context: {current_experience_summary or "Not provided"}

Based on best practices and {target_role} role requirements, here are key improvements:

1. Impact Metrics (Quantify Your Achievements)
   Use specific numbers and measurable outcomes:
{chr(10).join([f"   - {ex}" for ex in guidance["impact_metrics"]])}

2. Strong Action Verbs
   Replace weak verbs with powerful alternatives:
   {", ".join(action_verbs[:8])}

3. ATS Optimization
   Include these keywords for {target_role} positions:
   {", ".join(guidance["keywords"])}

4. Structure & Formatting
   - Use clear section headers (Experience, Skills, Education)
   - Keep to 1-2 pages maximum
   - Use bullet points for readability
   - Ensure consistent formatting throughout

Recommendations saved to: {path}

Next Steps:
  1. Review your current resume against these recommendations
  2. Update bullet points with impact metrics
  3. Incorporate relevant keywords naturally
  4. Tailor content for each application while keeping a master version
"""

            return response

        except Exception as e:
            return f"Error providing resume optimization: {str(e)}"

    @tool
    def generate_interview_prep(
        user_id: str, target_role: str, company_type: Optional[str] = None
    ) -> str:
        """Generate interview preparation guidance tailored to target role.

        This tool creates comprehensive interview preparation materials including:
        - Common behavioral questions with STAR method examples
        - Technical/domain-specific question topics
        - Company research checklist
        - Strategic questions to ask interviewers

        Args:
            user_id: The user's unique identifier
            target_role: Target job title (e.g., "Data Scientist", "Product Manager")
            company_type: Optional type of company (tech, finance, startup, etc.)

        Returns:
            Structured interview preparation guide with practice questions and
            strategies for different interview types. Saved to career_guidance/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> generate_interview_prep(
            ...     "user_123",
            ...     "Data Scientist",
            ...     "tech"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not target_role or not isinstance(target_role, str):
            return "Error: target_role must be a non-empty string"

        try:
            # Define role-specific interview content
            role_content = {
                "Data Scientist": {
                    "behavioral_questions": [
                        "Tell me about a time you had to explain complex data findings to non-technical stakeholders",
                        "Describe a project where machine learning didn't work as expected",
                        "How do you approach feature selection and model development?",
                    ],
                    "technical_topics": [
                        "Machine learning algorithms (common types, when to use)",
                        "Data cleaning and preprocessing techniques",
                        "Evaluation metrics for different problem types",
                    ],
                },
            }

            content = role_content.get(
                target_role,
                {
                    "behavioral_questions": [
                        "Tell me about a challenging project you led",
                        "Describe how you handle competing priorities",
                        "Give an example of improving a process or workflow",
                    ],
                    "technical_topics": [
                        "Core skills relevant to the role",
                        "Problem-solving approaches",
                        "Industry-specific knowledge",
                    ],
                },
            )

            prep_guide = {
                "user_id": user_id,
                "target_role": target_role,
                "company_type": company_type or "general",
                "timestamp": datetime.now().isoformat(),
                "behavioral_questions": content["behavioral_questions"],
                "technical_topics": content["technical_topics"],
            }

            # Save guide
            json_content = json.dumps(prep_guide, indent=2)
            path = f"career_guidance/{user_id}/interview_prep_{target_role.replace(' ', '_')}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response = f"""Interview Preparation Guide for {target_role}

{"=" * 60}

## Behavioral Questions (Use STAR Method)

Practice these common questions using the STAR structure:
(Situation, Task, Action, Result)

{chr(10).join([f"{i + 1}. {q}" for i, q in enumerate(content["behavioral_questions"])])}

STAR Method Refresher:
- **S**ituation: Set the context
- **T**ask: What was your responsibility?
- **A**ction: What specific steps did you take? (This is most important)
- **R**esult: What was the outcome? Use numbers if possible

## Technical Topics to Review

{chr(10).join([f"- {topic}" for topic in content["technical_topics"]])}

## Company Research Checklist

Before your interview, research:
- Recent company news and announcements
- Company's products/services and competitors
- Company culture and values (check website, LinkedIn)
- Interviewers' backgrounds (LinkedIn profiles)

## Questions to Ask the Interviewer

Prepare 2-3 thoughtful questions:
1. "What does success look like in this role?"
2. "How does the team collaborate on projects?"
3. "What are the biggest challenges facing the team right now?"

Prep guide saved to: {path}

Next Steps:
  1. Practice STAR responses for behavioral questions
  2. Review technical topics and prepare examples
  3. Research the company thoroughly
  4. Prepare questions to show your interest and engagement
"""

            return response

        except Exception as e:
            return f"Error generating interview prep: {str(e)}"

    @tool
    def research_salary_benchmarks(
        user_id: str,
        target_role: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
    ) -> str:
        """Provide salary benchmark information and negotiation guidance.

        This tool offers general salary range information based on role, location,
        and experience level, along with negotiation strategies. Note: This provides
        general market guidance only; actual offers vary significantly.

        Args:
            user_id: The user's unique identifier
            target_role: Target job title (e.g., "Data Scientist", "Product Manager")
            location: Optional city/region for market context
            experience_level: Optional level (entry, mid, senior)

        Returns:
            Salary benchmark information with negotiation strategies.
            Saved to career_guidance/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> research_salary_benchmarks(
            ...     "user_123",
            ...     "Data Scientist",
            ...     "San Francisco",
            ...     "mid"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not target_role or not isinstance(target_role, str):
            return "Error: target_role must be a non-empty string"

        try:
            # General salary ranges (these are broad estimates for context only)
            salary_ranges = {
                "entry": {"min": 60000, "median": 80000, "max": 100000},
                "mid": {"min": 90000, "median": 120000, "max": 150000},
                "senior": {"min": 130000, "median": 170000, "max": 250000},
            }

            exp_level = (experience_level or "mid").lower()
            if exp_level not in salary_ranges:
                exp_level = "mid"

            range_data = salary_ranges[exp_level]

            # Negotiation strategies
            negotiation_tips = [
                "Research market rates before negotiations",
                "Consider total compensation (salary, bonus, benefits, equity)",
                "Know your walk-away point before negotiations start",
                "Practice salary negotiation conversations beforehand",
                "Be prepared to justify your value with specific achievements",
            ]

            # Save benchmark data
            bench_data = {
                "user_id": user_id,
                "target_role": target_role,
                "location": location or "general",
                "experience_level": exp_level,
                "timestamp": datetime.now().isoformat(),
                "salary_range": range_data,
            }

            json_content = json.dumps(bench_data, indent=2)
            path = (
                f"career_guidance/{user_id}/salary_benchmark_{target_role.replace(' ', '_')}.json"
            )

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            location_str = f" in {location}" if location else ""
            response = f"""Salary Benchmark for {target_role}{location_str}
Experience Level: {exp_level.title()}

{"=" * 60}

## General Salary Range (Estimates Only)

These are broad market estimates for reference:
- Entry Level: ${range_data["min"]:,} - ${salary_ranges["entry"]["max"]:,}
- Mid Level: ${range_data["min"]:,} - ${salary_ranges["mid"]["max"]:,}
- Senior Level: ${range_data["min"]:,} - ${salary_ranges["senior"]["max"]:,}

**Your level ({exp_level}):**
- Range: ${range_data["min"]:,} - ${range_data["max"]:,}
- Median: ${range_data["median"]:,}

**Important Notes:**
- Actual offers vary widely based on company, location, and individual qualifications
- Consider total compensation package (salary + bonus + benefits + equity)
- Tech hubs and major cities typically pay higher ranges
- Startups may offer lower base salary but more equity upside

## Negotiation Strategies

{chr(10).join([f"{i + 1}. {tip}" for i, tip in enumerate(negotiation_tips)])}

## Key Negotiation Points

1. **Timing**: Discuss salary after you receive an offer, not before
2. **Total Package**: Consider all components, not just base salary
3. **Justification**: Prepare examples of your value and achievements
4. **Flexibility**: Be open to creative solutions (signing bonus, equity, etc.)

Benchmark data saved to: {path}

**Disclaimer:** This is general market information only. For accurate salary
data, research current listings on Glassdoor, Levels.fyi, or industry-specific
salary surveys. Consider consulting with professional recruiters for personalized guidance.
"""

            return response

        except Exception as e:
            return f"Error researching salary benchmarks: {str(e)}"

    @tool
    def calculate_skill_match_score(
        user_id: str, user_skills: List[str], job_requirements: List[str]
    ) -> str:
        """Calculate a skill match score between user skills and job requirements.

        This tool uses weighted matching algorithms to assess how well a user's
        skills align with job requirements, providing:
        - Overall match percentage (0-100%)
        - Matched skills and gap analysis
        - Recommendations for improving match rate

        Args:
            user_id: The user's unique identifier
            user_skills: List of skills the user possesses (e.g., ["Python", "SQL"])
            job_requirements: List of required skills for the position
                           (e.g., ["Python", "Machine Learning", "SQL"])

        Returns:
            Skill match analysis with percentage score, matched/gapped skills,
            and improvement recommendations. Saved to career_assessments/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> calculate_skill_match_score(
            ...     "user_123",
            ...     ["Python", "SQL", "Data Visualization"],
            ...     ["Python", "Machine Learning", "SQL", "Statistics"]
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not user_skills or not isinstance(user_skills, list):
            return "Error: user_skills must be a non-empty list"
        if not job_requirements or not isinstance(job_requirements, list):
            return "Error: job_requirements must be a non-empty list"

        try:
            # Normalize skills for matching (case-insensitive, handle variations)
            user_skills_normalized = [s.lower().strip() for s in user_skills]
            job_reqs_normalized = [r.lower().strip() for r in job_requirements]

            # Find exact matches
            matched_skills = []
            for req in job_reqs_normalized:
                for skill in user_skills_normalized:
                    # Check for exact match or partial overlap
                    if req == skill or req in skill or skill in req:
                        matched_skills.append(req)
                        break

            # Remove duplicates while preserving order
            seen = set()
            matched_unique = []
            for skill in matched_skills:
                if skill not in seen:
                    seen.add(skill)
                    matched_unique.append(skill)

            # Calculate metrics
            total_requirements = len(job_requirements)
            matched_count = len(matched_unique)
            match_percentage = (
                (matched_count / total_requirements * 100) if total_requirements > 0 else 0
            )

            # Identify gaps
            gap_skills = [req for req in job_reqs_normalized if req not in matched_unique]

            # Categorize match quality
            if match_percentage >= 80:
                match_quality = "Excellent"
            elif match_percentage >= 60:
                match_quality = "Good"
            elif match_percentage >= 40:
                match_quality = "Moderate"
            else:
                match_quality = "Low"

            # Generate recommendations
            recommendations = []
            if gap_skills:
                recommendations.append(
                    f"Focus on acquiring {len(gap_skills)} missing skill(s): "
                    f"{', '.join([s.title() for s in gap_skills[:3]])}"
                    + ("..." if len(gap_skills) > 3 else "")
                )
            if match_percentage >= 60:
                recommendations.append(
                    "Highlight your matched skills prominently in resume and interviews"
                )
            if match_percentage < 80:
                recommendations.append(
                    "Consider online courses or certifications to fill skill gaps"
                )

            # Build analysis data
            analysis = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "user_skills": user_skills,
                "job_requirements": job_requirements,
                "matched_count": matched_count,
                "total_requirements": total_requirements,
                "match_percentage": round(match_percentage, 1),
                "match_quality": match_quality,
                "matched_skills": matched_unique,
                "gap_skills": gap_skills,
                "recommendations": recommendations,
            }

            # Save to file
            json_content = json.dumps(analysis, indent=2)
            today = date.today()
            path = f"career_assessments/{user_id}/{today}_skill_match_score.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                "Skill Match Score Analysis",
                "=" * 60,
                f"\nMatch Quality: {match_quality}",
                f"Overall Match: {match_percentage:.1f}%",
                f"\nMatched Skills ({matched_count}/{total_requirements}):",
            ]

            if matched_unique:
                for skill in matched_unique:
                    response_parts.append(f"  ✓ {skill.title()}")

            if gap_skills:
                response_parts.append(f"\nMissing Skills ({len(gap_skills)}):")
                for skill in gap_skills:
                    response_parts.append(f"  ○ {skill.title()}")

            if recommendations:
                response_parts.append("\nRecommendations:")
                for i, rec in enumerate(recommendations, 1):
                    response_parts.append(f"  {i}. {rec}")

            response_parts.append(f"\nAnalysis saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error calculating skill match score: {str(e)}"

    @tool
    def estimate_salary_range(
        user_id: str,
        role: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = "mid",
    ) -> str:
        """Estimate salary range based on role, location, and experience.

        This tool provides estimated salary ranges using market data patterns.
        It considers cost of living adjustments for different locations and
        experience-based multipliers. Note: These are estimates only - actual
        salaries vary significantly by company, industry, and individual factors.

        Args:
            user_id: The user's unique identifier
            role: Job title or role (e.g., "Data Scientist", "Software Engineer")
            location: Optional city/state/region for COL adjustment
            experience_level: Experience level (entry, mid, senior, executive)

        Returns:
            Salary range estimate with breakdown by experience level,
            location adjustments, and negotiation context. Saved to career_guidance/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> estimate_salary_range(
            ...     "user_123",
            ...     "Data Scientist",
            ...     location="San Francisco, CA",
            ...     experience_level="mid"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not role or not isinstance(role, str):
            return "Error: role must be a non-empty string"

        # Normalize experience level
        exp_levels = ["entry", "mid", "senior", "executive"]
        if experience_level and experience_level.lower() not in exp_levels:
            experience_level = "mid"
        else:
            experience_level = (experience_level or "mid").lower()

        try:
            # Base salary ranges by role category (broad estimates)
            role_categories = {
                "tech": {
                    "roles": [
                        "software engineer",
                        "data scientist",
                        "product manager",
                        "developer",
                        "engineer",
                        "analyst",
                    ],
                    "entry": {"min": 70000, "median": 85000, "max": 100000},
                    "mid": {"min": 110000, "median": 140000, "max": 170000},
                    "senior": {"min": 160000, "median": 200000, "max": 250000},
                    "executive": {"min": 250000, "median": 350000, "max": 500000},
                },
                "business": {
                    "roles": [
                        "marketing",
                        "sales",
                        "hr",
                        "operations",
                        "finance",
                        "consultant",
                    ],
                    "entry": {"min": 50000, "median": 65000, "max": 80000},
                    "mid": {"min": 80000, "median": 100000, "max": 130000},
                    "senior": {"min": 120000, "median": 150000, "max": 200000},
                    "executive": {"min": 180000, "median": 250000, "max": 400000},
                },
            }

            # Determine role category
            role_lower = role.lower()
            base_category = None
            for cat_name, cat_data in role_categories.items():
                if any(role_word in role_lower for role_word in cat_data["roles"]):
                    base_category = cat_name
                    break

            # Default to business if no match found
            if not base_category:
                base_category = "business"

            # Get base range for experience level
            salary_data = role_categories[base_category][experience_level]

            # Location cost of living multipliers
            col_adjustments = {
                "san francisco": 1.45,
                "new york": 1.35,
                "seattle": 1.25,
                "boston": 1.20,
                "los angeles": 1.25,
                "chicago": 1.10,
                "austin": 1.05,
                "denver": 1.00,
                "atlanta": 0.95,
                "dallas": 0.95,
                "phoenix": 0.90,
            }

            # Apply location adjustment if provided
            col_multiplier = 1.0
            if location:
                loc_lower = location.lower()
                for city, multiplier in col_adjustments.items():
                    if city in loc_lower:
                        col_multiplier = multiplier
                        break

            # Calculate adjusted ranges
            min_salary = round(salary_data["min"] * col_multiplier)
            median_salary = round(salary_data["median"] * col_multiplier)
            max_salary = round(salary_data["max"] * col_multiplier)

            # Build estimate data
            estimate = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "location": location or "national_average",
                "experience_level": experience_level,
                "col_multiplier": col_multiplier,
                "salary_range": {
                    "min": min_salary,
                    "median": median_salary,
                    "max": max_salary,
                },
            }

            # Save to file
            json_content = json.dumps(estimate, indent=2)
            path = (
                f"career_guidance/{user_id}/salary_estimate_{role.replace(' ', '_').lower()}.json"
            )

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            location_str = f" in {location}" if location else " (National Average)"
            col_note = (
                f"\nCost of Living Adjustment: {col_multiplier:.2f}x"
                if col_multiplier != 1.0
                else ""
            )

            response = f"""Salary Estimate for {role}{location_str}
Experience Level: {experience_level.title()}
{"=" * 60}

Estimated Salary Range:
• Minimum: ${min_salary:,}
• Median: ${median_salary:,}
• Maximum: ${max_salary:,}{col_note}

Factors Affecting Salary:
• Company size and funding stage
• Specific industry sector
• Educational background and certifications
• Specialized skills and expertise
• Geographic location (within region)
• Current market conditions

Negotiation Tips:
1. Research specific companies on Glassdoor, Levels.fyi, or Payscale
2. Consider total compensation (salary + bonus + benefits + equity)
3. Know your walk-away point before negotiating
4. Be prepared to justify your value with specific achievements
5. Practice your negotiation pitch beforehand

⚠️ Disclaimer: These are broad market estimates only. Actual offers vary
significantly based on individual qualifications and company-specific factors.

Estimate saved to: {path}
"""

            return response

        except Exception as e:
            return f"Error estimating salary range: {str(e)}"

    print("Career tools created successfully!")
    return (
        analyze_skill_gap,
        create_career_path_plan,
        optimize_resume,
        generate_interview_prep,
        research_salary_benchmarks,
        calculate_skill_match_score,
        estimate_salary_range,
    )


# Export tools at module level for convenience
__all__ = [
    "create_career_tools",
]
