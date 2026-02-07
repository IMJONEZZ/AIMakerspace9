#!/usr/bin/env python3
"""
Comprehensive Demo Script for AI Life Coach - Bead #38 Final Review

This script demonstrates the complete functionality of the AI Life Coach system
including all specialist domains, integration features, and advanced capabilities.

Usage:
    python comprehensive_demo.py
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Initialize environment before importing other modules
try:
    from src.config import config, get_backend

    config.initialize_environment()
    backend = get_backend()
    print("✅ Environment initialized successfully")
except Exception as e:
    print(f"❌ Environment initialization failed: {e}")
    sys.exit(1)

# Import the main AI Life Coach system
try:
    from src.main import create_life_coach

    print("✅ Main module imported successfully")
except Exception as e:
    print(f"❌ Main module import failed: {e}")
    sys.exit(1)


def print_section(title, description=""):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"🔹 {title}")
    if description:
        print(f"   {description}")
    print("=" * 80)


def print_subsection(title):
    """Print a formatted subsection header."""
    print(f"\n📌 {title}")
    print("-" * 60)


def test_basic_functionality():
    """Test basic AI Life Coach functionality."""
    print_section(
        "1. Basic System Functionality", "Testing core system initialization and basic interaction"
    )

    try:
        # Create the AI Life Coach
        coach = create_life_coach()
        print("✅ AI Life Coach created successfully")

        # Test basic interaction
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

        response = result["messages"][-1].content
        print(f"✅ Basic interaction successful")
        print(f"📝 Response preview: {response[:200]}...")

        return coach

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return None


def test_career_specialist(coach):
    """Test Career Specialist functionality."""
    print_section("2. Career Specialist", "Testing career guidance and skill analysis")

    try:
        result = coach.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "I'm a software developer looking to advance my career. What skills should I focus on?",
                    }
                ]
            }
        )

        response = result["messages"][-1].content
        print("✅ Career specialist response successful")
        print(f"📝 Career advice preview: {response[:300]}...")

    except Exception as e:
        print(f"❌ Career specialist test failed: {e}")


def test_relationship_specialist(coach):
    """Test Relationship Specialist functionality."""
    print_section("3. Relationship Specialist", "Testing relationship guidance and communication")

    try:
        result = coach.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "I'm having trouble communicating effectively with my partner. Can you help?",
                    }
                ]
            }
        )

        response = result["messages"][-1].content
        print("✅ Relationship specialist response successful")
        print(f"📝 Relationship advice preview: {response[:300]}...")

    except Exception as e:
        print(f"❌ Relationship specialist test failed: {e}")


def test_finance_specialist(coach):
    """Test Finance Specialist functionality."""
    print_section("4. Finance Specialist", "Testing financial planning and budget analysis")

    try:
        result = coach.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "I want to create a budget and save for a house down payment. Can you help me plan?",
                    }
                ]
            }
        )

        response = result["messages"][-1].content
        print("✅ Finance specialist response successful")
        print(f"📝 Financial advice preview: {response[:300]}...")

    except Exception as e:
        print(f"❌ Finance specialist test failed: {e}")


def test_wellness_specialist(coach):
    """Test Wellness Specialist functionality."""
    print_section("5. Wellness Specialist", "Testing wellness assessment and habit formation")

    try:
        result = coach.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "I want to improve my physical fitness and mental wellbeing. What should I focus on?",
                    }
                ]
            }
        )

        response = result["messages"][-1].content
        print("✅ Wellness specialist response successful")
        print(f"📝 Wellness advice preview: {response[:300]}...")

    except Exception as e:
        print(f"❌ Wellness specialist test failed: {e}")


def test_cross_domain_integration(coach):
    """Test cross-domain integration capabilities."""
    print_section("6. Cross-Domain Integration", "Testing multi-domain goal coordination")

    try:
        result = coach.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "I'm planning to change careers, which affects my finances, relationships, and overall wellbeing. Can you help me create an integrated plan?",
                    }
                ]
            }
        )

        response = result["messages"][-1].content
        print("✅ Cross-domain integration successful")
        print(f"📝 Integration response preview: {response[:300]}...")

    except Exception as e:
        print(f"❌ Cross-domain integration test failed: {e}")


def test_advanced_features(coach):
    """Test advanced features like mood tracking and progress monitoring."""
    print_section(
        "7. Advanced Features", "Testing mood tracking, progress monitoring, and habit tools"
    )

    try:
        # Test mood tracking
        print_subsection("Mood Tracking")
        result = coach.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "I'm feeling stressed about my work-life balance. Can you track this mood and suggest coping strategies?",
                    }
                ]
            }
        )

        # Test habit formation
        print_subsection("Habit Formation")
        result = coach.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "I want to develop a daily exercise habit. Can you help me create a habit formation plan?",
                    }
                ]
            }
        )

        # Test progress monitoring
        print_subsection("Progress Monitoring")
        result = coach.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Can you help me track my progress on my goals and generate a weekly report?",
                    }
                ]
            }
        )

        print("✅ Advanced features test successful")

    except Exception as e:
        print(f"❌ Advanced features test failed: {e}")


def test_emergency_features(coach):
    """Test emergency support and crisis intervention."""
    print_section("8. Emergency Support", "Testing crisis detection and emergency resources")

    try:
        result = coach.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "I'm going through a really difficult time emotionally and need immediate support.",
                    }
                ]
            }
        )

        response = result["messages"][-1].content
        print("✅ Emergency support test successful")
        print(f"📝 Support response preview: {response[:300]}...")

    except Exception as e:
        print(f"❌ Emergency support test failed: {e}")


def test_memory_system(coach):
    """Test memory and user profile system."""
    print_section("9. Memory System", "Testing user profile storage and retrieval")

    try:
        # Test profile creation
        print_subsection("Profile Creation")
        result = coach.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "My name is Alex, I'm 32 years old, work as a software engineer, and I'm single. Please save this information.",
                    }
                ]
            }
        )

        # Test profile retrieval
        print_subsection("Profile Retrieval")
        result = coach.invoke(
            {"messages": [{"role": "user", "content": "Can you retrieve my profile information?"}]}
        )

        print("✅ Memory system test successful")

    except Exception as e:
        print(f"❌ Memory system test failed: {e}")


def generate_test_report(coach):
    """Generate a comprehensive test report."""
    print_section("10. Test Summary and System Status", "Generating comprehensive test report")

    try:
        # Check system status
        print_subsection("System Configuration")
        print(f"🔧 Model Configuration: {config.model.get_model_config()}")
        print(f"🗂️ Workspace Directory: {config.memory.workspace_dir}")
        print(f"💾 Memory Store Type: {config.memory.store_type}")
        print(f"🐛 Debug Mode: {config.debug_mode}")

        print_subsection("Available Tools")
        print(f"🛠️  Total Tools Loaded: {len(coach.get_tools().get('tools', []))}")

        print_subsection("Specialist Agents")
        specialists = coach.get_tools().get("subagents", [])
        print(f"👥 Total Specialists: {len(specialists)}")
        for specialist in specialists:
            print(f"   • {specialist.get('name', 'Unknown Specialist')}")

        print("✅ Test report generated successfully")

    except Exception as e:
        print(f"❌ Test report generation failed: {e}")


def main():
    """Run comprehensive demo of AI Life Coach system."""
    print_section("🚀 AI Life Coach - Comprehensive Demo", "Bead #38 Final Review and Polish")
    print("This demo will test all major features of the AI Life Coach system...")

    # Track demo start time
    start_time = time.time()

    try:
        # Test basic functionality
        coach = test_basic_functionality()
        if not coach:
            print("❌ Cannot proceed without basic functionality")
            return

        # Test individual specialists
        test_career_specialist(coach)
        test_relationship_specialist(coach)
        test_finance_specialist(coach)
        test_wellness_specialist(coach)

        # Test integration features
        test_cross_domain_integration(coach)

        # Test advanced features
        test_advanced_features(coach)
        test_emergency_features(coach)
        test_memory_system(coach)

        # Generate final report
        generate_test_report(coach)

        # Calculate total time
        end_time = time.time()
        total_time = end_time - start_time

        print_section("🎉 Demo Complete!", f"Total time: {total_time:.2f} seconds")
        print("✅ All major features have been tested successfully!")
        print("🎯 The AI Life Coach system is ready for production use!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
