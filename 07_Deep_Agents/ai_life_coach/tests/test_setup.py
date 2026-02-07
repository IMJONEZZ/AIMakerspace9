#!/usr/bin/env python3
"""
Quick test script to verify AI Life Coach setup is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        from deepagents import create_deep_agent

        print("  ✓ deepagents imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import deepagents: {e}")
        return False

    try:
        from langchain.chat_models import init_chat_model

        print("  ✓ langchain imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import langchain: {e}")
        return False

    try:
        from dotenv import load_dotenv

        print("  ✓ python-dotenv imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import python-dotenv: {e}")
        return False

    return True


def test_structure():
    """Test that all required directories and files exist."""
    print("\nTesting project structure...")

    required_dirs = [
        "src",
        "skills/career-assessment",
        "skills/relationship-building",
        "skills/financial-planning",
        "skills/wellness-optimization",
        "workspace/user_profile",
        "workspace/assessments",
        "workspace/plans",
        "workspace/progress",
        "workspace/resources",
        "tests",
        "docs",
    ]

    required_files = [
        ".env.example",
        "pyproject.toml",
        "README.md",
        "src/__init__.py",
        "src/config.py",
        "src/main.py",
        "skills/career-assessment/SKILL.md",
        "skills/relationship-building/SKILL.md",
        "skills/financial-planning/SKILL.md",
        "skills/wellness-optimization/SKILL.md",
    ]

    all_good = True

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ (missing)")
            all_good = False

    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists() and full_path.is_file():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (missing)")
            all_good = False

    return all_good


def test_config():
    """Test configuration module."""
    print("\nTesting configuration...")

    try:
        from src.config import config

        print("  ✓ Config module imported")

        # Test environment initialization
        config.initialize_environment()
        print("  ✓ Environment initialized")

        return True
    except Exception as e:
        print(f"  ✗ Config test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Life Coach Setup Verification")
    print("=" * 60)

    results = {"imports": test_imports(), "structure": test_structure(), "config": test_config()}

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")

    all_passed = all(results.values())

    print("=" * 60)
    if all_passed:
        print("All tests passed! Setup is complete. ✓")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your API keys")
        print("2. Run 'python src/main.py' to test the system")
    else:
        print("Some tests failed. Please review the errors above.")
        sys.exit(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
