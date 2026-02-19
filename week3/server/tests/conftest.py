"""Pytest configuration and fixtures."""

import os
import pytest
from unittest.mock import Mock, MagicMock
from google.oauth2.credentials import Credentials

from server.auth import get_credentials
from server.gmail_client import GmailClient
from server.tools import GmailMcpTools


@pytest.fixture
def mock_credentials():
    """Mock OAuth2 credentials."""
    creds = Mock(spec=Credentials)
    creds.valid = True
    creds.token = "mock_access_token"
    creds.refresh_token = "mock_refresh_token"
    return creds


@pytest.fixture
def mock_gmail_client(mock_credentials):
    """Mock GmailClient."""
    client = Mock(spec=GmailClient)
    client.credentials = mock_credentials
    return client


@pytest.fixture
def gmail_tools(mock_gmail_client):
    """GmailMcpTools instance with mocked client."""
    return GmailMcpTools(mock_gmail_client)


@pytest.fixture(scope="session")
def live_credentials():
    """Real credentials for live API tests.
    
    Requires .token.json to exist.
    Skips test if credentials are not available.
    """
    try:
        return get_credentials()
    except Exception as e:
        pytest.skip(f"Live credentials not available: {e}")


@pytest.fixture
def live_gmail_client(live_credentials):
    """Real GmailClient for live API tests."""
    return GmailClient(live_credentials)


@pytest.fixture
def live_gmail_tools(live_gmail_client):
    """Real GmailMcpTools for live API tests."""
    return GmailMcpTools(live_gmail_client)


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "live: mark test as requiring live Gmail API access")

