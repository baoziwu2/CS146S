"""MCP tool implementations for Gmail API.

Tool layer that validates inputs and returns stable JSON responses.
"""

import base64
import re
from typing import Any, Optional, Sequence

from googleapiclient.errors import HttpError

from server.gmail_client import GmailClient
from server.models import GetMessageParams, MessageFormat, SearchParams, SearchResultItem


class GmailMcpTools:
    """MCP tool implementations that validate inputs and return stable JSON."""
    
    def __init__(self, gmail_client: GmailClient):
        """Initialize tools with Gmail client.
        
        Args:
            gmail_client: Authenticated GmailClient instance
        """
        self.client = gmail_client
        self.metadata_enrichment_limit = 10  # Only enrich first K messages
    
    def _combine_query(
        self,
        query: str,
        newer_than_days: Optional[int] = None,
        label_ids: Optional[Sequence[str]] = None
    ) -> str:
        """Combine base query with optional filters.
        
        Args:
            query: Base Gmail search query
            newer_than_days: Optional days filter (converted to newer_than:Nd)
            label_ids: Optional label filters (converted to label:LABEL)
        
        Returns:
            Combined query string
        """
        parts = []
        
        # Add base query
        if query.strip():
            parts.append(query.strip())
        
        # Add newer_than filter
        if newer_than_days is not None:
            parts.append(f"newer_than:{newer_than_days}d")
        
        # Add label filters
        if label_ids:
            for label_id in label_ids:
                parts.append(f"label:{label_id}")
        
        return " ".join(parts) if parts else "in:anywhere"
    
    def _extract_header(self, headers: list[dict[str, str]], name: str) -> Optional[str]:
        """Extract header value by name (case-insensitive).
        
        Args:
            headers: List of header dicts with 'name' and 'value' keys
            name: Header name to find
        
        Returns:
            Header value or None
        """
        for header in headers:
            if header.get('name', '').lower() == name.lower():
                return header.get('value')
        return None
    
    def _decode_body(self, payload: dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        """Decode email body from payload.
        
        Args:
            payload: Gmail API message payload
        
        Returns:
            Tuple of (body_text, body_html)
        """
        body_text = None
        body_html = None
        
        # Check if body exists in payload
        if 'body' in payload and 'data' in payload['body']:
            data = payload['body']['data']
            try:
                decoded = base64.urlsafe_b64decode(data).decode('utf-8')
                if payload.get('mimeType', '').startswith('text/plain'):
                    body_text = decoded
                elif payload.get('mimeType', '').startswith('text/html'):
                    body_html = decoded
            except Exception:
                pass
        
        # Check parts (multipart messages)
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType', '').startswith('text/plain'):
                    if 'body' in part and 'data' in part['body']:
                        try:
                            body_text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        except Exception:
                            pass
                elif part.get('mimeType', '').startswith('text/html'):
                    if 'body' in part and 'data' in part['body']:
                        try:
                            body_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        except Exception:
                            pass
                
                # Recursively check nested parts
                if 'parts' in part:
                    nested_text, nested_html = self._decode_body(part)
                    if nested_text and not body_text:
                        body_text = nested_text
                    if nested_html and not body_html:
                        body_html = nested_html
        
        return body_text, body_html
    
    def gmail_search_messages(
        self,
        *,
        query: str,
        max_results: int = 10,
        newer_than_days: Optional[int] = None,
        label_ids: Optional[Sequence[str]] = None
    ) -> dict[str, Any]:
        """Search Gmail messages with query syntax.
        
        Combines query with newer_than_days and label_ids filters.
        Handles pagination, deduplication, and metadata enrichment.
        
        Args:
            query: Gmail search query (see https://support.google.com/mail/answer/7190)
            max_results: Maximum number of results (1-50, default 10)
            newer_than_days: Optional filter for messages newer than N days
            label_ids: Optional list of label IDs to filter by
        
        Returns:
            {
                "results": [SearchResultItem, ...],
                "total_count": int,
                "hint": str (optional, for empty results)
            }
        """
        # Validate and combine query
        combined_query = self._combine_query(query, newer_than_days, label_ids)
        
        # Collect all message IDs with pagination
        all_message_ids: list[dict[str, str]] = []
        seen_ids: set[str] = set()
        page_token: Optional[str] = None
        max_pages = 10  # Safety limit to prevent infinite loops
        
        for page_num in range(max_pages):
            try:
                # Call messages.list
                response = self.client.list_messages(
                    query=combined_query,
                    max_results=min(500, max_results * 2),  # Request more to account for dedup
                    page_token=page_token
                )
                
                messages = response.get('messages', [])
                
                # Add new message IDs (deduplicate)
                for msg in messages:
                    msg_id = msg.get('id')
                    if msg_id and msg_id not in seen_ids:
                        all_message_ids.append({
                            'id': msg_id,
                            'threadId': msg.get('threadId', '')
                        })
                        seen_ids.add(msg_id)
                
                # Check if we have enough results
                if len(all_message_ids) >= max_results:
                    all_message_ids = all_message_ids[:max_results]
                    break
                
                # Check for next page
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
                    
            except HttpError as e:
                # Handle errors
                status_code = getattr(e, 'status_code', None) or (e.resp.status if hasattr(e, 'resp') and hasattr(e.resp, 'status') else None)
                if status_code == 401:
                    return {
                        "error": "authentication_error",
                        "message": "Gmail API authentication failed. Please re-authorize by running: python server/auth_cli.py",
                        "results": []
                    }
                elif status_code == 429:
                    return {
                        "error": "rate_limited",
                        "message": "Gmail API rate limit exceeded. Please try again later.",
                        "results": []
                    }
                else:
                    return {
                        "error": "api_error",
                        "message": f"Gmail API error: {e}",
                        "results": []
                    }
        
        # Handle empty results
        if not all_message_ids:
            return {
                "results": [],
                "total_count": 0,
                "hint": "No messages found. Try adjusting your search criteria."
            }
        
        # Enrich first K messages with metadata
        results: list[SearchResultItem] = []
        enrich_count = min(self.metadata_enrichment_limit, len(all_message_ids))
        
        for i, msg_info in enumerate(all_message_ids):
            msg_id = msg_info['id']
            thread_id = msg_info['threadId']
            
            # Enrich first K messages
            if i < enrich_count:
                try:
                    msg_data = self.client.get_message(message_id=msg_id, fmt="metadata")
                    payload = msg_data.get('payload', {})
                    headers = payload.get('headers', [])
                    
                    from_email = self._extract_header(headers, 'From')
                    subject = self._extract_header(headers, 'Subject')
                    date = self._extract_header(headers, 'Date')
                    snippet = msg_data.get('snippet', '')
                    
                    results.append(SearchResultItem(
                        id=msg_id,
                        thread_id=thread_id,
                        from_email=from_email,
                        subject=subject,
                        date=date,
                        snippet=snippet
                    ))
                except Exception:
                    # Fallback: return basic info if enrichment fails
                    results.append(SearchResultItem(
                        id=msg_id,
                        thread_id=thread_id
                    ))
            else:
                # For remaining messages, return basic info
                results.append(SearchResultItem(
                    id=msg_id,
                    thread_id=thread_id
                ))
        
        # Convert to dict for JSON serialization
        return {
            "results": [
                {
                    "id": r.id,
                    "thread_id": r.thread_id,
                    "from_email": r.from_email,
                    "subject": r.subject,
                    "date": r.date,
                    "snippet": r.snippet
                }
                for r in results
            ],
            "total_count": len(results)
        }
    
    def gmail_get_message(
        self,
        *,
        message_id: str,
        fmt: MessageFormat = "full"
    ) -> dict[str, Any]:
        """Get message details by ID.
        
        Returns structured headers and body content.
        
        Args:
            message_id: Gmail message ID
            fmt: Message format ("full" or "metadata")
        
        Returns:
            {
                "id": str,
                "thread_id": str,
                "headers": {...},
                "body_text": str (optional),
                "body_html": str (optional),
                "snippet": str
            }
        """
        try:
            msg_data = self.client.get_message(message_id=message_id, fmt=fmt)
            
            payload = msg_data.get('payload', {})
            headers = payload.get('headers', [])
            
            # Extract common headers
            header_dict = {}
            for header in headers:
                name = header.get('name', '')
                value = header.get('value', '')
                header_dict[name] = value
            
            result = {
                "id": msg_data.get('id', ''),
                "thread_id": msg_data.get('threadId', ''),
                "headers": header_dict,
                "snippet": msg_data.get('snippet', '')
            }
            
            # Decode body if format is "full"
            if fmt == "full":
                body_text, body_html = self._decode_body(payload)
                if body_text:
                    result["body_text"] = body_text
                if body_html:
                    result["body_html"] = body_html
            
            return result
            
        except HttpError as e:
            status_code = getattr(e, 'status_code', None) or (e.resp.status if hasattr(e, 'resp') and hasattr(e.resp, 'status') else None)
            # Gmail API returns 400 for invalid message IDs, 404 for non-existent messages
            if status_code == 404 or (status_code == 400 and 'Invalid id' in str(e)):
                return {
                    "error": "not_found",
                    "message": f"Message not found: {message_id}. Please check the message_id is correct."
                }
            elif status_code == 401:
                return {
                    "error": "authentication_error",
                    "message": "Gmail API authentication failed. Please re-authorize by running: python server/auth_cli.py"
                }
            elif status_code == 429:
                return {
                    "error": "rate_limited",
                    "message": "Gmail API rate limit exceeded. Please try again later."
                }
            else:
                return {
                    "error": "api_error",
                    "message": f"Gmail API error: {e}"
                }
        except Exception as e:
            return {
                "error": "unknown_error",
                "message": f"Unexpected error: {e}"
            }

