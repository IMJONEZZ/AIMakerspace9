"""
Test dashboard can load and display statistics.
This runs the dashboard in a non-interactive mode to verify core functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dashboard import MemoryDashboard


def test_dashboard_load():
    """Test that dashboard can initialize and show stats."""
    print("=== Dashboard Load Test ===")

    try:
        # Initialize dashboard
        print("\n[1/3] Initializing dashboard...")
        dash = MemoryDashboard()

        # Try to show system stats
        print("[2/3] Retrieving system statistics...")
        dash.show_system_stats()

        # Try to list profiles
        print("\n[3/3] Listing user profiles...")
        dash.list_user_profiles()

        # Print success message
        print("\n✓ Dashboard loaded and displayed statistics successfully!")
        return True

    except Exception as e:
        print(f"\n✗ Dashboard test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_dashboard_load()
    sys.exit(0 if success else 1)
