#!/usr/bin/env python3
"""
Simple test script for the production AI Life Coach CLI.

This tests basic functionality without requiring interactive input.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from life_coach_cli import AILifeCoachCLI, SessionManager


def test_session_manager():
    """Test session manager functionality."""
    print("Testing Session Manager...")

    sm = SessionManager("test_user")
    session = sm.load_session()

    assert session["user_id"] == "test_user"
    assert "message_history" in session
    assert isinstance(session["message_history"], list)

    # Add a test message
    session["message_history"].append(
        {"user": "Hello", "coach": "Hi there!", "timestamp": "2024-01-01T00:00:00"}
    )

    sm.save_session(session)

    # Load it back
    loaded = sm.load_session()
    assert len(loaded["message_history"]) == 1

    print("✓ Session Manager tests passed")
    return True


def test_cli_initialization():
    """Test CLI initialization."""
    print("\nTesting CLI Initialization...")

    cli = AILifeCoachCLI(user_id="test_user")
    success = cli.initialize()

    assert success is True
    assert cli.coach is not None
    assert cli.current_session is not None

    print("✓ CLI Initialization tests passed")
    return True


def test_message_handling():
    """Test basic message handling."""
    print("\nTesting Message Handling...")

    cli = AILifeCoachCLI(user_id="test_user")
    cli.initialize()

    # Send a simple message
    try:
        response = cli.send_message("Hello, can you introduce yourself?")
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"✓ Message handled successfully. Response length: {len(response)} chars")
        return True
    except Exception as e:
        print(f"✗ Message handling failed: {e}")
        return False


def test_commands():
    """Test CLI commands."""
    print("\nTesting Commands...")

    cli = AILifeCoachCLI(user_id="test_user")
    cli.initialize()

    # Test help command (should not raise exceptions)
    try:
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            cli.show_help()

        output = f.getvalue()
        assert "Available Commands" in output
        print("✓ Help command works correctly")

    except Exception as e:
        print(f"✗ Help command failed: {e}")
        return False

    # Test report generation
    try:
        f = io.StringIO()
        with redirect_stdout(f):
            cli.generate_and_show_report()

        output = f.getvalue()
        assert "Progress Report" in output
        print("✓ Report generation works correctly")

    except Exception as e:
        print(f"✗ Report generation failed: {e}")
        return False

    # Test export report
    try:
        success = cli.export_report(format="markdown")
        assert success is True
        print("✓ Export report works correctly")

    except Exception as e:
        print(f"✗ Export report failed: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Life Coach CLI - Test Suite")
    print("=" * 60)

    tests = [
        test_session_manager,
        test_cli_initialization,
        test_message_handling,
        test_commands,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback

            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)

    if all(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {len(results) - sum(results)} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
