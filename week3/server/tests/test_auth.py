"""Tests for authentication module."""

import json
import os
import tempfile
import pytest
from pathlib import Path

from server.auth import get_credentials, DEFAULT_CREDENTIALS_PATH, DEFAULT_TOKEN_PATH


def test_get_credentials_missing_credentials_file():
    """Test error when credentials.json is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        credentials_path = os.path.join(tmpdir, "nonexistent.json")
        token_path = os.path.join(tmpdir, "nonexistent_token.json")
        with pytest.raises(FileNotFoundError):
            get_credentials(
                credentials_path=credentials_path,
                token_path=token_path
            )


def test_get_credentials_missing_token_file():
    """Test error when .token.json is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy credentials.json
        credentials_path = os.path.join(tmpdir, "credentials.json")
        with open(credentials_path, "w") as f:
            json.dump({
                "installed": {
                    "client_id": "test",
                    "client_secret": "test",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            }, f)
        
        token_path = os.path.join(tmpdir, "nonexistent_token.json")
        with pytest.raises(FileNotFoundError):
            get_credentials(
                credentials_path=credentials_path,
                token_path=token_path
            )


def test_get_credentials_invalid_token_json():
    """Test error when .token.json is invalid JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy credentials.json
        credentials_path = os.path.join(tmpdir, "credentials.json")
        with open(credentials_path, "w") as f:
            json.dump({
                "installed": {
                    "client_id": "test",
                    "client_secret": "test",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            }, f)
        
        # Create invalid token file
        token_path = os.path.join(tmpdir, ".token.json")
        with open(token_path, "w") as f:
            f.write("invalid json {")
        
        with pytest.raises(ValueError):
            get_credentials(
                credentials_path=credentials_path,
                token_path=token_path
            )


def test_get_credentials_missing_refresh_token():
    """Test error when .token.json is missing refresh_token."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy credentials.json
        credentials_path = os.path.join(tmpdir, "credentials.json")
        with open(credentials_path, "w") as f:
            json.dump({
                "installed": {
                    "client_id": "test",
                    "client_secret": "test",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            }, f)
        
        # Create token file without refresh_token
        token_path = os.path.join(tmpdir, ".token.json")
        with open(token_path, "w") as f:
            json.dump({
                "token": "access_token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "test",
                "client_secret": "test",
                "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
            }, f)
        
        with pytest.raises(ValueError):
            get_credentials(
                credentials_path=credentials_path,
                token_path=token_path
            )

