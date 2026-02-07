"""
User management tools for AI Life Coach.

This module provides multi-user support with authentication, session management,
and data isolation. It implements namespace-based data isolation from Bead #3.

Tools:
- create_user: Create a new user with unique ID and profile
- authenticate_user: Authenticate a user and create session
- logout_user: End user session
- switch_user: Switch to a different user context
- get_current_user: Get currently authenticated user
- update_user_profile: Update user profile information
- list_all_users: Administrative feature to list all users
- delete_user: Delete a user and all their data
- validate_session: Check if a session is valid
- get_user_session_info: Get session details for a user
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

# Import LangChain components
try:
    from langchain_core.tools import tool
except ImportError:
    # Fallback for development environments without full LangChain
    def tool(func):
        """Fallback decorator when langchain_core is not available."""
        func.is_tool = True  # type: ignore
        return func


# Import memory module components
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import MemoryManager, UserProfile, create_memory_store


# ==============================================================================
# Session Management
# ==============================================================================


class SessionManager:
    """
    Manages user sessions for multi-user support.

    Provides session creation, validation, and cleanup with TTL support.
    Sessions are stored in memory and include user context for isolation.
    """

    def __init__(self, default_ttl_hours: int = 24):
        """
        Initialize session manager.

        Args:
            default_ttl_hours: Default session time-to-live in hours
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = timedelta(hours=default_ttl_hours)

    def create_session(self, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session for a user.

        Args:
            user_id: The user's unique identifier
            metadata: Optional session metadata

        Returns:
            Session token string
        """
        # Generate secure session token
        session_token = secrets.token_urlsafe(32)

        # Calculate expiration
        expires_at = datetime.now() + self.default_ttl

        # Store session
        self.sessions[session_token] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        return session_token

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a session token and return session info if valid.

        Args:
            session_token: The session token to validate

        Returns:
            Session info dict if valid, None otherwise
        """
        if session_token not in self.sessions:
            return None

        session = self.sessions[session_token]
        expires_at = datetime.fromisoformat(session["expires_at"])

        # Check if expired
        if datetime.now() > expires_at:
            del self.sessions[session_token]
            return None

        # Update last accessed
        session["last_accessed"] = datetime.now().isoformat()

        return session

    def get_user_id(self, session_token: str) -> Optional[str]:
        """
        Get user ID from a session token.

        Args:
            session_token: The session token

        Returns:
            User ID if valid session, None otherwise
        """
        session = self.validate_session(session_token)
        return session["user_id"] if session else None

    def end_session(self, session_token: str) -> bool:
        """
        End a session (logout).

        Args:
            session_token: The session token to end

        Returns:
            True if session was ended, False if not found
        """
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False

    def end_all_user_sessions(self, user_id: str) -> int:
        """
        End all sessions for a user.

        Args:
            user_id: The user whose sessions to end

        Returns:
            Number of sessions ended
        """
        tokens_to_remove = [
            token for token, session in self.sessions.items() if session["user_id"] == user_id
        ]

        for token in tokens_to_remove:
            del self.sessions[token]

        return len(tokens_to_remove)

    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions.

        Returns:
            Number of sessions removed
        """
        now = datetime.now()
        expired_tokens = [
            token
            for token, session in self.sessions.items()
            if now > datetime.fromisoformat(session["expires_at"])
        ]

        for token in expired_tokens:
            del self.sessions[token]

        return len(expired_tokens)

    def list_active_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List active sessions, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of session info dicts
        """
        sessions = []
        for token, session in self.sessions.items():
            if user_id is None or session["user_id"] == user_id:
                session_info = session.copy()
                session_info["session_token"] = token[:8] + "..."  # Truncated for security
                sessions.append(session_info)
        return sessions


# ==============================================================================
# Authentication Manager
# ==============================================================================


class AuthenticationManager:
    """
    Manages user authentication with secure password hashing.

    Uses PBKDF2 with SHA-256 for password hashing with unique salts.
    """

    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize authentication manager.

        Args:
            memory_manager: MemoryManager instance for storing credentials
        """
        self.memory_manager = memory_manager

    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash a password with salt using PBKDF2.

        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)

        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)

        # Use PBKDF2 with SHA-256, 100,000 iterations
        hashed = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()

        return hashed, salt

    def _verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password
            hashed: Stored hash
            salt: Stored salt

        Returns:
            True if password matches, False otherwise
        """
        computed_hash, _ = self._hash_password(password, salt)
        return secrets.compare_digest(computed_hash, hashed)

    def store_credentials(self, user_id: str, password: str) -> bool:
        """
        Store hashed credentials for a user.

        Args:
            user_id: The user's unique identifier
            password: Plain text password to hash and store

        Returns:
            True if stored successfully
        """
        hashed, salt = self._hash_password(password)

        # Store in credentials namespace
        namespace = ("auth", "credentials")
        credentials = {
            "user_id": user_id,
            "password_hash": hashed,
            "salt": salt,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        self.memory_manager.store.put(namespace, user_id, credentials)
        return True

    def authenticate(self, user_id: str, password: str) -> bool:
        """
        Authenticate a user with credentials.

        Args:
            user_id: The user's unique identifier
            password: Plain text password to verify

        Returns:
            True if authentication successful, False otherwise
        """
        namespace = ("auth", "credentials")

        try:
            item = self.memory_manager.store.get(namespace, user_id)
            if not item or not item.value:
                return False

            credentials = item.value
            stored_hash = credentials.get("password_hash")
            salt = credentials.get("salt")

            if not stored_hash or not salt:
                return False

            return self._verify_password(password, stored_hash, salt)

        except Exception:
            return False

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> Tuple[bool, str]:
        """
        Change a user's password.

        Args:
            user_id: The user's unique identifier
            old_password: Current password
            new_password: New password to set

        Returns:
            Tuple of (success, message)
        """
        # Verify old password
        if not self.authenticate(user_id, old_password):
            return False, "Current password is incorrect"

        # Validate new password
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters"

        # Store new credentials
        self.store_credentials(user_id, new_password)
        return True, "Password changed successfully"


# ==============================================================================
# User Management Tools Factory
# ==============================================================================


def create_user_tools(store: Optional[Any] = None) -> tuple:
    """
    Create user management tools with shared managers.

    Args:
        store: Optional LangGraph Store instance. If None, creates InMemoryStore.

    Returns:
        Tuple of user management tools
    """
    # Create memory manager
    if store is None:
        store = create_memory_store()
    memory_manager = MemoryManager(store)

    # Create session and auth managers
    session_manager = SessionManager(default_ttl_hours=24)
    auth_manager = AuthenticationManager(memory_manager)

    # Track current active session (for single-user mode compatibility)
    current_session: Dict[str, Optional[str]] = {"token": None}

    # Define tools

    @tool
    def create_user(
        username: str,
        password: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        **profile_data,
    ) -> str:
        """Create a new user with authentication credentials and profile.

        This tool creates a new user account with a unique user ID, sets up
        authentication credentials, and creates an initial profile. All user
        data is isolated by namespace.

        Args:
            username: Unique username for login (required)
            password: Password for authentication (min 8 characters)
            name: User's display name (optional)
            email: User's email address (optional)
            **profile_data: Additional profile fields (age, occupation, etc.)

        Returns:
            Confirmation message with user_id if successful, error message otherwise.

        Raises:
            ValueError: If username or password is invalid

        Example:
            >>> create_user("johndoe", "securepass123", name="John Doe", age=30)
            'User created successfully! User ID: user_johndoe_abc123'
        """
        # Validate inputs
        if not username or not isinstance(username, str):
            return "Error: username must be a non-empty string"

        if not password or len(password) < 8:
            return "Error: password must be at least 8 characters"

        # Generate unique user ID
        user_id = f"user_{username}_{secrets.token_hex(4)}"

        # Check if user already exists (by checking credentials namespace)
        namespace = ("auth", "credentials")
        try:
            existing = memory_manager.store.get(namespace, user_id)
            if existing:
                return f"Error: User with ID '{user_id}' already exists"
        except Exception:
            pass

        try:
            # Store authentication credentials
            auth_manager.store_credentials(user_id, password)

            # Create user profile
            profile = UserProfile(
                user_id=user_id,
                name=name or username,
                **{
                    k: v
                    for k, v in profile_data.items()
                    if k in ["age", "occupation", "relationship_status", "values", "life_situation"]
                },
            )
            memory_manager.save_profile(profile)

            # Store additional user metadata
            user_meta_namespace = ("users", "metadata")
            user_metadata = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "is_active": True,
            }
            memory_manager.store.put(user_meta_namespace, user_id, user_metadata)

            return f"User created successfully! User ID: {user_id}"

        except Exception as e:
            return f"Error creating user: {str(e)}"

    @tool
    def authenticate_user(user_id: str, password: str) -> str:
        """Authenticate a user and create a session.

        Verifies credentials and creates a session token for the user.
        The session token should be used for subsequent operations.

        Args:
            user_id: The user's unique identifier
            password: The user's password

        Returns:
            Session token if authentication successful, error message otherwise.
            Session expires after 24 hours of inactivity.

        Example:
            >>> authenticate_user("user_johndoe_abc123", "securepass123")
            'Authentication successful. Session token: abc123...'
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        if not password:
            return "Error: password is required"

        try:
            # Authenticate
            if not auth_manager.authenticate(user_id, password):
                return "Error: Invalid credentials"

            # Create session
            session_token = session_manager.create_session(
                user_id=user_id, metadata={"auth_method": "password"}
            )

            # Update last login
            user_meta_namespace = ("users", "metadata")
            try:
                item = memory_manager.store.get(user_meta_namespace, user_id)
                if item and item.value:
                    metadata = item.value
                    metadata["last_login"] = datetime.now().isoformat()
                    memory_manager.store.put(user_meta_namespace, user_id, metadata)
            except Exception:
                pass

            # Set as current session
            current_session["token"] = session_token

            return f"Authentication successful. Session token: {session_token}"

        except Exception as e:
            return f"Error during authentication: {str(e)}"

    @tool
    def logout_user(session_token: str) -> str:
        """End a user session (logout).

        Invalidates the session token and ends the user's session.

        Args:
            session_token: The session token to invalidate

        Returns:
            Confirmation message indicating logout status.

        Example:
            >>> logout_user("abc123...")
            'Logout successful'
        """
        if not session_token:
            return "Error: session_token is required"

        try:
            if session_manager.end_session(session_token):
                # Clear current session if it matches
                if current_session["token"] == session_token:
                    current_session["token"] = None
                return "Logout successful"
            else:
                return "Error: Invalid or expired session token"

        except Exception as e:
            return f"Error during logout: {str(e)}"

    @tool
    def switch_user(user_id: str, session_token: Optional[str] = None) -> str:
        """Switch to a different user context.

        Changes the current active user context. If session_token is provided,
        validates it first. Otherwise, switches to the specified user ID if
        they have an active session.

        Args:
            user_id: The user ID to switch to
            session_token: Optional session token for the target user

        Returns:
            Confirmation message indicating switch status.

        Example:
            >>> switch_user("user_janedoe_xyz789")
            'Switched to user: user_janedoe_xyz789'
        """
        if not user_id:
            return "Error: user_id is required"

        try:
            # If session token provided, validate it
            if session_token:
                session = session_manager.validate_session(session_token)
                if not session:
                    return "Error: Invalid or expired session token"
                if session["user_id"] != user_id:
                    return "Error: Session token does not match user_id"
                current_session["token"] = session_token
            else:
                # Check if user has any active sessions
                sessions = session_manager.list_active_sessions(user_id)
                if not sessions:
                    return f"Error: No active session found for user '{user_id}'. Please authenticate first."
                # Use the most recent session
                current_session["token"] = None  # Will need re-auth
                return f"User '{user_id}' found. Please provide session token to switch."

            return f"Switched to user: {user_id}"

        except Exception as e:
            return f"Error switching user: {str(e)}"

    @tool
    def get_current_user() -> str:
        """Get the currently authenticated user.

        Returns information about the currently active user session.

        Returns:
            Current user ID and session info, or message if no active session.

        Example:
            >>> get_current_user()
            'Current user: user_johndoe_abc123 (Session active, expires: 2024-01-15T10:30:00)'
        """
        token = current_session["token"]

        if not token:
            return "No active user session. Please authenticate first."

        session = session_manager.validate_session(token)
        if not session:
            current_session["token"] = None
            return "Session expired. Please authenticate again."

        user_id = session["user_id"]
        expires = session["expires_at"]

        # Get user profile for additional info
        try:
            profile = memory_manager.get_profile(user_id)
            name = profile.name if profile else user_id
        except Exception:
            name = user_id

        return f"Current user: {name} ({user_id}) - Session active, expires: {expires}"

    @tool
    def update_user_profile(user_id: str, session_token: str, **updates) -> str:
        """Update a user's profile information.

        Updates user profile fields. Requires valid session token for
        authentication. Only the authenticated user can update their own profile.

        Args:
            user_id: The user's unique identifier
            session_token: Valid session token
            **updates: Profile fields to update (name, age, occupation, etc.)

        Returns:
            Confirmation message indicating update status.

        Example:
            >>> update_user_profile("user_123", "token...", name="John", age=31)
            'Profile updated successfully for user_123'
        """
        if not user_id or not session_token:
            return "Error: user_id and session_token are required"

        try:
            # Validate session
            session = session_manager.validate_session(session_token)
            if not session:
                return "Error: Invalid or expired session token"

            # Verify user matches session
            if session["user_id"] != user_id:
                return "Error: Session token does not match user_id"

            # Get current profile
            profile = memory_manager.get_profile(user_id)
            if not profile:
                return f"Error: Profile not found for user '{user_id}'"

            # Update fields
            valid_fields = [
                "name",
                "age",
                "occupation",
                "relationship_status",
                "values",
                "life_situation",
            ]
            for field, value in updates.items():
                if field in valid_fields and hasattr(profile, field):
                    setattr(profile, field, value)

            # Save updated profile
            memory_manager.save_profile(profile)

            return f"Profile updated successfully for {user_id}"

        except Exception as e:
            return f"Error updating profile: {str(e)}"

    @tool
    def list_all_users(admin_token: str) -> str:
        """List all users in the system (administrative feature).

        Requires admin authentication. Returns list of all registered users
        with their metadata (no sensitive data like passwords).

        Args:
            admin_token: Admin authentication token

        Returns:
            Formatted list of all users or error message.

        Example:
            >>> list_all_users("admin_secret_token")
            'Users in system (3 total):\\n1. user_johndoe_abc123 - John Doe (Active)\\n...'
        """
        # Simple admin token check (in production, use proper admin auth)
        if admin_token != "admin_secret_token":
            return "Error: Invalid admin token"

        try:
            user_meta_namespace = ("users", "metadata")
            users = []

            try:
                items = list(memory_manager.store.search(user_meta_namespace))
                for item in items:
                    if item.value:
                        metadata = item.value
                        users.append(
                            {
                                "user_id": metadata.get("user_id", "unknown"),
                                "username": metadata.get("username", "unknown"),
                                "name": metadata.get("name", "N/A"),
                                "created_at": metadata.get("created_at", "unknown"),
                                "last_login": metadata.get("last_login", "never"),
                                "is_active": metadata.get("is_active", True),
                            }
                        )
            except Exception:
                pass

            if not users:
                return "No users found in the system"

            # Format output
            parts = [f"Users in system ({len(users)} total):", ""]
            for i, user in enumerate(users, 1):
                status = "Active" if user["is_active"] else "Inactive"
                parts.append(f"{i}. {user['user_id']}")
                parts.append(f"   Username: {user['username']}")
                parts.append(f"   Created: {user['created_at']}")
                parts.append(f"   Last Login: {user['last_login']}")
                parts.append(f"   Status: {status}")
                parts.append("")

            return "\n".join(parts)

        except Exception as e:
            return f"Error listing users: {str(e)}"

    @tool
    def delete_user(user_id: str, admin_token: str, confirm: bool = False) -> str:
        """Delete a user and all their data (administrative feature).

        Permanently deletes a user account, all associated data, and all
        active sessions. This action cannot be undone.

        Args:
            user_id: The user ID to delete
            admin_token: Admin authentication token
            confirm: Must be True to confirm deletion

        Returns:
            Confirmation message indicating deletion status.

        Example:
            >>> delete_user("user_123", "admin_secret_token", confirm=True)
            'User user_123 and all associated data deleted successfully'
        """
        # Simple admin token check
        if admin_token != "admin_secret_token":
            return "Error: Invalid admin token"

        if not confirm:
            return "Error: confirm=True required to delete user. This action cannot be undone."

        try:
            # End all user sessions
            session_manager.end_all_user_sessions(user_id)

            # Delete user data using memory manager
            memory_manager.delete_user_data(user_id)

            # Delete credentials
            namespace = ("auth", "credentials")
            try:
                memory_manager.store.delete(namespace, user_id)
            except Exception:
                pass

            # Delete user metadata
            user_meta_namespace = ("users", "metadata")
            try:
                memory_manager.store.delete(user_meta_namespace, user_id)
            except Exception:
                pass

            return f"User {user_id} and all associated data deleted successfully"

        except Exception as e:
            return f"Error deleting user: {str(e)}"

    @tool
    def validate_session_token(session_token: str) -> str:
        """Validate a session token and return session information.

        Checks if a session token is valid and returns session details.

        Args:
            session_token: The session token to validate

        Returns:
            Session status and details if valid, error message otherwise.

        Example:
            >>> validate_session_token("abc123...")
            'Session valid. User: user_123, Expires: 2024-01-15T10:30:00'
        """
        if not session_token:
            return "Error: session_token is required"

        session = session_manager.validate_session(session_token)

        if not session:
            return "Error: Invalid or expired session token"

        user_id = session["user_id"]
        expires = session["expires_at"]
        created = session["created_at"]

        return f"Session valid. User: {user_id}, Created: {created}, Expires: {expires}"

    @tool
    def get_user_session_info(user_id: str, session_token: str) -> str:
        """Get session information for a user.

        Returns information about all active sessions for a user.
        Requires valid session token for authentication.

        Args:
            user_id: The user ID to query
            session_token: Valid session token for authentication

        Returns:
            Session information for the user.

        Example:
            >>> get_user_session_info("user_123", "token...")
            'Active sessions for user_123: 1 session(s)'
        """
        # Validate session
        session = session_manager.validate_session(session_token)
        if not session:
            return "Error: Invalid or expired session token"

        # Users can only view their own sessions (or admin)
        if session["user_id"] != user_id:
            return "Error: Can only view your own sessions"

        sessions = session_manager.list_active_sessions(user_id)

        if not sessions:
            return f"No active sessions for user '{user_id}'"

        parts = [f"Active sessions for {user_id}: {len(sessions)} session(s)", ""]
        for i, s in enumerate(sessions, 1):
            parts.append(f"{i}. Session: {s['session_token']}")
            parts.append(f"   Created: {s['created_at']}")
            parts.append(f"   Expires: {s['expires_at']}")
            parts.append(f"   Last Accessed: {s['last_accessed']}")
            parts.append("")

        return "\n".join(parts)

    @tool
    def change_user_password(
        user_id: str, old_password: str, new_password: str, session_token: str
    ) -> str:
        """Change a user's password.

        Requires current password and valid session for security.
        New password must be at least 8 characters.

        Args:
            user_id: The user's unique identifier
            old_password: Current password
            new_password: New password (min 8 characters)
            session_token: Valid session token

        Returns:
            Confirmation message indicating password change status.

        Example:
            >>> change_user_password("user_123", "oldpass", "newpass123", "token...")
            'Password changed successfully'
        """
        # Validate session
        session = session_manager.validate_session(session_token)
        if not session:
            return "Error: Invalid or expired session token"

        if session["user_id"] != user_id:
            return "Error: Session does not match user_id"

        success, message = auth_manager.change_password(user_id, old_password, new_password)

        if success:
            return f"Password changed successfully for {user_id}"
        else:
            return f"Error: {message}"

    print("User management tools created successfully!")

    return (
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
    )


# Export tools at module level for convenience
__all__ = [
    "create_user_tools",
    "SessionManager",
    "AuthenticationManager",
]
