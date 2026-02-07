#!/usr/bin/env python3
"""
Minimal Performance Test

Just test basic imports and initialization to identify bottlenecks.
"""

import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test import performance."""
    print("🔍 Testing import performance...")

    start_time = time.perf_counter()

    try:
        print("  Importing config...")
        from src.config import config

        config_time = time.perf_counter() - start_time
        print(f"  ✅ Config imported in {config_time:.3f}s")

        print("  Initializing environment...")
        init_start = time.perf_counter()
        config.initialize_environment()
        env_time = time.perf_counter() - init_start
        print(f"  ✅ Environment initialized in {env_time:.3f}s")

        print("  Importing main...")
        main_start = time.perf_counter()
        from src.main import create_life_coach

        main_time = time.perf_counter() - main_start
        print(f"  ✅ Main imported in {main_time:.3f}s")

        total_time = time.perf_counter() - start_time
        print(f"✅ All imports completed in {total_time:.3f}s")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_minimal_creation():
    """Test minimal coach creation."""
    print("\n🔍 Testing coach creation...")

    start_time = time.perf_counter()

    try:
        print("  Creating coach...")
        from src.main import create_life_coach

        coach = create_life_coach()
        create_time = time.perf_counter() - start_time
        print(f"✅ Coach created in {create_time:.3f}s")

        return coach, create_time

    except Exception as e:
        print(f"❌ Coach creation failed: {e}")
        import traceback

        traceback.print_exc()
        return None, 0


def main():
    """Run minimal performance test."""
    print("🚀 Minimal Performance Test")
    print("=" * 40)

    # Test imports
    if not test_imports():
        print("❌ Cannot continue due to import failures")
        return

    # Test coach creation
    coach, create_time = test_minimal_creation()

    if coach:
        print(f"\n📊 RESULTS:")
        print(f"  Coach Creation Time: {create_time:.3f}s")
        print(f"  Target (<5s): {'✅ PASS' if create_time < 5 else '❌ FAIL'}")
    else:
        print("❌ Coach creation failed")


if __name__ == "__main__":
    main()
