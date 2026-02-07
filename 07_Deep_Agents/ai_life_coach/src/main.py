"""
Main module for AI Life Coach.

This module provides the create_life_coach function which initializes
the full multi-agent system with all specialist subagents.
"""

from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

# Import configuration
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config, get_backend
from src.tools.memory_tools import create_memory_tools
from src.tools.planning_tools import create_planning_tools
from src.tools.context_tools import create_context_tools
from src.tools.assessment_tools import create_assessment_tools
from src.tools.career_tools import create_career_tools
from src.tools.relationship_tools import create_relationship_tools
from src.tools.finance_tools import create_finance_tools
from src.tools.wellness_tools import create_wellness_tools
from src.tools.cross_domain_tools import create_cross_domain_tools
from src.tools.goal_dependency_tools import create_goal_dependency_tools
from src.tools.viz_tools import create_viz_tools
from src.tools.communication_tools import create_communication_tools
from src.tools.integration_tools import create_integration_tools
from src.tools.phase_planning_tools import create_phase_planning_tools
from src.tools.checkin_tools import create_checkin_tools
from src.tools.adaptive_tools import create_adaptive_tools
from src.tools.mood_tools import create_mood_tools
from src.tools.reflection_tools import create_reflection_tools
from src.tools.dashboard_tools import create_dashboard_tools
from src.tools.habit_tools import create_habit_tools
from src.tools.resource_tools import create_resource_tools
from src.tools.emergency_tools import create_emergency_tools
from src.tools.user_tools import create_user_tools
from src.agents import get_all_specialists
from src.agents.coordinator import get_coordinator_prompt


def create_life_coach():
    """
    Create and configure the AI Life Coach coordinator agent.

    This is the main entry point for creating a complete AI Life Coach system
    with all four domain specialists and memory tools.

    Returns:
        CompiledStateGraph: The configured Life Coach agent ready for use

    Example:
        >>> coach = create_life_coach()
        >>> result = coach.invoke({
        ...     "messages": [{
        ...         "role": "user",
        ...         "content": "I need help with my career and relationships"
        ...     }]
        ... })
    """
    # Initialize environment
    config.initialize_environment()

    # Create model instance
    model_config = config.model.get_model_config()
    model = init_chat_model(model_config)

    # Create memory tools
    from src.memory import create_memory_store

    memory_store = create_memory_store()
    (
        get_user_profile,
        save_user_preference,
        update_milestone,
        get_progress_history,
    ) = create_memory_tools(memory_store)

    # Create planning tools
    write_todos, update_todo, list_todos = create_planning_tools()

    # Create context tools
    (
        save_assessment,
        get_active_plan,
        save_weekly_progress,
        list_user_assessments,
        read_assessment,
        save_curated_resource,
    ) = create_context_tools(backend=get_backend())

    # Create multi-domain assessment tools
    (
        conduct_initial_assessment,
        prioritize_domains_by_urgency,
        assess_cross_domain_impacts,
        generate_integrated_report,
        design_follow_up_questions,
    ) = create_assessment_tools(backend=get_backend())

    # Create career tools for the Career Specialist
    (
        analyze_skill_gap,
        create_career_path_plan,
        optimize_resume,
        generate_interview_prep,
        research_salary_benchmarks,
        calculate_skill_match_score,
        estimate_salary_range,
    ) = create_career_tools(backend=get_backend())

    # Create relationship tools for the Relationship Specialist
    (
        analyze_communication_style,
        create_boundary_setting_plan,
        apply_dear_man_technique,
        assess_relationship_quality,
        develop_social_connection_plan,
        calculate_relationship_score,
        assess_communication_compatibility,
    ) = create_relationship_tools(backend=get_backend())

    # Create finance tools for the Finance Specialist
    (
        create_budget_analyzer,
        generate_debt_payoff_plan,
        calculate_emergency_fund_target,
        set_financial_goal,
        analyze_expense_optimization,
        calculate_savings_timeline,
        calculate_compound_interest,
        calculate_budget_ratio,
        estimate_debt_free_date,
    ) = create_finance_tools(backend=get_backend())

    # Create wellness tools for the Wellness Specialist
    (
        assess_wellness_dimensions,
        create_habit_formation_plan,
        provide_stress_management_techniques,
        create_sleep_optimization_plan,
        design_exercise_program,
        calculate_wellness_score,
        track_habit_consistency,
    ) = create_wellness_tools(backend=get_backend())

    # Create cross-domain integration tools for the coordinator
    (
        build_goal_dependency_graph,
        analyze_cross_domain_impacts,
        detect_goal_conflicts,
        recommend_priority_adjustments,
        generate_integration_plan,
    ) = create_cross_domain_tools(backend=get_backend())

    # Create goal dependency mapping tools for advanced graph analysis
    (
        build_goal_dependency_graph_advanced,
        detect_implicit_dependencies,
        simulate_goal_impact,
        visualize_dependency_graph,
        find_critical_path,
        suggest_dependency_resolutions,
    ) = create_goal_dependency_tools(backend=get_backend())

    # Create goal dependency visualization tools for advanced visual analysis
    (
        render_ascii_graph,
        explore_dependencies_interactive,
        highlight_critical_path,
        what_if_add_goal,
        what_if_remove_goal,
        generate_dependency_report_tool,
    ) = create_viz_tools(backend=get_backend())

    # Create communication protocol tools for subagent coordination
    (
        format_specialist_message,
        aggregate_results,
        resolve_conflicts,
        detect_cross_consultation,
        generate_unified_response_tool,
    ) = create_communication_tools(backend=get_backend())

    # Create integration tools for advanced result synthesis
    (
        harmonize_specialist_outputs,
        synthesize_cross_domain_insights,
        generate_prioritized_action_list,
        create_unified_response,
    ) = create_integration_tools(backend=get_backend())

    # Create phase-based planning tools for advanced workflow management
    (
        initialize_phase_workflow,
        transition_to_next_phase,
        generate_milestones_from_goals_tool,
        adapt_plan_based_on_progress,
        get_phase_status,
        apply_phase_template_tool,
    ) = create_phase_planning_tools(backend=get_backend())

    # Create weekly check-in tools for comprehensive progress tracking
    (
        conduct_weekly_checkin,
        calculate_progress_score,
        analyze_weekly_trends,
        generate_adaptation_recommendations,
        generate_weekly_report,
    ) = create_checkin_tools(backend=get_backend())

    # Create adaptive recommendation tools for personalized learning
    (
        track_recommendation_response,
        calculate_recommendation_effectiveness,
        learn_user_preferences,
        detect_adaptation_triggers,
        generate_personalized_alternatives,
        get_adaptive_recommendations_history,
    ) = create_adaptive_tools(backend=get_backend())

    # Create mood tracking tools with sentiment analysis
    (
        log_mood_entry,
        analyze_text_sentiment,
        calculate_mood_score,
        generate_mood_trend_chart,
        analyze_mood_progress_correlation,
        detect_mood_triggers,
        get_mood_history,
    ) = create_mood_tools(backend=get_backend())

    # Create reflection prompt tools for personalized weekly reflections
    (
        generate_weekly_reflection_prompts,
        save_reflection_response,
        get_reflection_history,
        extract_insights_from_reflections,
        trigger_milestone_reflection,
        trigger_setback_reflection,
    ) = create_reflection_tools(backend=get_backend())

    # Create progress dashboard tools for comprehensive progress visualization
    (
        render_progress_dashboard,
        calculate_life_satisfaction_score,
        generate_domain_progress_bar,
        create_mood_trend_sparkline,
        get_recent_achievements,
        get_upcoming_milestones,
        export_dashboard_report,
        switch_dashboard_view,
    ) = create_dashboard_tools(backend=get_backend())

    # Create habit tracking tools based on Atomic Habits framework
    (
        create_habit,
        log_habit_completion,
        get_habit_streaks,
        calculate_habit_strength_score,
        get_habit_stacking_suggestions,
        get_habits_by_domain,
        review_habit,
        update_habit,
        delete_habit,
        list_habits,
    ) = create_habit_tools(backend=get_backend())

    # List of planning tools for task management
    planning_tools = [write_todos, update_todo, list_todos]

    # List of phase-based planning tools for advanced workflow management
    phase_planning_tools = [
        initialize_phase_workflow,
        transition_to_next_phase,
        generate_milestones_from_goals_tool,
        adapt_plan_based_on_progress,
        get_phase_status,
        apply_phase_template_tool,
    ]

    # List of weekly check-in tools for comprehensive progress tracking
    checkin_tools = [
        conduct_weekly_checkin,
        calculate_progress_score,
        analyze_weekly_trends,
        generate_adaptation_recommendations,
        generate_weekly_report,
    ]

    # List of adaptive recommendation tools for personalized learning
    adaptive_tools = [
        track_recommendation_response,
        calculate_recommendation_effectiveness,
        learn_user_preferences,
        detect_adaptation_triggers,
        generate_personalized_alternatives,
        get_adaptive_recommendations_history,
    ]

    # List of mood tracking tools for emotional monitoring
    mood_tools = [
        log_mood_entry,
        analyze_text_sentiment,
        calculate_mood_score,
        generate_mood_trend_chart,
        analyze_mood_progress_correlation,
        detect_mood_triggers,
        get_mood_history,
    ]

    # List of reflection prompt tools for weekly reflections
    reflection_tools = [
        generate_weekly_reflection_prompts,
        save_reflection_response,
        get_reflection_history,
        extract_insights_from_reflections,
        trigger_milestone_reflection,
        trigger_setback_reflection,
    ]

    # List of progress dashboard tools for visualization
    dashboard_tools = [
        render_progress_dashboard,
        calculate_life_satisfaction_score,
        generate_domain_progress_bar,
        create_mood_trend_sparkline,
        get_recent_achievements,
        get_upcoming_milestones,
        export_dashboard_report,
        switch_dashboard_view,
    ]

    # List of habit tracking tools for behavior change
    habit_tools = [
        create_habit,
        log_habit_completion,
        get_habit_streaks,
        calculate_habit_strength_score,
        get_habit_stacking_suggestions,
        get_habits_by_domain,
        review_habit,
        update_habit,
        delete_habit,
        list_habits,
    ]

    # Create resource curation tools for learning content management
    (
        add_resource,
        search_resources,
        get_recommendations,
        rate_resource,
        track_resource_progress,
        get_resource_details,
        get_user_resource_stats,
        get_available_tags,
    ) = create_resource_tools(backend=get_backend())

    # List of resource curation tools
    resource_tools = [
        add_resource,
        search_resources,
        get_recommendations,
        rate_resource,
        track_resource_progress,
        get_resource_details,
        get_user_resource_stats,
        get_available_tags,
    ]

    # Create emergency support tools for crisis intervention
    (
        analyze_crisis_risk,
        get_immediate_resources,
        create_safety_plan,
        get_safety_plan_template,
        schedule_followup_checkin,
        complete_followup_checkin,
        get_crisis_protocol_guidance,
        generate_crisis_response,
    ) = create_emergency_tools(backend=get_backend())

    # Create user management tools for multi-user support
    (
        create_user,
        authenticate_user,
        logout_user,
        switch_user,
        get_current_user,
        update_user_profile,
        list_all_users,
        delete_user,
        validate_session_token,
        get_user_session_info,
        change_user_password,
    ) = create_user_tools(store=memory_store)

    # List of emergency support tools for crisis detection and response
    emergency_tools = [
        analyze_crisis_risk,
        get_immediate_resources,
        create_safety_plan,
        get_safety_plan_template,
        schedule_followup_checkin,
        complete_followup_checkin,
        get_crisis_protocol_guidance,
        generate_crisis_response,
    ]

    # List of user management tools for multi-user support
    user_tools = [
        create_user,
        authenticate_user,
        logout_user,
        switch_user,
        get_current_user,
        update_user_profile,
        list_all_users,
        delete_user,
        validate_session_token,
        get_user_session_info,
        change_user_password,
    ]

    # List of memory tools to pass to agents
    memory_tools = [
        get_user_profile,
        save_user_preference,
        update_milestone,
        get_progress_history,
    ]

    # List of context tools for file operations
    context_tools = [
        save_assessment,
        get_active_plan,
        save_weekly_progress,
        list_user_assessments,
        read_assessment,
        save_curated_resource,
    ]

    # List of multi-domain assessment tools
    assessment_tools = [
        conduct_initial_assessment,
        prioritize_domains_by_urgency,
        assess_cross_domain_impacts,
        generate_integrated_report,
        design_follow_up_questions,
    ]

    # List of career tools for Career Specialist
    career_tools = [
        analyze_skill_gap,
        create_career_path_plan,
        optimize_resume,
        generate_interview_prep,
        research_salary_benchmarks,
        calculate_skill_match_score,
        estimate_salary_range,
    ]

    # List of relationship tools for Relationship Specialist
    relationship_tools = [
        analyze_communication_style,
        create_boundary_setting_plan,
        apply_dear_man_technique,
        assess_relationship_quality,
        develop_social_connection_plan,
        calculate_relationship_score,
        assess_communication_compatibility,
    ]

    # List of finance tools for Finance Specialist
    finance_tools = [
        create_budget_analyzer,
        generate_debt_payoff_plan,
        calculate_emergency_fund_target,
        set_financial_goal,
        analyze_expense_optimization,
        calculate_savings_timeline,
        calculate_compound_interest,
        calculate_budget_ratio,
        estimate_debt_free_date,
    ]

    # List of wellness tools for Wellness Specialist
    wellness_tools = [
        assess_wellness_dimensions,
        create_habit_formation_plan,
        provide_stress_management_techniques,
        create_sleep_optimization_plan,
        design_exercise_program,
        calculate_wellness_score,
        track_habit_consistency,
    ]

    # List of cross-domain tools for the main coordinator
    cross_domain_tools = [
        build_goal_dependency_graph,
        analyze_cross_domain_impacts,
        detect_goal_conflicts,
        recommend_priority_adjustments,
        generate_integration_plan,
        # Advanced goal dependency mapping tools
        build_goal_dependency_graph_advanced,
        detect_implicit_dependencies,
        simulate_goal_impact,
        visualize_dependency_graph,
        find_critical_path,
        suggest_dependency_resolutions,
        # Advanced goal dependency visualization tools
        render_ascii_graph,
        explore_dependencies_interactive,
        highlight_critical_path,
        what_if_add_goal,
        what_if_remove_goal,
        generate_dependency_report_tool,
    ]

    # List of communication tools for subagent coordination
    communication_tools = [
        format_specialist_message,
        aggregate_results,
        resolve_conflicts,
        detect_cross_consultation,
        generate_unified_response_tool,
    ]

    # List of integration tools for advanced result synthesis
    integration_tools = [
        harmonize_specialist_outputs,
        synthesize_cross_domain_insights,
        generate_prioritized_action_list,
        create_unified_response,
    ]

    # Combined tools for the main coordinator
    all_tools = (
        memory_tools
        + planning_tools
        + phase_planning_tools
        + checkin_tools
        + adaptive_tools
        + mood_tools
        + reflection_tools
        + dashboard_tools
        + habit_tools
        + resource_tools
        + emergency_tools
        + context_tools
        + assessment_tools
        + cross_domain_tools
        + communication_tools
        + integration_tools
        + user_tools
    )

    # Get specialist subagents with appropriate tool allocation
    # Career Specialist gets memory + context + career tools (no planning - coordinator handles)
    career_specialist_tools = memory_tools + context_tools + career_tools
    # Relationship Specialist gets memory + context + relationship tools (no planning - coordinator handles)
    relationship_specialist_tools = memory_tools + context_tools + relationship_tools
    # Finance Specialist gets memory + context + finance tools (no planning - coordinator handles)
    finance_specialist_tools = memory_tools + context_tools + finance_tools
    # Wellness Specialist gets memory + context + wellness tools + habit tools (no planning - coordinator handles)
    wellness_specialist_tools = (
        memory_tools + context_tools + wellness_tools + mood_tools + habit_tools
    )

    career_specialist, relationship_specialist, finance_specialist, wellness_specialist = (
        get_all_specialists()
    )

    # Assign tools to each specialist
    # Career Specialist gets career-specific tools in addition to memory/context
    career_specialist["tools"] = career_specialist_tools
    # Relationship Specialist gets relationship-specific tools in addition to memory/context
    relationship_specialist["tools"] = relationship_specialist_tools
    # Finance Specialist gets finance-specific tools in addition to memory/context
    finance_specialist["tools"] = finance_specialist_tools
    # Wellness Specialist gets wellness-specific tools in addition to memory/context
    wellness_specialist["tools"] = wellness_specialist_tools

    # Create the main coordinator agent with comprehensive system prompt
    life_coach = create_deep_agent(
        model=model,
        tools=all_tools,  # Include both memory and planning tools for the coordinator
        backend=get_backend(),  # Use FilesystemBackend for workspace operations
        store=memory_store,  # Pass InMemoryStore for long-term memory persistence
        subagents=[
            career_specialist,
            relationship_specialist,
            finance_specialist,
            wellness_specialist,
        ],
        system_prompt=get_coordinator_prompt(),
    )

    return life_coach


if __name__ == "__main__":
    # Example usage
    print("Creating AI Life Coach...")
    coach = create_life_coach()
    print("AI Life Coach created successfully!")
    print("\nExample session:")
    print("-" * 60)
    result = coach.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! Can you introduce yourself and explain how you can help me?",
                }
            ]
        }
    )
    print(result["messages"][-1].content)
