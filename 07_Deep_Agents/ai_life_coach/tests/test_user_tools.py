"""
Comprehensive test suite for user management tools.

Tests multi-user authentication, session management, data isolation,
and administrative features.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.user_tools import (
    create_user_tools,
    SessionManager,
    AuthenticationManager,
)
from memory import create_memory_store, MemoryManager


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def memory_store():
    """Create a fresh memory store for each test."""
    return create_memory_store()


@pytest.fixture
def user_tools(memory_store):
    """Create user tools with memory store."""
    return create_user_tools(memory_store)


@pytest.fixture
def session_manager():
    """Create a session manager."""
    return SessionManager(default_ttl_hours=24)


@pytest.fixture
def auth_manager(memory_store):
    """Create an auth manager."""
    memory_manager = MemoryManager(memory_store)
    return AuthenticationManager(memory_manager)


# Helper to invoke tools
def invoke_tool(tool, **kwargs):
    """Helper to invoke a LangChain tool."""
    return tool.invoke(kwargs)


# ==============================================================================
# Session Manager Tests
# ==============================================================================


class TestSessionManager:
    """Test session management functionality."""

    def test_create_session(self, session_manager):
        """Test creating a new session."""
        token = session_manager.create_session("user_123")

        assert token is not None
        assert len(token) > 0
        # Sessions are stored by token, not by user_id
        assert token in session_manager.sessions
        assert session_manager.sessions[token]["user_id"] == "user_123"

    def test_validate_valid_session(self, session_manager):
        """Test validating a valid session."""
        token = session_manager.create_session("user_123")
        session = session_manager.validate_session(token)

        assert session is not None
        assert session["user_id"] == "user_123"
        assert "expires_at" in session

    def test_validate_invalid_session(self, session_manager):
        """Test validating an invalid session."""
        session = session_manager.validate_session("invalid_token")
        assert session is None

    def test_session_expiration(self, session_manager):
        """Test that expired sessions are rejected."""
        # Create session with very short TTL
        manager = SessionManager(default_ttl_hours=-1)  # Already expired
        token = manager.create_session("user_123")

        # Should be invalid/expired
        session = manager.validate_session(token)
        assert session is None

    def test_end_session(self, session_manager):
        """Test ending a session."""
        token = session_manager.create_session("user_123")

        # End the session
        result = session_manager.end_session(token)
        assert result is True

        # Should no longer be valid
        session = session_manager.validate_session(token)
        assert session is None

    def test_end_nonexistent_session(self, session_manager):
        """Test ending a non-existent session."""
        result = session_manager.end_session("nonexistent_token")
        assert result is False

    def test_end_all_user_sessions(self, session_manager):
        """Test ending all sessions for a user."""
        # Create multiple sessions
        token1 = session_manager.create_session("user_123")
        token2 = session_manager.create_session("user_123")
        token3 = session_manager.create_session("user_456")

        # End all for user_123
        count = session_manager.end_all_user_sessions("user_123")
        assert count == 2

        # Verify user_123 sessions are gone
        assert session_manager.validate_session(token1) is None
        assert session_manager.validate_session(token2) is None

        # Verify user_456 session still exists
        assert session_manager.validate_session(token3) is not None

    def test_cleanup_expired_sessions(self, session_manager):
        """Test cleaning up expired sessions."""
        # Create an expired session manually
        from datetime import datetime, timedelta

        token = "expired_token"
        session_manager.sessions[token] = {
            "user_id": "user_123",
            "created_at": (datetime.now() - timedelta(hours=48)).isoformat(),
            "expires_at": (datetime.now() - timedelta(hours=24)).isoformat(),
            "last_accessed": (datetime.now() - timedelta(hours=48)).isoformat(),
            "metadata": {},
        }

        # Create valid session
        valid_token = session_manager.create_session("user_456")

        # Cleanup
        count = session_manager.cleanup_expired_sessions()
        assert count == 1
        assert token not in session_manager.sessions
        assert valid_token in session_manager.sessions

    def test_list_active_sessions(self, session_manager):
        """Test listing active sessions."""
        session_manager.create_session("user_123")
        session_manager.create_session("user_123")
        session_manager.create_session("user_456")

        # List all sessions
        all_sessions = session_manager.list_active_sessions()
        assert len(all_sessions) == 3

        # List for specific user
        user_sessions = session_manager.list_active_sessions("user_123")
        assert len(user_sessions) == 2


# ==============================================================================
# Authentication Manager Tests
# ==============================================================================


class TestAuthenticationManager:
    """Test authentication functionality."""

    def test_store_and_authenticate(self, auth_manager):
        """Test storing credentials and authenticating."""
        # Store credentials
        auth_manager.store_credentials("user_123", "password123")

        # Authenticate with correct password
        assert auth_manager.authenticate("user_123", "password123") is True

        # Authenticate with wrong password
        assert auth_manager.authenticate("user_123", "wrongpassword") is False

    def test_authenticate_nonexistent_user(self, auth_manager):
        """Test authenticating a non-existent user."""
        assert auth_manager.authenticate("nonexistent", "password") is False

    def test_password_hashing(self, auth_manager):
        """Test that passwords are properly hashed."""
        # Store credentials
        auth_manager.store_credentials("user_123", "mypassword")

        # Retrieve stored credentials
        namespace = ("auth", "credentials")
        item = auth_manager.memory_manager.store.get(namespace, "user_123")

        assert item is not None
        assert item.value["password_hash"] != "mypassword"  # Should be hashed
        assert "salt" in item.value

    def test_change_password_success(self, auth_manager):
        """Test successful password change."""
        auth_manager.store_credentials("user_123", "oldpassword")

        success, message = auth_manager.change_password("user_123", "oldpassword", "newpassword123")

        assert success is True
        assert "successfully" in message

        # Verify new password works
        assert auth_manager.authenticate("user_123", "newpassword123") is True
        assert auth_manager.authenticate("user_123", "oldpassword") is False

    def test_change_password_wrong_old(self, auth_manager):
        """Test password change with wrong old password."""
        auth_manager.store_credentials("user_123", "oldpassword")

        success, message = auth_manager.change_password(
            "user_123", "wrongpassword", "newpassword123"
        )

        assert success is False
        assert "incorrect" in message.lower()

    def test_change_password_too_short(self, auth_manager):
        """Test password change with too short new password."""
        auth_manager.store_credentials("user_123", "oldpassword")

        success, message = auth_manager.change_password("user_123", "oldpassword", "short")

        assert success is False
        assert "8 characters" in message


# ==============================================================================
# User Tools Tests
# ==============================================================================


class TestUserTools:
    """Test user management tools."""

    def test_create_user_success(self, user_tools):
        """Test successful user creation."""
        create_user = user_tools[0]

        result = invoke_tool(
            create_user, username="testuser", password="securepass123", name="Test User", age=30
        )

        assert "successfully" in result
        assert "User ID:" in result
        assert "user_testuser_" in result

    def test_create_user_invalid_username(self, user_tools):
        """Test user creation with invalid username."""
        create_user = user_tools[0]

        result = invoke_tool(create_user, username="", password="securepass123")

        assert "Error" in result
        assert "username" in result.lower()

    def test_create_user_short_password(self, user_tools):
        """Test user creation with short password."""
        create_user = user_tools[0]

        result = invoke_tool(create_user, username="testuser", password="short")

        assert "Error" in result
        assert "8 characters" in result

    def test_authenticate_user_success(self, user_tools):
        """Test successful authentication."""
        create_user, authenticate_user = user_tools[0], user_tools[1]

        # Create user
        create_result = invoke_tool(create_user, username="authuser", password="securepass123")

        # Extract user_id from result
        user_id = create_result.split("User ID: ")[1].strip()

        # Authenticate
        auth_result = invoke_tool(authenticate_user, user_id=user_id, password="securepass123")

        assert "successful" in auth_result
        assert "Session token:" in auth_result

    def test_authenticate_user_wrong_password(self, user_tools):
        """Test authentication with wrong password."""
        create_user, authenticate_user = user_tools[0], user_tools[1]

        # Create user
        create_result = invoke_tool(create_user, username="authuser2", password="securepass123")
        user_id = create_result.split("User ID: ")[1].strip()

        # Authenticate with wrong password
        auth_result = invoke_tool(authenticate_user, user_id=user_id, password="wrongpassword")

        assert "Error" in auth_result
        assert "Invalid" in auth_result

    def test_logout_user(self, user_tools):
        """Test user logout."""
        create_user, authenticate_user, logout_user = user_tools[0], user_tools[1], user_tools[2]

        # Create and authenticate user
        create_result = invoke_tool(create_user, username="logoutuser", password="securepass123")
        user_id = create_result.split("User ID: ")[1].strip()
        auth_result = invoke_tool(authenticate_user, user_id=user_id, password="securepass123")

        # Extract session token
        token = auth_result.split("Session token: ")[1].strip()

        # Logout
        logout_result = invoke_tool(logout_user, session_token=token)

        assert "successful" in logout_result

    def test_get_current_user_no_session(self, user_tools):
        """Test getting current user with no active session."""
        get_current_user = user_tools[4]

        result = invoke_tool(get_current_user)

        assert "No active user session" in result

    def test_update_user_profile(self, user_tools):
        """Test updating user profile."""
        create_user, authenticate_user, _, _, _, update_user_profile = (
            user_tools[0],
            user_tools[1],
            user_tools[2],
            user_tools[3],
            user_tools[4],
            user_tools[5],
        )

        # Create and authenticate user
        create_result = invoke_tool(
            create_user, username="profileuser", password="securepass123", name="Original Name"
        )
        user_id = create_result.split("User ID: ")[1].strip()
        auth_result = invoke_tool(authenticate_user, user_id=user_id, password="securepass123")
        token = auth_result.split("Session token: ")[1].strip()

        # Update profile
        update_result = invoke_tool(
            update_user_profile, user_id=user_id, session_token=token, name="New Name", age=25
        )

        assert "successfully" in update_result

    def test_validate_session_token(self, user_tools):
        """Test session token validation."""
        create_user, authenticate_user, _, _, _, _, _, _, validate_session_token = (
            user_tools[0],
            user_tools[1],
            user_tools[2],
            user_tools[3],
            user_tools[4],
            user_tools[5],
            user_tools[6],
            user_tools[7],
            user_tools[8],
        )

        # Create and authenticate user
        create_result = invoke_tool(create_user, username="sessionuser", password="securepass123")
        user_id = create_result.split("User ID: ")[1].strip()
        auth_result = invoke_tool(authenticate_user, user_id=user_id, password="securepass123")
        token = auth_result.split("Session token: ")[1].strip()

        # Validate
        validate_result = invoke_tool(validate_session_token, session_token=token)

        assert "valid" in validate_result.lower()
        assert user_id in validate_result

    def test_validate_invalid_token(self, user_tools):
        """Test validation of invalid token."""
        validate_session_token = user_tools[8]

        result = invoke_tool(validate_session_token, session_token="invalid_token")

        assert "Error" in result or "Invalid" in result

    def test_list_all_users_admin_only(self, user_tools):
        """Test that listing users requires admin token."""
        list_all_users = user_tools[6]

        # Try without admin token
        result = invoke_tool(list_all_users, admin_token="wrong_token")
        assert "Error" in result or "Invalid" in result

        # Try with admin token
        result = invoke_tool(list_all_users, admin_token="admin_secret_token")
        # Should succeed (may be empty list or list of users)
        assert "Error" not in result or "Users in system" in result

    def test_delete_user_requires_confirmation(self, user_tools):
        """Test that deleting user requires confirmation."""
        delete_user = user_tools[7]

        result = invoke_tool(
            delete_user, user_id="user_123", admin_token="admin_secret_token", confirm=False
        )

        assert "confirm=True required" in result

    def test_change_password(self, user_tools):
        """Test changing user password."""
        create_user, authenticate_user, _, _, _, _, _, _, _, _, change_user_password = user_tools

        # Create and authenticate user
        create_result = invoke_tool(create_user, username="passuser", password="oldpassword123")
        user_id = create_result.split("User ID: ")[1].strip()
        auth_result = invoke_tool(authenticate_user, user_id=user_id, password="oldpassword123")
        token = auth_result.split("Session token: ")[1].strip()

        # Change password
        change_result = invoke_tool(
            change_user_password,
            user_id=user_id,
            old_password="oldpassword123",
            new_password="newpassword456",
            session_token=token,
        )

        assert "successfully" in change_result.lower()

        # Verify new password works
        new_auth = invoke_tool(authenticate_user, user_id=user_id, password="newpassword456")
        assert "successful" in new_auth


# ==============================================================================
# Data Isolation Tests
# ==============================================================================


class TestDataIsolation:
    """Test that user data is properly isolated."""

    def test_user_data_isolation(self, user_tools, memory_store):
        """Test that users cannot access each other's data."""
        from memory import MemoryManager

        create_user, authenticate_user = user_tools[0], user_tools[1]
        memory_manager = MemoryManager(memory_store)

        # Create two users
        result1 = invoke_tool(
            create_user, username="user1", password="password123", name="User One"
        )
        user_id_1 = result1.split("User ID: ")[1].strip()

        result2 = invoke_tool(
            create_user, username="user2", password="password123", name="User Two"
        )
        user_id_2 = result2.split("User ID: ")[1].strip()

        # Save data for user 1
        from memory import Goal

        goal = Goal(title="User 1 Goal", description="Private to user 1")
        memory_manager.save_goal(user_id_1, goal)

        # Verify goals are in correct namespace
        goals_for_user1 = memory_manager.get_goals(user_id_1)
        assert len(goals_for_user1) == 1
        assert goals_for_user1[0].title == "User 1 Goal"

        goals_for_user2 = memory_manager.get_goals(user_id_2)
        assert len(goals_for_user2) == 0  # User 2 has no goals

    def test_namespace_structure(self, memory_store):
        """Test that namespaces are correctly structured per user."""
        from memory import (
            get_profile_namespace,
            get_goals_namespace,
            get_progress_namespace,
            get_preferences_namespace,
        )

        user_id = "test_user_123"

        # Verify namespace structure
        assert get_profile_namespace(user_id) == (user_id, "profile")
        assert get_goals_namespace(user_id) == (user_id, "goals")
        assert get_progress_namespace(user_id) == (user_id, "progress")
        assert get_preferences_namespace(user_id) == (user_id, "preferences")

    def test_session_isolation(self, session_manager):
        """Test that sessions are isolated between users."""
        # Create sessions for different users
        token1 = session_manager.create_session("user_1")
        token2 = session_manager.create_session("user_2")

        # Verify sessions return correct user IDs
        session1 = session_manager.validate_session(token1)
        session2 = session_manager.validate_session(token2)

        assert session1["user_id"] == "user_1"
        assert session2["user_id"] == "user_2"

        # End one session, verify other still valid
        session_manager.end_session(token1)
        assert session_manager.validate_session(token1) is None
        assert session_manager.validate_session(token2) is not None


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestUserWorkflow:
    """Test complete user workflows."""

    def test_complete_user_lifecycle(self, user_tools):
        """Test the complete lifecycle: create, auth, use, logout."""
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
        ) = user_tools

        # 1. Create user
        create_result = invoke_tool(
            create_user,
            username="lifecycleuser",
            password="securepass123",
            name="Lifecycle User",
            age=30,
        )
        assert "successfully" in create_result
        user_id = create_result.split("User ID: ")[1].strip()

        # 2. Authenticate
        auth_result = invoke_tool(authenticate_user, user_id=user_id, password="securepass123")
        assert "successful" in auth_result
        token = auth_result.split("Session token: ")[1].strip()

        # 3. Check current user
        current = invoke_tool(get_current_user)
        assert "Lifecycle User" in current
        assert user_id in current

        # 4. Update profile
        update_result = invoke_tool(
            update_user_profile, user_id=user_id, session_token=token, age=31
        )
        assert "successfully" in update_result

        # 5. Validate session
        validate_result = invoke_tool(validate_session_token, session_token=token)
        assert "valid" in validate_result.lower()

        # 6. Get session info
        session_info = invoke_tool(get_user_session_info, user_id=user_id, session_token=token)
        assert "Active sessions" in session_info

        # 7. Logout
        logout_result = invoke_tool(logout_user, session_token=token)
        assert "successful" in logout_result

        # 8. Verify session invalid
        validate_after = invoke_tool(validate_session_token, session_token=token)
        assert "Invalid" in validate_after or "Error" in validate_after


# ==============================================================================
# Run Tests
# ==============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
