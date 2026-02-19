"""Unit tests for gmail_get_message tool."""

import pytest
from unittest.mock import Mock
import base64

from server.tools import GmailMcpTools


def test_get_message_full_format(gmail_tools, mock_gmail_client):
    """Test getting message with full format."""
    body_data = base64.urlsafe_b64encode(b"Test email body").decode('utf-8')
    
    mock_gmail_client.get_message.return_value = {
        "id": "msg123",
        "threadId": "thread123",
        "snippet": "Test snippet",
        "payload": {
            "headers": [
                {"name": "From", "value": "test@example.com"},
                {"name": "To", "value": "recipient@example.com"},
                {"name": "Subject", "value": "Test Subject"},
                {"name": "Date", "value": "Mon, 1 Jan 2024 00:00:00 +0000"}
            ],
            "body": {
                "data": body_data
            },
            "mimeType": "text/plain"
        }
    }
    
    result = gmail_tools.gmail_get_message(message_id="msg123", fmt="full")
    
    assert result["id"] == "msg123"
    assert result["thread_id"] == "thread123"
    assert "body_text" in result
    assert result["body_text"] == "Test email body"
    assert "headers" in result
    assert result["headers"]["From"] == "test@example.com"


def test_get_message_metadata_format(gmail_tools, mock_gmail_client):
    """Test getting message with metadata format."""
    mock_gmail_client.get_message.return_value = {
        "id": "msg123",
        "threadId": "thread123",
        "snippet": "Test snippet",
        "payload": {
            "headers": [
                {"name": "From", "value": "test@example.com"},
                {"name": "Subject", "value": "Test Subject"}
            ]
        }
    }
    
    result = gmail_tools.gmail_get_message(message_id="msg123", fmt="metadata")
    
    assert result["id"] == "msg123"
    assert "body_text" not in result  # Should not include body in metadata format
    assert "headers" in result


def test_get_message_not_found(gmail_tools, mock_gmail_client):
    """Test handling of 404 not found errors."""
    from googleapiclient.errors import HttpError
    mock_response = Mock()
    mock_response.status = 404
    mock_gmail_client.get_message.side_effect = HttpError(mock_response, b"Not found")
    
    result = gmail_tools.gmail_get_message(message_id="nonexistent", fmt="full")
    
    assert "error" in result
    assert result["error"] == "not_found"


def test_get_message_authentication_error(gmail_tools, mock_gmail_client):
    """Test handling of 401 authentication errors."""
    from googleapiclient.errors import HttpError
    mock_response = Mock()
    mock_response.status = 401
    mock_gmail_client.get_message.side_effect = HttpError(mock_response, b"Unauthorized")
    
    result = gmail_tools.gmail_get_message(message_id="msg123", fmt="full")
    
    assert "error" in result
    assert result["error"] == "authentication_error"


def test_get_message_rate_limit_error(gmail_tools, mock_gmail_client):
    """Test handling of 429 rate limit errors."""
    from googleapiclient.errors import HttpError
    mock_response = Mock()
    mock_response.status = 429
    mock_gmail_client.get_message.side_effect = HttpError(mock_response, b"Rate limit")
    
    result = gmail_tools.gmail_get_message(message_id="msg123", fmt="full")
    
    assert "error" in result
    assert result["error"] == "rate_limited"


def test_get_message_multipart_body(gmail_tools, mock_gmail_client):
    """Test decoding multipart message body."""
    text_data = base64.urlsafe_b64encode(b"Plain text body").decode('utf-8')
    html_data = base64.urlsafe_b64encode(b"<p>HTML body</p>").decode('utf-8')
    
    mock_gmail_client.get_message.return_value = {
        "id": "msg123",
        "threadId": "thread123",
        "snippet": "Test snippet",
        "payload": {
            "headers": [
                {"name": "From", "value": "test@example.com"}
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": text_data}
                },
                {
                    "mimeType": "text/html",
                    "body": {"data": html_data}
                }
            ]
        }
    }
    
    result = gmail_tools.gmail_get_message(message_id="msg123", fmt="full")
    
    assert "body_text" in result
    assert result["body_text"] == "Plain text body"
    assert "body_html" in result
    assert result["body_html"] == "<p>HTML body</p>"

