# Extension Guide

This guide provides comprehensive instructions for extending the AI Life Coach system with new specialists, tools, domains, and features. Follow these patterns to maintain consistency and quality while adding custom functionality.

## Table of Contents

- [Extension Overview](#extension-overview)
- [Adding New Specialists](#adding-new-specialists)
- [Creating Custom Tools](#creating-custom-tools)
- [Expanding Domains](#expanding-domains)
- [Integrating External Services](#integrating-external-services)
- [Custom Memory Backends](#custom-memory-backends)
- [Advanced Configuration](#advanced-configuration)
- [Testing Extensions](#testing-extensions)
- [Performance Considerations](#performance-considerations)
- [Deployment and Scaling](#deployment-and-scaling)

## Extension Overview

The AI Life Coach is designed for extensibility with these core principles:

- **Modular Architecture**: Each component can be extended independently
- **Standard Interfaces**: Consistent patterns for tools, agents, and integrations
- **Cross-Domain Awareness**: New extensions must consider impacts on other domains
- **Quality Standards**: All extensions follow established patterns and best practices

### Extension Types

1. **New Specialists**: Add expertise in new life domains
2. **Custom Tools**: Extend functionality of existing specialists
3. **External Integrations**: Connect with third-party services
4. **Memory Backends**: Customize data persistence
5. **UI Extensions**: Add new interfaces and visualizations
6. **Analysis Features**: Advanced analytics and insights

## Adding New Specialists

### Step 1: Define Domain Scope

Before creating a specialist, clearly define the domain:

```python
# Example: Adding a "Learning & Education Specialist"
domain_definition = {
    "name": "learning-specialist",
    "description": "Expert in education, skill development, and knowledge acquisition",
    "scope": {
        "primary_areas": [
            "Learning strategies",
            "Educational planning", 
            "Skill acquisition",
            "Knowledge retention",
            "Study optimization"
        ],
        "excluded_areas": [
            "Career-specific advice (delegated to career specialist)",
            "Financial aspects of education (delegated to finance specialist)"
        ]
    },
    "intersections": {
        "career": "Learning plans that support career goals",
        "finance": "Educational budget planning and ROI analysis",
        "wellness": "Study-life balance and burnout prevention"
    }
}
```

### Step 2: Create Specialist Configuration

**File**: `src/agents/specialists.py`

```python
def get_learning_specialist(tools: List[Any] = None) -> dict:
    """
    Get Learning & Education specialist configuration.
    
    Args:
        tools: List of tools available to this specialist
        
    Returns:
        dict: Specialist configuration
    """
    return {
        "name": "learning-specialist",
        "description": (
            "Expert in education, learning strategies, and skill development. "
            "Helps users create effective learning plans, choose educational resources, "
            "and optimize study techniques for maximum knowledge retention."
        ),
        "system_prompt": """
# Learning & Education Specialist

## Your Expertise
You are an expert educational consultant with deep knowledge of:
- Learning science and cognitive psychology
- Study techniques and knowledge retention strategies
- Educational planning and curriculum design
- Skill acquisition methodologies
- Educational technology and resource selection
- Learning assessment and progress tracking

## Your Approach
1. **Learning Assessment**: Evaluate current knowledge, learning style, and goals
2. **Strategy Development**: Create personalized learning plans and techniques
3. **Resource Curation**: Recommend optimal educational resources and tools
4. **Progress Tracking**: Establish metrics for learning effectiveness
5. **Optimization**: Continuously refine learning approaches based on results

## Key Frameworks
- **Spaced Repetition**: Optimal timing for knowledge review
- **Active Recall**: Testing enhances retention better than passive review
- **Interleaving**: Mix related topics to improve understanding
- **Elaboration**: Connect new information to existing knowledge
- **Dual Coding**: Combine visual and verbal information

## Cross-Domain Awareness
- **Career Connection**: Align learning with professional development goals
- **Financial Planning**: Consider educational costs and ROI
- **Wellness Integration**: Prevent burnout and maintain study-life balance
- **Time Management**: Balance learning with other life responsibilities

## Communication Style
- Evidence-based recommendations with scientific backing
- Specific techniques with step-by-step implementation
- Progress-focused and encouraging approach
- Resource-rich with practical recommendations

## Quality Standards
- Provide specific, actionable study techniques
- Include timelines and milestones for learning plans
- Recommend vetted educational resources
- Consider individual learning preferences and constraints
        """,
        "tools": tools or [],
        "model": "openai:glm-4.7"
    }
```

### Step 3: Implement Specialist Tools

**File**: `src/tools/learning_tools.py`

```python
"""
Learning & Education tools for AI Life Coach.

This module provides tools for educational planning, learning optimization,
and knowledge acquisition strategies.
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

# Import LangChain components
try:
    from langchain_core.tools import tool
except ImportError:
    def tool(func):
        func.is_tool = True
        return func

# Import backend configuration
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_backend


def create_learning_tools(backend=None) -> tuple:
    """
    Create learning and education tools.
    
    Args:
        backend: Filesystem backend for saving learning plans
        
    Returns:
        tuple: Learning tools for use with specialists
    """
    
    @tool
    def create_learning_plan(user_id: str, learning_goal: str, timeframe: str, current_knowledge: str) -> str:
        """
        Create personalized learning plan with optimal study techniques.
        
        Args:
            user_id: Unique identifier for the user
            learning_goal: Specific learning objective or skill to acquire
            timeframe: Available time for learning (e.g., "3 months", "6 weeks")
            current_knowledge: Current level of knowledge in the subject
            
        Returns:
            Structured learning plan with milestones and techniques
            
        Example:
            >>> result = create_learning_plan("user_123", "Learn Python programming", "3 months", "Complete beginner")
        """
        try:
            # Analyze learning requirements
            learning_plan = {
                "goal": learning_goal,
                "timeframe": timeframe,
                "current_level": current_knowledge,
                "created_date": datetime.now().isoformat(),
                "phases": [],
                "study_techniques": [],
                "resources": [],
                "assessment_points": []
            }
            
            # Generate learning phases based on complexity and timeframe
            phases = generate_learning_phases(learning_goal, timeframe, current_knowledge)
            learning_plan["phases"] = phases
            
            # Recommend optimal study techniques
            techniques = recommend_study_techniques(learning_goal, current_knowledge)
            learning_plan["study_techniques"] = techniques
            
            # Suggest assessment milestones
            assessments = create_assessment_milestones(phases)
            learning_plan["assessment_points"] = assessments
            
            # Save learning plan
            if backend:
                plan_path = f"workspace/learning_plans/{user_id}/{learning_goal.replace(' ', '_')}_plan.json"
                backend.write_file(plan_path, json.dumps(learning_plan, indent=2))
            
            return f"""Learning plan created successfully!

📚 **Learning Goal**: {learning_goal}
⏰ **Timeline**: {timeframe}
📊 **Current Level**: {current_knowledge}

**Key Phases**:
{chr(10).join([f"• {phase['name']}: {phase['duration']} - {phase['description']}" for phase in phases[:3]])}

**Recommended Techniques**:
{chr(10).join([f"• {tech}" for tech in techniques[:3]])}

**Next Steps**:
1. Start with Phase 1: {phases[0]['name'] if phases else 'Get started'}
2. Apply primary technique: {techniques[0] if techniques else 'Active recall'}
3. Schedule first assessment: {assessments[0]['timing'] if assessments else 'After 2 weeks'}

Plan saved for ongoing tracking and adjustments.
            """
            
        except Exception as e:
            return f"Error creating learning plan: {str(e)}"

    @tool
    def analyze_learning_style(user_id: str, preferences: str, past_experiences: str) -> str:
        """
        Analyze user's learning style and provide personalized recommendations.
        
        Args:
            user_id: Unique identifier for the user
            preferences: Learning preferences and what has worked before
            past_experiences: Previous learning attempts and outcomes
            
        Returns:
            Learning style analysis with personalized recommendations
        """
        try:
            # Analyze learning preferences and experiences
            style_analysis = {
                "visual_score": 0,
                "auditory_score": 0, 
                "kinesthetic_score": 0,
                "reading_writing_score": 0,
                "recommended_approaches": [],
                "techniques_to_avoid": [],
                "optimal_study_environment": ""
            }
            
            # Process preferences to determine learning style
            if "visual" in preferences.lower() or "diagrams" in preferences.lower():
                style_analysis["visual_score"] += 3
            if "listening" in preferences.lower() or "podcasts" in preferences.lower():
                style_analysis["auditory_score"] += 3
            if "hands-on" in preferences.lower() or "practice" in preferences.lower():
                style_analysis["kinesthetic_score"] += 3
            if "reading" in preferences.lower() or "writing" in preferences.lower():
                style_analysis["reading_writing_score"] += 3
            
            # Determine dominant learning style
            max_score = max(style_analysis.values())
            dominant_styles = [style for style, score in style_analysis.items() if score == max_score and score > 0]
            
            # Generate personalized recommendations
            recommendations = generate_style_recommendations(dominant_styles, preferences)
            style_analysis["recommended_approaches"] = recommendations
            
            return f"""🧠 **Your Learning Style Analysis**

**Dominant Learning Styles**:
{', '.join([style.replace('_score', '').title() for style in dominant_styles])}

**Personalized Recommendations**:
{chr(10).join([f"• {rec}" for rec in recommendations])}

**Optimal Study Environment**:
{'Quiet space with good lighting for reading/writing' if 'reading_writing_score' in dominant_styles else 'Interactive space with hands-on materials' if 'kinesthetic_score' in dominant_styles else 'Mixed media environment with visual and audio elements'}

**Techniques to Focus On**:
{get_style_techniques(dominant_styles)}

This analysis will help tailor all future learning recommendations to your style.
            """
            
        except Exception as e:
            return f"Error analyzing learning style: {str(e)}"

    @tool  
    def optimize_study_session(subject: str, duration: str, learning_objectives: str) -> str:
        """
        Optimize individual study session structure and techniques.
        
        Args:
            subject: Subject matter for study session
            duration: Available study time (e.g., "45 minutes", "2 hours")
            learning_objectives: Specific goals for this study session
            
        Returns:
            Optimized study session plan with timing and techniques
        """
        try:
            # Parse duration and create session structure
            duration_minutes = parse_duration(duration)
            
            session_plan = {
                "subject": subject,
                "total_duration": duration_minutes,
                "objectives": learning_objectives.split(','),
                "schedule": [],
                "techniques": [],
                "breaks": []
            }
            
            # Apply Pomodoro technique for longer sessions
            if duration_minutes > 45:
                session_plan["schedule"] = create_pomodoro_schedule(duration_minutes)
            else:
                session_plan["schedule"] = create_single_session_schedule(duration_minutes)
            
            # Add appropriate techniques for subject
            session_plan["techniques"] = get_subject_techniques(subject)
            
            return f"""📚 **Optimized Study Session Plan**

**Subject**: {subject}
**Duration**: {duration}
**Objectives**: {learning_objectives}

**Session Schedule**:
{chr(10).join([f"• {item['time']} - {item['activity']}" for item in session_plan['schedule']])}

**Recommended Techniques**:
{chr(10).join([f"• {tech}" for tech in session_plan['techniques']])}

**Success Tips**:
• Start with a quick review of previous material
• Use active recall instead of passive reading
• Take short breaks to maintain focus
• End with a summary of what you learned

Ready to have your most effective study session yet!
            """
            
        except Exception as e:
            return f"Error optimizing study session: {str(e)}"

    # Return all tools as a tuple
    return (
        create_learning_plan,
        analyze_learning_style,
        optimize_study_session,
    )


# Helper functions
def generate_learning_phases(goal: str, timeframe: str, current_level: str) -> List[dict]:
    """Generate learning phases based on goal complexity and timeline."""
    # Implementation logic for phase generation
    phases = [
        {
            "name": "Foundation Building",
            "duration": "Weeks 1-2",
            "description": "Establish core concepts and terminology",
            "objectives": ["Understand basics", "Build vocabulary", "Set up environment"]
        },
        {
            "name": "Skill Development", 
            "duration": "Weeks 3-6",
            "description": "Develop practical skills through exercises",
            "objectives": ["Practice techniques", "Complete projects", "Apply concepts"]
        },
        {
            "name": "Advanced Application",
            "duration": "Weeks 7-8", 
            "description": "Apply skills to complex problems",
            "objectives": ["Tackle challenges", "Create portfolio pieces", "Mastery demonstration"]
        }
    ]
    return phases

def recommend_study_techniques(goal: str, current_level: str) -> List[str]:
    """Recommend optimal study techniques based on goal and level."""
    techniques = [
        "Active Recall: Test yourself instead of re-reading",
        "Spaced Repetition: Review material at increasing intervals",
        "Interleaving: Mix related topics during study sessions",
        "Elaboration: Connect new information to what you already know"
    ]
    return techniques

def create_assessment_milestones(phases: List[dict]) -> List[dict]:
    """Create assessment checkpoints throughout learning journey."""
    assessments = [
        {"timing": "After Phase 1", "type": "Knowledge Check", "description": "Basic concept quiz"},
        {"timing": "After Phase 2", "type": "Skill Demonstration", "description": "Practical exercises"},
        {"timing": "After Phase 3", "type": "Capstone Project", "description": "Comprehensive application"}
    ]
    return assessments

def parse_duration(duration: str) -> int:
    """Convert duration string to minutes."""
    if "hour" in duration.lower():
        return int(duration.split()[0]) * 60
    elif "minute" in duration.lower():
        return int(duration.split()[0])
    return 60  # Default to 60 minutes

def create_pomodoro_schedule(total_minutes: int) -> List[dict]:
    """Create Pomodoro-based study schedule."""
    schedule = []
    current_time = 0
    session_num = 1
    
    while current_time < total_minutes:
        # Work session
        work_duration = min(25, total_minutes - current_time)
        schedule.append({
            "time": f"Minute {current_time}-{current_time + work_duration}",
            "activity": f"Focused Study Session {session_num}"
        })
        current_time += work_duration
        
        # Break (if not at end)
        if current_time < total_minutes:
            break_duration = 5 if session_num % 4 != 0 else 15
            schedule.append({
                "time": f"Minute {current_time}-{current_time + break_duration}",
                "activity": f"Break ({break_duration} min)"
            })
            current_time += break_duration
            session_num += 1
    
    return schedule

def create_single_session_schedule(duration: int) -> List[dict]:
    """Create schedule for single study session."""
    schedule = []
    
    # Warm-up (10% of time)
    warmup = max(5, duration // 10)
    schedule.append({
        "time": f"Minute 0-{warmup}",
        "activity": "Review previous material & set intentions"
    })
    
    # Main study (80% of time)
    main_study = duration - warmup - 5
    schedule.append({
        "time": f"Minute {warmup}-{warmup + main_study}",
        "activity": "Focused learning and practice"
    })
    
    # Wrap-up (5 minutes)
    schedule.append({
        "time": f"Minute {duration-5}-{duration}",
        "activity": "Summarize and plan next steps"
    })
    
    return schedule

def get_subject_techniques(subject: str) -> List[str]:
    """Get study techniques specific to subject."""
    subject_lower = subject.lower()
    
    if "programming" in subject_lower or "coding" in subject_lower:
        return ["Hands-on coding practice", "Code review and debugging", "Building projects"]
    elif "language" in subject_lower:
        return ["Conversation practice", "Immersion techniques", "Grammar exercises"]
    elif "math" in subject_lower:
        return ["Problem-solving practice", "Step-by-step solutions", "Visual representations"]
    else:
        return ["Active recall", "Concept mapping", "Practice problems"]

def generate_style_recommendations(styles: List[str], preferences: str) -> List[str]:
    """Generate recommendations based on learning style."""
    recommendations = []
    
    for style in styles:
        if "visual" in style:
            recommendations.append("Use diagrams, charts, and visual summaries")
        if "auditory" in style:
            recommendations.append("Listen to podcasts and explain concepts aloud")
        if "kinesthetic" in style:
            recommendations.append("Engage in hands-on practice and movement")
        if "reading_writing" in style:
            recommendations.append("Take detailed notes and create written summaries")
    
    return recommendations

def get_style_techniques(styles: List[str]) -> str:
    """Get techniques tailored to learning styles."""
    techniques = []
    
    for style in styles:
        if "visual" in style:
            techniques.append("Mind mapping and visual diagrams")
        if "auditory" in style:
            techniques.append("Record yourself explaining concepts")
        if "kinesthetic" in style:
            techniques.append("Physical practice and real-world application")
        if "reading_writing" in style:
            techniques.append("Summarize concepts in your own words")
    
    return chr(10).join([f"• {tech}" for tech in techniques])
```

### Step 4: Update Main System

**File**: `src/main.py`

```python
# Add import
from src.tools.learning_tools import create_learning_tools

# In create_life_coach() function:
def create_life_coach():
    # ... existing code ...
    
    # Create learning tools
    (
        create_learning_plan_tool,
        analyze_learning_style_tool,
        optimize_study_session_tool
    ) = create_learning_tools(backend=get_backend())
    
    # Learning tools list
    learning_tools = [
        create_learning_plan_tool,
        analyze_learning_style_tool,
        optimize_study_session_tool
    ]
    
    # Get learning specialist
    learning_specialist = get_learning_specialist(
        tools=memory_tools + context_tools + learning_tools
    )
    
    # Update coordinator subagents list
    life_coach = create_deep_agent(
        model=model,
        tools=all_tools + learning_tools,  # Add to coordinator tools
        backend=get_backend(),
        store=memory_store,
        subagents=[
            career_specialist,
            relationship_specialist,
            finance_specialist,
            wellness_specialist,
            learning_specialist,  # Add new specialist
        ],
        system_prompt=get_coordinator_prompt(),
    )
    
    return life_coach
```

### Step 5: Update Coordinator Logic

**File**: `src/agents/coordinator.py`

Add to the coordinator prompt:

```python
# Add to coordinator system prompt in get_coordinator_prompt():

## Domain Expansion: Learning & Education

**NEW: Learning Specialist Available**
When users mention educational goals, skill development, or learning optimization:
- Delegate to learning-specialist for comprehensive learning plans
- Learning intersects with career (professional development), finance (educational ROI), and wellness (study-life balance)
- Consider learning style and preferred techniques when creating recommendations

**Delegation Triggers for Learning**:
- "I want to learn [skill/subject]"
- "Help me study more effectively"
- "What's the best way to learn [topic]"
- Educational planning and resource selection
- Study optimization and retention strategies
```

## Creating Custom Tools

### Tool Development Pattern

All tools follow this consistent pattern:

```python
from langchain_core.tools import tool
from typing import Any, Dict, List, Optional

@tool
def my_custom_tool(
    required_param: str,
    optional_param: Optional[int] = None,
    complex_param: Optional[str] = "{}"
) -> str:
    """
    Brief description of what the tool does.
    
    Args:
        required_param: Description of required parameter
        optional_param: Description of optional parameter (default: None)
        complex_param: JSON string with complex data structure (default: "{}")
    
    Returns:
        User-friendly result message with clear outcomes
        
    Example:
        >>> result = my_custom_tool("example", 42, '{"key": "value"}')
        >>> print(result)
        Tool executed successfully with specified parameters.
    """
    try:
        # Input validation
        if not required_param or not isinstance(required_param, str):
            return "Error: required_param must be a non-empty string"
        
        # Parse complex parameter if provided
        if complex_param and complex_param != "{}":
            try:
                complex_data = json.loads(complex_param)
            except json.JSONDecodeError:
                return "Error: complex_param must be valid JSON"
        else:
            complex_data = {}
        
        # Core tool logic
        result = perform_tool_logic(required_param, optional_param, complex_data)
        
        # Format user-friendly response
        return format_response(result)
        
    except Exception as e:
        return f"Error executing tool: {str(e)}"

def perform_tool_logic(param1: str, param2: Optional[int], data: dict) -> Any:
    """Core logic implementation."""
    # Your tool's main functionality here
    pass

def format_response(result: Any) -> str:
    """Format result into user-friendly message."""
    if isinstance(result, dict):
        return json.dumps(result, indent=2)
    return str(result)
```

### Tool Categories and Examples

#### Analysis Tools

```python
@tool
def analyze_situation(context: str, analysis_type: str) -> str:
    """
    Analyzes a situation and provides structured insights.
    
    Args:
        context: Detailed description of situation to analyze
        analysis_type: Type of analysis (SWOT, root_cause, risk_assessment)
    
    Returns:
        Structured analysis with actionable insights
    """
    # Implementation for various analysis frameworks
    pass
```

#### Planning Tools

```python
@tool
def create_action_plan(goal: str, timeframe: str, resources: str) -> str:
    """
    Creates structured action plan with milestones and dependencies.
    
    Args:
        goal: Specific goal to achieve
        timeframe: Available time for goal completion
        resources: Available resources and constraints
    
    Returns:
        Detailed action plan with timelines and milestones
    """
    # Implementation for goal planning and breaking down
    pass
```

#### Assessment Tools

```python
@tool
def evaluate_progress(user_id: str, goal_id: str, timeframe: str) -> str:
    """
    Evaluates progress toward specific goals.
    
    Args:
        user_id: Unique user identifier
        goal_id: Goal to evaluate progress for
        timeframe: Period to evaluate (week, month, quarter)
    
    Returns:
        Progress assessment with scores and recommendations
    """
    # Implementation for progress tracking and evaluation
    pass
```

#### Resource Tools

```python
@tool
def recommend_resources(topic: str, learning_style: str, budget: str) -> str:
    """
    Recommends educational or professional resources.
    
    Args:
        topic: Subject area or skill to learn
        learning_style: User's preferred learning style
        budget: Available budget for resources
    
    Returns:
        Curated resource recommendations with ratings and access methods
    """
    # Implementation for resource curation and recommendation
    pass
```

## Integrating External Services

### API Integration Pattern

```python
import requests
import os
from langchain_core.tools import tool

@tool
def integrate_external_service(service_name: str, query: str) -> str:
    """
    Integrates with external service for additional data or capabilities.
    
    Args:
        service_name: Name of external service to integrate
        query: Query or request for the external service
    
    Returns:
        Processed response from external service
    """
    try:
        # Get API configuration
        api_key = os.getenv(f"{service_name.upper()}_API_KEY")
        base_url = os.getenv(f"{service_name.upper()}_BASE_URL")
        
        if not api_key or not base_url:
            return f"Error: {service_name} integration not configured"
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{base_url}/query",
            json={"query": query},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return format_external_response(data, service_name)
        else:
            return f"Error from {service_name}: {response.status_code}"
            
    except requests.RequestException as e:
        return f"Network error calling {service_name}: {str(e)}"
    except Exception as e:
        return f"Error integrating with {service_name}: {str(e)}"

def format_external_response(data: dict, service_name: str) -> str:
    """Format external service response for user."""
    # Implementation to format API response
    pass
```

### Example: Weather Integration for Wellness Planning

```python
@tool
def get_weather_impact(location: str, activity: str) -> str:
    """
    Gets weather information and provides wellness activity recommendations.
    
    Args:
        location: User's location for weather data
        activity: Planned wellness activity
    
    Returns:
        Weather-based recommendations and adjustments
    """
    try:
        # Get weather data
        weather_data = get_weather_data(location)
        
        # Analyze impact on planned activity
        impact_analysis = analyze_weather_impact(activity, weather_data)
        
        # Provide recommendations
        recommendations = generate_weather_recommendations(impact_analysis)
        
        return f"""🌤️ **Weather Impact on {activity}**

**Current Weather**: {weather_data['description']} ({weather_data['temperature']}°F)

**Impact Analysis**: {impact_analysis['impact_level']}

**Recommendations**:
{chr(10).join([f"• {rec}" for rec in recommendations])}

**Alternative Activities**: {impact_analysis['alternatives']}
        """
        
    except Exception as e:
        return f"Error getting weather data: {str(e)}"
```

## Custom Memory Backends

### Backend Interface

```python
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

class CustomMemoryBackend(ABC):
    """Interface for custom memory backends."""
    
    @abstractmethod
    def put(self, namespace: Tuple[str, str], key: str, value: Any) -> None:
        """Store a value in the specified namespace."""
        pass
    
    @abstractmethod
    def get(self, namespace: Tuple[str, str], key: str) -> Optional[Any]:
        """Retrieve a value from the specified namespace."""
        pass
    
    @abstractmethod
    def search(self, namespace: Tuple[str, str], query: Optional[str] = None) -> List[Any]:
        """Search for values in the specified namespace."""
        pass
    
    @abstractmethod
    def delete(self, namespace: Tuple[str, str], key: str) -> bool:
        """Delete a value from the specified namespace."""
        pass
```

### Redis Backend Example

```python
import redis
import json
from typing import Any, List, Optional, Tuple

class RedisMemoryBackend(CustomMemoryBackend):
    """Redis-based memory backend for distributed deployments."""
    
    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url)
    
    def _make_key(self, namespace: Tuple[str, str], key: str) -> str:
        """Create Redis key from namespace and key."""
        return f"{namespace[0]}:{namespace[1]}:{key}"
    
    def put(self, namespace: Tuple[str, str], key: str, value: Any) -> None:
        """Store value in Redis."""
        redis_key = self._make_key(namespace, key)
        serialized_value = json.dumps(value, default=str)
        self.client.set(redis_key, serialized_value)
    
    def get(self, namespace: Tuple[str, str], key: str) -> Optional[Any]:
        """Retrieve value from Redis."""
        redis_key = self._make_key(namespace, key)
        value = self.client.get(redis_key)
        
        if value:
            return json.loads(value)
        return None
    
    def search(self, namespace: Tuple[str, str], query: Optional[str] = None) -> List[Any]:
        """Search for values in namespace."""
        pattern = f"{namespace[0]}:{namespace[2]}:*"
        keys = self.client.keys(pattern)
        
        results = []
        for key in keys:
            value = self.client.get(key)
            if value:
                data = json.loads(value)
                if not query or query.lower() in str(data).lower():
                    results.append(data)
        
        return results
    
    def delete(self, namespace: Tuple[str, str], key: str) -> bool:
        """Delete value from Redis."""
        redis_key = self._make_key(namespace, key)
        return bool(self.client.delete(redis_key))
```

### Database Backend Example

```python
import sqlite3
from typing import Any, List, Optional, Tuple

class DatabaseMemoryBackend(CustomMemoryBackend):
    """SQLite database backend for persistent storage."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Create database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memory_store (
                    namespace_user TEXT,
                    namespace_type TEXT,
                    key TEXT,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (namespace_user, namespace_type, key)
                )
            ''')
            conn.commit()
    
    def put(self, namespace: Tuple[str, str], key: str, value: Any) -> None:
        """Store value in database."""
        serialized_value = json.dumps(value, default=str)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO memory_store 
                (namespace_user, namespace_type, key, value)
                VALUES (?, ?, ?, ?)
            ''', (namespace[0], namespace[1], key, serialized_value))
            conn.commit()
    
    def get(self, namespace: Tuple[str, str], key: str) -> Optional[Any]:
        """Retrieve value from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT value FROM memory_store 
                WHERE namespace_user = ? AND namespace_type = ? AND key = ?
            ''', (namespace[0], namespace[1], key))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None
    
    def search(self, namespace: Tuple[str, str], query: Optional[str] = None) -> List[Any]:
        """Search for values in database."""
        with sqlite3.connect(self.db_path) as conn:
            if query:
                cursor = conn.execute('''
                    SELECT value FROM memory_store 
                    WHERE namespace_user = ? AND namespace_type = ?
                    AND value LIKE ?
                ''', (namespace[0], namespace[1], f"%{query}%"))
            else:
                cursor = conn.execute('''
                    SELECT value FROM memory_store 
                    WHERE namespace_user = ? AND namespace_type = ?
                ''', (namespace[0], namespace[1]))
            
            results = []
            for row in cursor.fetchall():
                results.append(json.loads(row[0]))
            
            return results
```

## Advanced Configuration

### Plugin Architecture

```python
import importlib
from typing import Dict, Any, List

class ExtensionManager:
    """Manages loading and configuration of extensions."""
    
    def __init__(self):
        self.extensions: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}
    
    def load_extension(self, extension_name: str, config_path: str = None):
        """Load an extension from module."""
        try:
            module = importlib.import_module(f"extensions.{extension_name}")
            
            # Load configuration
            if config_path:
                with open(config_path, 'r') as f:
                    ext_config = json.load(f)
            else:
                ext_config = {}
            
            # Initialize extension
            if hasattr(module, 'initialize'):
                extension = module.initialize(ext_config)
            else:
                extension = module
            
            self.extensions[extension_name] = extension
            self.config[extension_name] = ext_config
            
            return True
            
        except Exception as e:
            print(f"Failed to load extension {extension_name}: {str(e)}")
            return False
    
    def get_extension(self, name: str) -> Any:
        """Get loaded extension."""
        return self.extensions.get(name)
    
    def list_extensions(self) -> List[str]:
        """List all loaded extensions."""
        return list(self.extensions.keys())

# Usage
extension_manager = ExtensionManager()
extension_manager.load_extension("custom_analytics")
extension_manager.load_extension("integrations")
```

### Configuration Management

```python
import yaml
from pathlib import Path

class ConfigurationManager:
    """Manages system configuration with environment-specific overrides."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config = {}
        self.load_configuration()
    
    def load_configuration(self):
        """Load configuration from YAML files."""
        # Base configuration
        base_config = self._load_yaml("base.yaml")
        
        # Environment-specific configuration
        env = os.getenv("ENVIRONMENT", "development")
        env_config = self._load_yaml(f"{env}.yaml")
        
        # Merge configurations
        self.config = {**base_config, **env_config}
        
        # Override with environment variables
        self._apply_env_overrides()
    
    def _load_yaml(self, filename: str) -> dict:
        """Load YAML configuration file."""
        config_path = self.config_dir / filename
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        # Example: AGENT_MODEL_NAME overrides config
        if os.getenv("AGENT_MODEL_NAME"):
            self.config["model"]["name"] = os.getenv("AGENT_MODEL_NAME")
        
        # Apply other environment overrides
        for key, value in os.environ.items():
            if key.startswith("AI_COACH_"):
                config_key = key[9:].lower().replace('_', '.')
                self.set_nested_config(config_key, value)
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_nested_config(self, key: str, value: str):
        """Set nested configuration value."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

# Usage
config = ConfigurationManager()
model_name = config.get("model.name", "glm-4.7")
```

## Testing Extensions

### Unit Testing Tools

```python
import pytest
from src.tools.learning_tools import create_learning_plan

class TestLearningTools:
    """Test suite for learning tools."""
    
    def test_create_learning_plan_basic(self):
        """Test basic learning plan creation."""
        result = create_learning_plan(
            user_id="test_user",
            learning_goal="Learn Python",
            timeframe="3 months",
            current_knowledge="Complete beginner"
        )
        
        assert isinstance(result, str)
        assert "Learning plan created successfully" in result
        assert "Python" in result
        assert "3 months" in result
    
    def test_create_learning_plan_invalid_input(self):
        """Test error handling for invalid inputs."""
        result = create_learning_plan("", "Learn Python", "3 months", "Beginner")
        assert "Error" in result
    
    def test_create_learning_plan_file_creation(self, tmp_path):
        """Test that learning plan files are created correctly."""
        # Mock backend for testing
        class MockBackend:
            def __init__(self, path):
                self.path = Path(path)
                self.path.mkdir(parents=True, exist_ok=True)
            
            def write_file(self, file_path, content):
                full_path = self.path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
        
        backend = MockBackend(tmp_path)
        tools = create_learning_tools(backend)
        
        # Create learning plan
        tools[0]("test_user", "Learn Python", "3 months", "Beginner")
        
        # Verify file was created
        plan_file = tmp_path / "workspace/learning_plans/test_user/Learn_Python_plan.json"
        assert plan_file.exists()
        
        # Verify content
        content = plan_file.read_text()
        plan_data = json.loads(content)
        assert plan_data["goal"] == "Learn Python"
        assert plan_data["timeframe"] == "3 months"
```

### Integration Testing

```python
import pytest
from src.main import create_life_coach

class TestLearningSpecialistIntegration:
    """Test integration of learning specialist with main system."""
    
    @pytest.fixture
    def coach_with_learning(self):
        """Create coach with learning specialist."""
        return create_life_coach()
    
    def test_learning_goal_delegation(self, coach_with_learning):
        """Test that learning goals are delegated to learning specialist."""
        result = coach_with_learning.invoke({
            "messages": [{
                "role": "user",
                "content": "I want to learn data science in 6 months. Where should I start?"
            }]
        })
        
        response = result["messages"][-1].content
        
        # Should contain learning-specific advice
        assert any(term in response.lower() for term in ["learn", "study", "course", "plan"])
        
        # Should be structured as a learning plan
        assert "phase" in response.lower() or "step" in response.lower()
    
    def test_cross_domain_learning_integration(self, coach_with_learning):
        """Test integration of learning with other domains."""
        result = coach_with_learning.invoke({
            "messages": [{
                "role": "user",
                "content": "I want to learn Python to get a better job, but I'm worried about the cost and time commitment."
            }]
        })
        
        response = result["messages"][-1].content
        
        # Should address learning, career, and financial aspects
        assert "learn" in response.lower() or "study" in response.lower()
        assert "career" in response.lower() or "job" in response.lower()
        assert "cost" in response.lower() or "financial" in response.lower()
```

### Performance Testing

```python
import time
from src.tools.learning_tools import create_learning_plan

class TestPerformance:
    """Performance testing for extensions."""
    
    def test_tool_response_time(self):
        """Test that tools respond within acceptable time limits."""
        start_time = time.time()
        
        result = create_learning_plan(
            user_id="perf_test_user",
            learning_goal="Learn Machine Learning",
            timeframe="6 months",
            current_knowledge="Some programming experience"
        )
        
        response_time = time.time() - start_time
        
        # Should respond within 5 seconds
        assert response_time < 5.0
        assert result is not None
    
    def test_concurrent_tool_usage(self):
        """Test tool performance under concurrent usage."""
        import concurrent.futures
        
        def create_plan(user_id):
            return create_learning_plan(
                user_id=user_id,
                learning_goal="Learn Python",
                timeframe="3 months",
                current_knowledge="Beginner"
            )
        
        # Create plans concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_plan, f"user_{i}") for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert len(results) == 10
        assert all("Learning plan created successfully" in r for r in results)
```

## Performance Considerations

### Tool Optimization

```python
from functools import lru_cache
import asyncio

class OptimizedTools:
    """Optimized version of tools with caching and async support."""
    
    @lru_cache(maxsize=128)
    @staticmethod
    def cached_analysis(analysis_hash: str) -> str:
        """Cached version of analysis tool."""
        # Implementation that uses cached results for identical queries
        pass
    
    @staticmethod
    async def async_tool_execution(tools_with_args: List[tuple]) -> List[str]:
        """Execute multiple tools concurrently when possible."""
        
        # Group independent tools
        independent_tools = []
        dependent_tools = []
        
        for tool_func, args in tools_with_args:
            if is_independent_tool(tool_func):
                independent_tools.append((tool_func, args))
            else:
                dependent_tools.append((tool_func, args))
        
        # Execute independent tools concurrently
        results = []
        if independent_tools:
            concurrent_results = await asyncio.gather(*[
                run_tool_async(tool, args) for tool, args in independent_tools
            ])
            results.extend(concurrent_results)
        
        # Execute dependent tools sequentially
        for tool_func, args in dependent_tools:
            result = await run_tool_async(tool_func, args)
            results.append(result)
        
        return results

def is_independent_tool(tool_func) -> bool:
    """Determine if tool can be executed independently."""
    # Logic to check tool dependencies
    independent_tools = {
        "analyze_learning_style",
        "optimize_study_session"
    }
    return tool_func.__name__ in independent_tools

async def run_tool_async(tool_func, args):
    """Run tool function asynchronously."""
    # Wrap synchronous tools for async execution
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, tool_func, *args)
```

### Memory Optimization

```python
class MemoryOptimizedManager:
    """Memory management for extended systems."""
    
    def __init__(self, max_memory_usage: int = 1000):  # MB
        self.max_memory = max_memory_usage
        self.current_usage = 0
        self.access_counts = {}
        self.last_access = {}
    
    def should_cache(self, key: str, value: Any) -> bool:
        """Determine if value should be cached based on memory constraints."""
        value_size = self._estimate_size(value)
        
        if self.current_usage + value_size > self.max_memory:
            self._evict_least_used()
        
        return self.current_usage + value_size <= self.max_memory
    
    def cache_value(self, key: str, value: Any):
        """Cache value with memory management."""
        if self.should_cache(key, value):
            self.current_usage += self._estimate_size(value)
            self.access_counts[key] = 0
            self.last_access[key] = time.time()
            # Store value in cache
            return True
        return False
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate memory usage of value in MB."""
        import sys
        return sys.getsizeof(value) / (1024 * 1024)
    
    def _evict_least_used(self):
        """Evict least frequently used items from cache."""
        # LRU eviction logic
        pass
```

## Deployment and Scaling

### Container Configuration

```dockerfile
# Dockerfile for extended AI Life Coach
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY extensions/ ./extensions/
COPY config/ ./config/

# Create workspace directory
RUN mkdir -p workspace/{user_profile,assessments,plans,progress,resources}

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "src.main"]
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-life-coach
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-life-coach
  template:
    metadata:
      labels:
        app: ai-life-coach
    spec:
      containers:
      - name: ai-life-coach
        image: ai-life-coach:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: ai-coach-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Monitoring and Observability

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics for extension monitoring
TOOL_EXECUTION_COUNT = Counter(
    'tool_executions_total',
    'Total number of tool executions',
    ['tool_name', 'status']
)

TOOL_EXECUTION_DURATION = Histogram(
    'tool_execution_duration_seconds',
    'Time spent executing tools',
    ['tool_name']
)

ACTIVE_SPECIALISTS = Gauge(
    'active_specialists',
    'Number of active specialist agents'
)

class MetricsCollector:
    """Collect metrics for monitoring system performance."""
    
    def __init__(self):
        self.tool_counts = {}
        self.response_times = {}
    
    def record_tool_execution(self, tool_name: str, duration: float, success: bool):
        """Record tool execution metrics."""
        TOOL_EXECUTION_COUNT.labels(
            tool_name=tool_name,
            status='success' if success else 'error'
        ).inc()
        
        TOOL_EXECUTION_DURATION.labels(tool_name=tool_name).observe(duration)
    
    def update_active_specialists(self, count: int):
        """Update active specialists count."""
        ACTIVE_SPECIALISTS.set(count)

# Decorator for automatic metric collection
def with_metrics(tool_name: str):
    """Decorator to automatically collect metrics for tools."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.record_tool_execution(tool_name, duration, success)
        
        return wrapper
    return decorator

# Usage
@with_metrics("create_learning_plan")
def create_learning_plan(user_id: str, learning_goal: str, timeframe: str, current_knowledge: str) -> str:
    # Tool implementation
    pass
```

---

## Conclusion

The AI Life Coach system is designed to be highly extensible, allowing developers to add new capabilities while maintaining the quality and consistency of the core system. By following the patterns and guidelines in this guide, you can:

- Add new domain specialists for additional life areas
- Create custom tools for specialized functionality
- Integrate with external services and APIs
- Implement custom memory backends for different deployment scenarios
- Scale the system for production use

Remember to always test extensions thoroughly, consider cross-domain impacts, and maintain the user-centric approach that makes the AI Life Coach effective.

For specific implementation details, refer to the existing specialist implementations and tool examples in the codebase.