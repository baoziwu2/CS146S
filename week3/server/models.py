"""Data models for Gmail MCP Server."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Sequence

from pydantic import BaseModel, Field, PositiveInt, conint

MessageFormat = Literal["full", "metadata"]


@dataclass(frozen=True)
class SearchResultItem:
    """Search result item with metadata."""

    id: str
    thread_id: str
    from_email: Optional[str] = None
    subject: Optional[str] = None
    date: Optional[str] = None
    snippet: Optional[str] = None


class SearchParams(BaseModel):
    """Parameters for gmail_search_messages tool."""

    query: str = Field(
        min_length=1,
        description="Gmail search query syntax (see https://support.google.com/mail/answer/7190)",
    )
    max_results: conint(ge=1, le=50) = 10
    newer_than_days: Optional[PositiveInt] = None
    label_ids: Optional[Sequence[str]] = None


class GetMessageParams(BaseModel):
    """Parameters for gmail_get_message tool."""

    message_id: str = Field(min_length=5, description="Gmail message ID")
    fmt: str = Field(
        default="full",
        pattern="^(full|metadata)$",
        description="Message format: 'full' or 'metadata'",
    )
