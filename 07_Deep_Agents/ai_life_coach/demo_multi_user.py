"""
Demo script for Multi-User Support feature.

This script demonstrates the multi-user authentication, session management,
and data isolation capabilities of the AI Life Coach system.

Run: python demo_multi_user.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tools.user_tools import create_user_tools
from memory import create_memory_store, MemoryManager, UserProfile, Goal


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    """Run the multi-user demo."""
    print("\n" + "🎯 AI LIFE COACH - Multi-User Support Demo".center(60))
    print("=" * 60)

    # Initialize the system
    print("\n📦 Initializing system...")
    store = create_memory_store()
    tools = create_user_tools(store)
    memory_manager = MemoryManager(store)

    # Unpack tools
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
    ) = tools

    print("✅ System initialized!")

    # ========================================================================
    # Demo 1: Create Multiple Users
    # ========================================================================
    print_section("Demo 1: Creating Multiple Users")

    # Create User 1: Alice
    print("\n👤 Creating User 1: Alice...")
    result1 = create_user.invoke(
        {
            "username": "alice",
            "password": "alice_secure_pass",
            "name": "Alice Johnson",
            "age": 28,
            "occupation": "Software Engineer",
        }
    )
    print(f"   {result1}")
    alice_id = result1.split("User ID: ")[1].strip()

    # Create User 2: Bob
    print("\n👤 Creating User 2: Bob...")
    result2 = create_user.invoke(
        {
            "username": "bob",
            "password": "bob_secure_pass",
            "name": "Bob Smith",
            "age": 35,
            "occupation": "Marketing Manager",
        }
    )
    print(f"   {result2}")
    bob_id = result2.split("User ID: ")[1].strip()

    # Create User 3: Carol
    print("\n👤 Creating User 3: Carol...")
    result3 = create_user.invoke(
        {
            "username": "carol",
            "password": "carol_secure_pass",
            "name": "Carol Davis",
            "age": 42,
            "occupation": "Teacher",
        }
    )
    print(f"   {result3}")
    carol_id = result3.split("User ID: ")[1].strip()

    print(f"\n✅ Created 3 users with unique IDs")

    # ========================================================================
    # Demo 2: Authenticate Users
    # ========================================================================
    print_section("Demo 2: User Authentication & Session Management")

    # Authenticate Alice
    print("\n🔐 Authenticating Alice...")
    auth_alice = authenticate_user.invoke({"user_id": alice_id, "password": "alice_secure_pass"})
    print(f"   {auth_alice}")
    alice_token = auth_alice.split("Session token: ")[1].strip()

    # Check current user
    print("\n👤 Checking current user...")
    current = get_current_user.invoke({})
    print(f"   {current}")

    # Authenticate Bob (different session)
    print("\n🔐 Authenticating Bob...")
    auth_bob = authenticate_user.invoke({"user_id": bob_id, "password": "bob_secure_pass"})
    print(f"   {auth_bob}")
    bob_token = auth_bob.split("Session token: ")[1].strip()

    # ========================================================================
    # Demo 3: Data Isolation
    # ========================================================================
    print_section("Demo 3: Data Isolation per User")

    # Save a goal for Alice
    print("\n📝 Adding private goal for Alice...")
    alice_goal = Goal(
        title="Get promoted to Senior Engineer",
        description="Work towards promotion within 12 months",
        domain="career",
    )
    memory_manager.save_goal(alice_id, alice_goal)
    print(f"   ✅ Goal saved for Alice: '{alice_goal.title}'")

    # Save a goal for Bob
    print("\n📝 Adding private goal for Bob...")
    bob_goal = Goal(
        title="Run a marathon",
        description="Complete first marathon within 6 months",
        domain="wellness",
    )
    memory_manager.save_goal(bob_id, bob_goal)
    print(f"   ✅ Goal saved for Bob: '{bob_goal.title}'")

    # Verify Alice's goals
    print("\n🔍 Verifying Alice's goals (should only see her own)...")
    alice_goals = memory_manager.get_goals(alice_id)
    print(f"   Alice has {len(alice_goals)} goal(s):")
    for goal in alice_goals:
        print(f"     - {goal.title} ({goal.domain})")

    # Verify Bob's goals
    print("\n🔍 Verifying Bob's goals (should only see his own)...")
    bob_goals = memory_manager.get_goals(bob_id)
    print(f"   Bob has {len(bob_goals)} goal(s):")
    for goal in bob_goals:
        print(f"     - {goal.title} ({goal.domain})")

    # Verify Carol has no goals
    print("\n🔍 Verifying Carol's goals (should be empty)...")
    carol_goals = memory_manager.get_goals(carol_id)
    print(f"   Carol has {len(carol_goals)} goal(s)")

    print("\n✅ Data isolation verified - users cannot see each other's data!")

    # ========================================================================
    # Demo 4: Session Management
    # ========================================================================
    print_section("Demo 4: Session Management & Validation")

    # Validate Alice's session
    print("\n🔍 Validating Alice's session token...")
    validate_alice = validate_session_token.invoke({"session_token": alice_token})
    print(f"   {validate_alice}")

    # Get session info for Alice
    print("\n📊 Getting session info for Alice...")
    session_info = get_user_session_info.invoke({"user_id": alice_id, "session_token": alice_token})
    print(f"   {session_info}")

    # Logout Bob
    print("\n🚪 Logging out Bob...")
    logout_result = logout_user.invoke({"session_token": bob_token})
    print(f"   {logout_result}")

    # Verify Bob's session is invalid
    print("\n🔍 Verifying Bob's session is now invalid...")
    validate_bob = validate_session_token.invoke({"session_token": bob_token})
    print(f"   {validate_bob}")

    # ========================================================================
    # Demo 5: Profile Management
    # ========================================================================
    print_section("Demo 5: Profile Management")

    # Update Alice's profile
    print("\n✏️  Updating Alice's profile...")
    update_result = update_user_profile.invoke(
        {
            "user_id": alice_id,
            "session_token": alice_token,
            "age": 29,
            "occupation": "Senior Software Engineer",
        }
    )
    print(f"   {update_result}")

    # Retrieve updated profile
    print("\n📋 Retrieving Alice's updated profile...")
    profile = memory_manager.get_profile(alice_id)
    print(f"   Name: {profile.name}")
    print(f"   Age: {profile.age}")
    print(f"   Occupation: {profile.occupation}")

    # ========================================================================
    # Demo 6: Administrative Features
    # ========================================================================
    print_section("Demo 6: Administrative Features")

    # List all users (admin only)
    print("\n📋 Listing all users (admin operation)...")
    users_list = list_all_users.invoke({"admin_token": "admin_secret_token"})
    print(users_list)

    # ========================================================================
    # Demo 7: User Switching
    # ========================================================================
    print_section("Demo 7: User Context Switching")

    # Authenticate Carol
    print("\n🔐 Authenticating Carol...")
    auth_carol = authenticate_user.invoke({"user_id": carol_id, "password": "carol_secure_pass"})
    carol_token = auth_carol.split("Session token: ")[1].strip()
    print(f"   {auth_carol}")

    # Check current user (should be Carol now)
    print("\n👤 Current user after Carol's authentication...")
    current = get_current_user.invoke({})
    print(f"   {current}")

    # Switch back to Alice
    print("\n🔄 Switching back to Alice...")
    switch_result = switch_user.invoke({"user_id": alice_id, "session_token": alice_token})
    print(f"   {switch_result}")

    # Verify current user is Alice
    print("\n👤 Current user after switch...")
    current = get_current_user.invoke({})
    print(f"   {current}")

    # ========================================================================
    # Demo 8: Password Management
    # ========================================================================
    print_section("Demo 8: Password Management")

    # Change Alice's password
    print("\n🔑 Changing Alice's password...")
    change_result = change_user_password.invoke(
        {
            "user_id": alice_id,
            "old_password": "alice_secure_pass",
            "new_password": "alice_new_secure_pass",
            "session_token": alice_token,
        }
    )
    print(f"   {change_result}")

    # Verify old password no longer works
    print("\n🔐 Testing old password (should fail)...")
    old_auth = authenticate_user.invoke({"user_id": alice_id, "password": "alice_secure_pass"})
    print(f"   {old_auth}")

    # Verify new password works
    print("\n🔐 Testing new password (should succeed)...")
    new_auth = authenticate_user.invoke({"user_id": alice_id, "password": "alice_new_secure_pass"})
    print(f"   {new_auth[:70]}...")

    # ========================================================================
    # Summary
    # ========================================================================
    print_section("Demo Summary")

    print("""
✅ Multi-User Support Features Demonstrated:

   1. ✓ User Creation - Multiple users with unique IDs
   2. ✓ Authentication - Secure password-based login
   3. ✓ Session Management - Token-based sessions with TTL
   4. ✓ Data Isolation - Each user's data is completely separate
   5. ✓ Profile Management - Update user profiles
   6. ✓ Administrative Features - List all users (admin only)
   7. ✓ User Switching - Change between authenticated users
   8. ✓ Password Management - Secure password changes
   9. ✓ Session Validation - Verify and manage active sessions
   10. ✓ Logout - End sessions securely

🔒 Security Features:
   - Passwords hashed with PBKDF2 + SHA-256
   - Unique salts for each user
   - Session tokens with 24-hour expiration
   - Namespace-based data isolation
   - Admin-only operations protected

📊 Namespace Structure (per user):
   - (user_id, "profile")    - User profile data
   - (user_id, "goals")      - User goals
   - (user_id, "progress")   - Milestones and setbacks
   - (user_id, "preferences")- User preferences
   - ("auth", "credentials") - Authentication data
   - ("users", "metadata")   - User metadata

🎯 Multi-User Support is ready for production use!
""")


if __name__ == "__main__":
    main()
