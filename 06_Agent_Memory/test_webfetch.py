"""
Test script for webfetch tool
"""

import sys

sys.path.insert(0, "/home/imjonezz/Desktop/AIE9/06_Agent_Memory/src")

from tools.webfetch import webfetch


def test_webfetch():
    """Test the webfetch tool with various URLs and formats"""

    print("=" * 60)
    print("Testing WebFetch Tool")
    print("=" * 60)

    # Test 1: Fetch markdown from a simple URL
    print("\nTest 1: Fetching example.com in markdown format")
    try:
        result = webfetch("https://example.com", format="markdown", timeout=10)
        print(f"✓ Success! Fetched {len(result)} characters")
        print(f"First 200 chars: {result[:200]}...")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 2: Fetch text from a URL
    print("\nTest 2: Fetching example.com in text format")
    try:
        result = webfetch("https://example.com", format="text", timeout=10)
        print(f"✓ Success! Fetched {len(result)} characters")
        print(f"First 200 chars: {result[:200]}...")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 3: Fetch HTML
    print("\nTest 3: Fetching example.com in HTML format")
    try:
        result = webfetch("https://example.com", format="html", timeout=10)
        print(f"✓ Success! Fetched {len(result)} characters")
        print(f"First 200 chars: {result[:200]}...")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 4: Invalid URL
    print("\nTest 4: Testing invalid URL (should fail)")
    try:
        result = webfetch("not-a-valid-url", format="markdown")
        print(f"✗ Should have failed but got: {result[:100]}...")
    except ValueError as e:
        print(f"✓ Correctly failed with: {e}")
    except Exception as e:
        print(f"? Unexpected error: {e}")

    # Test 5: Timeout exceeding maximum
    print("\nTest 5: Testing timeout validation (should fail)")
    try:
        result = webfetch("https://example.com", format="markdown", timeout=200)
        print(f"✗ Should have failed but got: {result[:100]}...")
    except ValueError as e:
        print(f"✓ Correctly failed with: {e}")
    except Exception as e:
        print(f"? Unexpected error: {e}")

    # Test 6: Fetch from a real news site (searxng-like content)
    print("\nTest 6: News site test")
    try:
        result = webfetch("https://httpbin.org/html", format="text", timeout=10)
        print(f"✓ Success! Fetched {len(result)} characters")
        print(f"First 300 chars:\n{result[:300]}...")
    except Exception as e:
        print(f"✗ Failed: {e}")

    print("\n" + "=" * 60)
    print("WebFetch Tool Testing Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_webfetch()
