"""Gmail API client with retry logic and error handling.

Thin wrapper around Gmail API with retries, timeouts, and typed responses.
References:
- messages.list: https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list
- messages.get:  https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get
"""

import time
from typing import Any, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from server.models import MessageFormat


class GmailClient:
    """Thin wrapper around Gmail API with retries, timeouts, and typed responses."""

    def __init__(self, credentials: Credentials):
        """Initialize Gmail client with credentials.

        Args:
            credentials: OAuth2 credentials from auth.get_credentials()
        """
        self.credentials = credentials
        self.service = build("gmail", "v1", credentials=credentials)

    def _retry_with_backoff(self, func, max_retries: int, backoff_base: float = 1.0):
        """Retry function with exponential backoff.

        Args:
            func: Function to retry (callable that returns result)
            max_retries: Maximum number of retries
            backoff_base: Base delay in seconds (will be multiplied by 2^retry_count)

        Returns:
            Function result

        Raises:
            HttpError: If all retries fail
        """
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                return func()
            except HttpError as e:
                last_error = e
                status_code = getattr(e, "status_code", None) or (
                    e.resp.status if hasattr(e, "resp") and hasattr(e.resp, "status") else None
                )

                # 401: Authentication error - don't retry
                if status_code == 401:
                    raise

                # 429: Rate limit - retry with backoff
                if status_code == 429:
                    if attempt < max_retries:
                        delay = backoff_base * (2**attempt)
                        time.sleep(delay)
                        continue
                    else:
                        raise

                # 5xx: Server error - retry with backoff (fewer retries)
                if status_code and 500 <= status_code < 600:
                    if attempt < max_retries:
                        delay = backoff_base * (2**attempt)
                        time.sleep(delay)
                        continue
                    else:
                        raise

                # Other errors - don't retry
                raise

        # Should not reach here, but just in case
        if last_error:
            raise last_error

    def list_messages(
        self, *, user_id: str = "me", query: str, max_results: int, page_token: Optional[str] = None
    ) -> dict[str, Any]:
        """Call Gmail API messages.list endpoint.

        Args:
            user_id: Gmail user ID (default: "me" for authenticated user)
            query: Gmail search query (see https://support.google.com/mail/answer/7190)
            max_results: Maximum number of results per page (1-500)
            page_token: Optional page token for pagination

        Returns:
            {
                "messages": [{"id": "...", "threadId": "..."}, ...],
                "nextPageToken": "..." (optional),
                "resultSizeEstimate": int
            }

        Raises:
            HttpError: If API call fails after retries
        """

        def _call():
            results = (
                self.service.users()
                .messages()
                .list(
                    userId=user_id,
                    q=query,
                    maxResults=min(max_results, 500),  # Gmail API limit is 500
                    pageToken=page_token,
                )
                .execute()
            )
            return results

        # 429: retry 3 times with 1s/2s/4s backoff
        # 5xx: retry 2 times with 1s/2s backoff
        return self._retry_with_backoff(_call, max_retries=3, backoff_base=1.0)

    def get_message(
        self, *, user_id: str = "me", message_id: str, fmt: MessageFormat = "full"
    ) -> dict[str, Any]:
        """Call Gmail API messages.get endpoint.

        Args:
            user_id: Gmail user ID (default: "me" for authenticated user)
            message_id: Gmail message ID
            fmt: Message format ("full" or "metadata")

        Returns:
            {
                "id": "...",
                "threadId": "...",
                "snippet": "...",
                "payload": {
                    "headers": [...],
                    "body": {...},
                    "parts": [...]
                }
            }

        Raises:
            HttpError: If API call fails after retries
        """

        def _call():
            results = (
                self.service.users()
                .messages()
                .get(userId=user_id, id=message_id, format=fmt)
                .execute()
            )
            return results

        # 429: retry 3 times with 1s/2s/4s backoff
        # 5xx: retry 2 times with 1s/2s backoff
        return self._retry_with_backoff(_call, max_retries=3, backoff_base=1.0)
