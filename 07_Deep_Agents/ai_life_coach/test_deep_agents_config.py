"""
Test script for Deep Agents infrastructure configuration.

This script verifies:
1. Environment variables are properly set
2. FilesystemBackend is configured for workspace directory
3. Model initialization with local LLM endpoint works
4. Basic agent creation and invocation succeeds
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

# Import configuration
from src.config import config, get_backend


def test_environment_setup():
    """Test that environment variables are properly configured."""
    print("=" * 60)
    print("TEST 1: Environment Setup")
    print("=" * 60)

    # Initialize environment
    config.initialize_environment()

    # Check local endpoint configuration
    if not config.model.use_local_endpoint:
        print("⚠️  WARNING: Not using local endpoint")
    else:
        print(f"✓ Local endpoint enabled")
        print(f"  - Endpoint: {config.model.local_endpoint}")
        print(f"  - Model: {config.model.local_model}")

    # Check environment variables
    import os

    openai_base = os.environ.get("OPENAI_API_BASE", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")

    if not openai_base:
        print("✗ ERROR: OPENAI_API_BASE not set")
        return False
    else:
        print(f"✓ OPENAI_API_BASE: {openai_base}")

    if openai_key != "not-needed" and not openai_key:
        print("✗ ERROR: OPENAI_API_KEY not set")
        return False
    else:
        print(
            f"✓ OPENAI_API_KEY: {openai_key[:10]}..."
            if len(openai_key) > 10
            else f"✓ OPENAI_API_KEY: {openai_key}"
        )

    print("\n✓ Environment setup test passed!\n")
    return True


def test_backend_configuration():
    """Test that FilesystemBackend is properly configured."""
    print("=" * 60)
    print("TEST 2: FilesystemBackend Configuration")
    print("=" * 60)

    try:
        backend = get_backend()
        print(f"✓ Backend type: {type(backend).__name__}")
        print(f"  - Module: {type(backend).__module__}")

        # Check workspace directory
        workspace_dir = config.memory.workspace_dir
        print(f"✓ Workspace directory: {workspace_dir}")
        print(f"  - Exists: {workspace_dir.exists()}")

        # Check subdirectories
        subdirs = ["user_profile", "assessments", "plans", "progress", "resources"]
        for subdir in subdirs:
            dir_path = workspace_dir / subdir
            exists = dir_path.exists()
            status = "✓" if exists else "⚠️"
            print(f"{status}  - {subdir}: {exists}")

        print("\n✓ Backend configuration test passed!\n")
        return True
    except Exception as e:
        print(f"✗ ERROR: Backend configuration failed: {e}")
        return False


def test_model_initialization():
    """Test that model can be initialized with local endpoint."""
    print("=" * 60)
    print("TEST 3: Model Initialization")
    print("=" * 60)

    try:
        # Get model config
        model_config = config.model.get_model_config()
        print(f"✓ Model config: {model_config}")

        # Initialize model
        model = init_chat_model(model_config)
        print(f"✓ Model initialized: {type(model).__name__}")
        print(f"  - Provider module: {type(model).__module__}")

        # Test simple invocation
        print("\nTesting model invocation...")
        response = model.invoke("Say 'Hello!' in exactly those words.")
        print(f"  Response: {response.content[:100]}...")

        if "Hello!" in response.content:
            print("\n✓ Model initialization test passed!\n")
            return True
        else:
            print("\n⚠️  WARNING: Unexpected model response\n")
            return False

    except Exception as e:
        print(f"\n✗ ERROR: Model initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_agent_creation():
    """Test that a basic Deep Agent can be created."""
    print("=" * 60)
    print("TEST 4: Basic Deep Agent Creation")
    print("=" * 60)

    try:
        # Initialize model
        model_config = config.model.get_model_config()
        model = init_chat_model(model_config)

        # Get backend
        backend = get_backend()

        # Create a simple test agent
        print("Creating test agent...")
        test_agent = create_deep_agent(
            model=model,
            backend=backend,
            system_prompt="""You are a helpful test assistant.

Your role is to verify that the Deep Agents infrastructure is working correctly.
Keep responses brief and friendly.""",
        )

        print(f"✓ Agent created: {type(test_agent).__name__}")

        # Test invocation
        print("\nTesting agent invocation...")
        result = test_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Say 'Deep Agents infrastructure is working!' in exactly those words.",
                    }
                ]
            }
        )

        response = result["messages"][-1].content
        print(f"  Response: {response[:100]}...")

        if "Deep Agents infrastructure is working!" in response:
            print("\n✓ Agent creation test passed!\n")
            return True
        else:
            print(f"\n⚠️  WARNING: Unexpected agent response\n")
            return False

    except Exception as e:
        print(f"\n✗ ERROR: Agent creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_file_operations():
    """Test that file operations work through the backend."""
    print("=" * 60)
    print("TEST 5: File Operations")
    print("=" * 60)

    try:
        # Initialize model and create agent
        model_config = config.model.get_model_config()
        model = init_chat_model(model_config)
        backend = get_backend()

        test_agent = create_deep_agent(
            model=model,
            backend=backend,
            system_prompt="""You are a file operations test assistant.

When asked to write files, use the write_file tool.
Keep responses brief.""",
        )

        # Test file writing
        print("Testing file write operation...")
        result = test_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": 'Write a file called test.txt with the content: "This is a test of Deep Agents file operations."',
                    }
                ]
            }
        )

        print(f"  Agent response: {result['messages'][-1].content[:150]}...")

        # Check if file was created
        test_file = config.memory.workspace_dir / "test.txt"
        if test_file.exists():
            print(f"✓ File created: {test_file}")
            content = test_file.read_text()
            print(f"  Content: {content[:50]}...")

            # Clean up
            test_file.unlink()
            print(f"✓ Test file cleaned up")

            print("\n✓ File operations test passed!\n")
            return True
        else:
            print(f"⚠️  WARNING: File was not created at {test_file}\n")
            return False

    except Exception as e:
        print(f"\n✗ ERROR: File operations test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Deep Agents Infrastructure Test Suite" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    results = {
        "Environment Setup": test_environment_setup(),
        "Backend Configuration": test_backend_configuration(),
        "Model Initialization": test_model_initialization(),
        "Agent Creation": test_agent_creation(),
        "File Operations": test_file_operations(),
    }

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 All tests passed! Deep Agents infrastructure is ready.\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
