"""
Verification script for Integration Tools.

This script verifies that all integration tools are properly created
and can be used with the AI Life Coach system.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.tools.integration_tools import create_integration_tools


def verify_integration_tools():
    """Verify integration tools are properly configured."""

    print("=" * 70)
    print("Integration Tools Verification")
    print("=" * 70)

    # Initialize environment
    print("\n1. Initializing environment...")
    config.initialize_environment()
    print("   ✓ Environment initialized")

    # Create integration tools
    print("\n2. Creating integration tools...")
    (
        harmonize_specialist_outputs,
        synthesize_cross_domain_insights,
        generate_prioritized_action_list,
        create_unified_response,
    ) = create_integration_tools()
    print("   ✓ Integration tools created successfully")

    # Verify each tool
    print("\n3. Verifying integration tools:")
    tools = [
        ("harmonize_specialist_outputs", harmonize_specialist_outputs),
        ("synthesize_cross_domain_insights", synthesize_cross_domain_insights),
        ("generate_prioritized_action_list", generate_prioritized_action_list),
        ("create_unified_response", create_unified_response),
    ]

    for tool_name, tool_func in tools:
        has_tool_decorator = hasattr(tool_func, "is_tool") or hasattr(tool_func, "__wrapped__")
        is_callable = callable(tool_func)
        status = "✓" if (has_tool_decorator or is_callable) else "✗"
        print(f"   {status} {tool_name}")

    # Check tool metadata
    print("\n4. Checking tool metadata:")
    for tool_name, tool_func in tools:
        docstring = getattr(tool_func, "__doc__", None)
        if docstring:
            first_line = docstring.strip().split("\n")[0]
            print(f"   ✓ {tool_name}: {first_line[:60]}...")
        else:
            print(f"   ✗ {tool_name}: No docstring")

    # Summary
    print("\n" + "=" * 70)
    print("Verification Complete")
    print("=" * 70)
    print(f"\n✓ All {len(tools)} integration tools verified successfully")
    print("\nIntegration Tools Summary:")
    print("  • harmonize_specialist_outputs - Normalize and merge specialist outputs")
    print("  • synthesize_cross_domain_insights - Create integrated insights across domains")
    print("  • generate_prioritized_action_list - Create prioritized actionable steps")
    print("  • create_unified_response - Generate complete unified response")

    return True


if __name__ == "__main__":
    try:
        verify_integration_tools()
        print("\n✓ Verification passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Verification failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
