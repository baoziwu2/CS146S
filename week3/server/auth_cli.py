"""Pre-authorization CLI script for Gmail OAuth2.

Run this script ONCE in a terminal with browser access to complete
OAuth2 authorization and generate .token.json.

Usage:
    python server/auth_cli.py

This script will:
1. Open a browser for OAuth2 authorization
2. Save refresh_token to .token.json
3. The MCP server will use this token file for runtime authentication
"""

import json
import os
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

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
    3. Script file location (server/auth_cli.py -> server/ -> week3/)

    Returns:
        Path to project root directory
    """
    import os

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
    # Get the directory of this file (server/auth_cli.py)
    current_file = Path(__file__).resolve()
    # Go up to server/ directory
    server_dir = current_file.parent
    # Go up to project root (week3/)
    project_root = server_dir.parent

    return project_root


def main():
    """Run OAuth2 authorization flow and save token."""
    # Get project root directory
    project_root = _get_project_root()

    # Resolve paths relative to project root if not absolute
    env_creds_path = os.getenv("GMAIL_CREDENTIALS_PATH")
    if env_creds_path:
        if os.path.isabs(env_creds_path):
            credentials_path = env_creds_path
        else:
            credentials_path = str(project_root / env_creds_path)
    else:
        credentials_path = str(project_root / DEFAULT_CREDENTIALS_PATH)

    env_token_path = os.getenv("GMAIL_TOKEN_PATH")
    if env_token_path:
        if os.path.isabs(env_token_path):
            token_path = env_token_path
        else:
            token_path = str(project_root / env_token_path)
    else:
        token_path = str(project_root / DEFAULT_TOKEN_PATH)

    # Check credentials.json exists
    if not os.path.exists(credentials_path):
        print(f"Error: Credentials file not found: {credentials_path}", file=sys.stderr)
        print(
            "Please download credentials.json from Google Cloud Console:\n"
            "1. Go to https://console.cloud.google.com/\n"
            "2. Create/select a project\n"
            "3. Enable Gmail API\n"
            "4. Create OAuth 2.0 Client ID credentials\n"
            "5. Download as credentials.json and place in project root",
            file=sys.stderr,
        )
        sys.exit(1)

    # Check if token already exists
    if os.path.exists(token_path):
        response = input(
            f"Token file already exists: {token_path}\n" "Do you want to re-authorize? (y/N): "
        )
        if response.lower() != "y":
            print("Cancelled. Using existing token file.")
            sys.exit(0)

    print("Starting OAuth2 authorization flow...")
    print(f"Credentials: {credentials_path}")
    print(f"Token will be saved to: {token_path}")
    print("\nA browser window will open for authorization.")
    print("Please complete the authorization in the browser.\n")

    try:
        # Create OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)

        # Run local server to handle OAuth2 callback
        # This will open a browser and wait for user authorization
        creds = flow.run_local_server(port=0)

        # Save credentials to token file
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }

        with open(token_path, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)

        print("\n✓ Authorization successful!")
        print(f"✓ Token saved to: {token_path}")
        print("\nYou can now start the MCP server. It will use this token file.")
        print("Note: .token.json is gitignored and should not be committed.")

    except KeyboardInterrupt:
        print("\n\nAuthorization cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError during authorization: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
