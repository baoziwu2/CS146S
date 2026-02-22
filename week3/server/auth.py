"""OAuth2 authentication for Gmail API.

Runtime authentication module that loads refresh_token from .token.json
and refreshes access_token. Does NOT initiate browser authorization flow.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Default paths (relative to project root)
DEFAULT_CREDENTIALS_PATH = "credentials.json"
DEFAULT_TOKEN_PATH = ".token.json"


def _get_project_root() -> Path:
    """Get the project root directory (week3/).

    This function finds the project root using multiple strategies:
    1. Environment variable GMAIL_PROJECT_ROOT (highest priority)
    2. Current working directory if it contains server/ and credentials.json or .token.json
    3. Script file location (server/auth.py -> server/ -> week3/)

    Returns:
        Path to project root directory
    """
    # Strategy 1: Check environment variable
    env_root = os.getenv("GMAIL_PROJECT_ROOT")
    if env_root:
        root_path = Path(env_root).resolve()
        if root_path.exists() and root_path.is_dir():
            return root_path

    # Strategy 2: Check current working directory
    cwd = Path.cwd()
    server_dir = cwd / "server"
    has_credentials = (cwd / "credentials.json").exists() or (cwd / ".token.json").exists()
    if server_dir.exists() and server_dir.is_dir() and has_credentials:
        return cwd

    # Strategy 3: Use script file location (fallback)
    # Get the directory of this file (server/auth.py)
    current_file = Path(__file__).resolve()
    # Go up to server/ directory
    server_dir = current_file.parent
    # Go up to project root (week3/)
    project_root = server_dir.parent

    return project_root


def get_credentials(
    credentials_path: Optional[str] = None, token_path: Optional[str] = None
) -> Credentials:
    """Load credentials from token file and refresh if needed.

    This function does NOT initiate browser authorization.
    If token file is missing or invalid, raises an error with clear instructions.

    Args:
        credentials_path: Path to credentials.json (OAuth2 client credentials)
        token_path: Path to .token.json (stored refresh_token)

    Returns:
        Valid Credentials object with access_token

    Raises:
        FileNotFoundError: If credentials.json or .token.json is missing
        ValueError: If token file is invalid or refresh_token is missing
        Exception: If token refresh fails (e.g., refresh_token expired)
    """
    # Get project root directory
    project_root = _get_project_root()

    # Resolve paths relative to project root if not absolute
    if credentials_path:
        if not os.path.isabs(credentials_path):
            credentials_path = str(project_root / credentials_path)
    else:
        env_path = os.getenv("GMAIL_CREDENTIALS_PATH")
        if env_path:
            if not os.path.isabs(env_path):
                credentials_path = str(project_root / env_path)
            else:
                credentials_path = env_path
        else:
            credentials_path = str(project_root / DEFAULT_CREDENTIALS_PATH)

    if token_path:
        if not os.path.isabs(token_path):
            token_path = str(project_root / token_path)
    else:
        env_path = os.getenv("GMAIL_TOKEN_PATH")
        if env_path:
            if not os.path.isabs(env_path):
                token_path = str(project_root / env_path)
            else:
                token_path = env_path
        else:
            token_path = str(project_root / DEFAULT_TOKEN_PATH)

    # Check credentials.json exists
    if not os.path.exists(credentials_path):
        error_msg = (
            f"Credentials file not found: {credentials_path}\n"
            "Please ensure credentials.json exists in the project root.\n"
            "Get it from Google Cloud Console: https://console.cloud.google.com/"
        )
        print(error_msg, file=sys.stderr)
        raise FileNotFoundError(error_msg)

    # Check token file exists
    if not os.path.exists(token_path):
        error_msg = (
            f"Token file not found: {token_path}\n"
            "Please run the pre-authorization script first:\n"
            f"  python server/auth_cli.py\n"
            "This will open a browser for OAuth2 authorization and create .token.json"
        )
        print(error_msg, file=sys.stderr)
        raise FileNotFoundError(error_msg)

    # Load token from file
    try:
        with open(token_path, encoding="utf-8") as f:
            token_data = json.load(f)
    except json.JSONDecodeError as e:
        error_msg = (
            f"Invalid token file format: {token_path}\n"
            f"Error: {e}\n"
            "Please delete the corrupted .token.json and run:\n"
            f"  python server/auth_cli.py"
        )
        print(error_msg, file=sys.stderr)
        raise ValueError(error_msg) from e

    # Check refresh_token exists
    if "refresh_token" not in token_data:
        error_msg = (
            f"Token file missing refresh_token: {token_path}\n"
            "Please delete .token.json and run:\n"
            f"  python server/auth_cli.py"
        )
        print(error_msg, file=sys.stderr)
        raise ValueError(error_msg)

    # Create Credentials object
    creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    # Refresh if expired
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token back to file
                with open(token_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "token": creds.token,
                            "refresh_token": creds.refresh_token,
                            "token_uri": creds.token_uri,
                            "client_id": creds.client_id,
                            "client_secret": creds.client_secret,
                            "scopes": creds.scopes,
                        },
                        f,
                    )
            except Exception as e:
                error_msg = (
                    f"Failed to refresh access token: {e}\n"
                    "The refresh_token may have expired or been revoked.\n"
                    "Please delete .token.json and run:\n"
                    f"  python server/auth_cli.py"
                )
                print(error_msg, file=sys.stderr)
                raise Exception(error_msg) from e
        else:
            error_msg = (
                "Credentials are invalid and cannot be refreshed.\n"
                "Please delete .token.json and run:\n"
                "  python server/auth_cli.py"
            )
            print(error_msg, file=sys.stderr)
            raise ValueError(error_msg)

    return creds
