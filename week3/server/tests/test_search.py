"""Unit tests for gmail_search_messages tool."""

import pytest
from unittest.mock import Mock, MagicMock

from server.tools import GmailMcpTools


def test_query_combination_basic(gmail_tools, mock_gmail_client):
    """Test basic query combination."""
    mock_gmail_client.list_messages.return_value = {"messages": []}
    
    result = gmail_tools.gmail_search_messages(query="from:test", max_results=10)
    
    # Verify query was combined correctly
    call_args = mock_gmail_client.list_messages.call_args
    assert call_args is not None
    assert "from:test" in call_args.kwargs["query"]


def test_query_combination_with_newer_than(gmail_tools, mock_gmail_client):
    """Test query combination with newer_than_days."""
    mock_gmail_client.list_messages.return_value = {"messages": []}
    
    result = gmail_tools.gmail_search_messages(
        query="from:test",
        max_results=10,
        newer_than_days=7
    )
    
    call_args = mock_gmail_client.list_messages.call_args
    assert call_args is not None
    query = call_args.kwargs["query"]
    assert "from:test" in query
    assert "newer_than:7d" in query


def test_query_combination_with_labels(gmail_tools, mock_gmail_client):
    """Test query combination with label_ids."""
    mock_gmail_client.list_messages.return_value = {"messages": []}
    
    result = gmail_tools.gmail_search_messages(
        query="subject:meeting",
        max_results=10,
        label_ids=["INBOX", "STARRED"]
    )
    
    call_args = mock_gmail_client.list_messages.call_args
    assert call_args is not None
    query = call_args.kwargs["query"]
    assert "subject:meeting" in query
    assert "label:INBOX" in query
    assert "label:STARRED" in query


def test_query_combination_empty_query(gmail_tools, mock_gmail_client):
    """Test query combination with empty base query."""
    mock_gmail_client.list_messages.return_value = {"messages": []}
    
    result = gmail_tools.gmail_search_messages(
        query="",
        max_results=10,
        newer_than_days=30
    )
    
    call_args = mock_gmail_client.list_messages.call_args
    assert call_args is not None
    query = call_args.kwargs["query"]
    assert "newer_than:30d" in query


def test_pagination_single_page(gmail_tools, mock_gmail_client):
    """Test pagination with single page of results."""
    mock_gmail_client.list_messages.return_value = {
        "messages": [
            {"id": "1", "threadId": "t1"},
            {"id": "2", "threadId": "t2"}
        ]
    }
    
    result = gmail_tools.gmail_search_messages(query="test", max_results=10)
    
    assert result["total_count"] == 2
    assert len(result["results"]) == 2


def test_pagination_multiple_pages(gmail_tools, mock_gmail_client):
    """Test pagination across multiple pages."""
    # First page
    mock_gmail_client.list_messages.side_effect = [
        {
            "messages": [{"id": str(i), "threadId": f"t{i}"} for i in range(10)],
            "nextPageToken": "token1"
        },
        {
            "messages": [{"id": str(i), "threadId": f"t{i}"} for i in range(10, 15)]
        }
    ]
    
    result = gmail_tools.gmail_search_messages(query="test", max_results=15)
    
    assert result["total_count"] == 15
    assert len(result["results"]) == 15
    assert mock_gmail_client.list_messages.call_count == 2


def test_pagination_respects_max_results(gmail_tools, mock_gmail_client):
    """Test pagination stops at max_results."""
    mock_gmail_client.list_messages.side_effect = [
        {
            "messages": [{"id": str(i), "threadId": f"t{i}"} for i in range(10)],
            "nextPageToken": "token1"
        },
        {
            "messages": [{"id": str(i), "threadId": f"t{i}"} for i in range(10, 20)],
            "nextPageToken": "token2"
        }
    ]
    
    result = gmail_tools.gmail_search_messages(query="test", max_results=15)
    
    assert result["total_count"] == 15
    assert len(result["results"]) == 15


def test_deduplication(gmail_tools, mock_gmail_client):
    """Test deduplication of message IDs across pages."""
    mock_gmail_client.list_messages.side_effect = [
        {
            "messages": [
                {"id": "1", "threadId": "t1"},
                {"id": "2", "threadId": "t2"},
                {"id": "3", "threadId": "t3"}
            ],
            "nextPageToken": "token1"
        },
        {
            "messages": [
                {"id": "2", "threadId": "t2"},  # Duplicate
                {"id": "3", "threadId": "t3"},  # Duplicate
                {"id": "4", "threadId": "t4"}
            ]
        }
    ]
    
    result = gmail_tools.gmail_search_messages(query="test", max_results=10)
    
    ids = [r["id"] for r in result["results"]]
    assert len(ids) == len(set(ids))  # No duplicates
    assert len(ids) == 4  # All unique IDs


def test_empty_results(gmail_tools, mock_gmail_client):
    """Test handling of empty search results."""
    mock_gmail_client.list_messages.return_value = {"messages": []}
    
    result = gmail_tools.gmail_search_messages(query="nonexistent", max_results=10)
    
    assert result["total_count"] == 0
    assert result["results"] == []
    assert "hint" in result


def test_metadata_enrichment(gmail_tools, mock_gmail_client):
    """Test metadata enrichment for first K messages."""
    # Setup list_messages response
    mock_gmail_client.list_messages.return_value = {
        "messages": [{"id": str(i), "threadId": f"t{i}"} for i in range(15)]
    }
    
    # Setup get_message responses for enrichment
    def mock_get_message(message_id, fmt):
        return {
            "id": message_id,
            "threadId": f"t{message_id}",
            "snippet": f"Snippet for {message_id}",
            "payload": {
                "headers": [
                    {"name": "From", "value": f"test{message_id}@example.com"},
                    {"name": "Subject", "value": f"Subject {message_id}"},
                    {"name": "Date", "value": "Mon, 1 Jan 2024 00:00:00 +0000"}
                ]
            }
        }
    
    mock_gmail_client.get_message.side_effect = lambda **kwargs: mock_get_message(
        kwargs["message_id"], kwargs.get("fmt", "metadata")
    )
    
    result = gmail_tools.gmail_search_messages(query="test", max_results=15)
    
    # First 10 should be enriched
    assert result["results"][0]["from_email"] is not None
    assert result["results"][0]["subject"] is not None
    # Remaining should have basic info only
    assert result["results"][10]["from_email"] is None or result["results"][10]["from_email"] == ""


def test_metadata_enrichment_failure_graceful(gmail_tools, mock_gmail_client):
    """Test graceful handling of metadata enrichment failures."""
    mock_gmail_client.list_messages.return_value = {
        "messages": [{"id": "1", "threadId": "t1"}]
    }
    
    # Make get_message fail
    from googleapiclient.errors import HttpError
    mock_response = Mock()
    mock_response.status = 404
    mock_gmail_client.get_message.side_effect = HttpError(mock_response, b"Not found")
    
    result = gmail_tools.gmail_search_messages(query="test", max_results=10)
    
    # Should still return basic info
    assert len(result["results"]) == 1
    assert result["results"][0]["id"] == "1"


def test_authentication_error(gmail_tools, mock_gmail_client):
    """Test handling of 401 authentication errors."""
    from googleapiclient.errors import HttpError
    mock_response = Mock()
    mock_response.status = 401
    mock_gmail_client.list_messages.side_effect = HttpError(mock_response, b"Unauthorized")
    
    result = gmail_tools.gmail_search_messages(query="test", max_results=10)
    
    assert "error" in result
    assert result["error"] == "authentication_error"


def test_rate_limit_error(gmail_tools, mock_gmail_client):
    """Test handling of 429 rate limit errors."""
    from googleapiclient.errors import HttpError
    mock_response = Mock()
    mock_response.status = 429
    mock_gmail_client.list_messages.side_effect = HttpError(mock_response, b"Rate limit")
    
    result = gmail_tools.gmail_search_messages(query="test", max_results=10)
    
    assert "error" in result
    assert result["error"] == "rate_limited"

