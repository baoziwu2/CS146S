"""MCP Server entry point for Gmail API.

STDIO transport server that registers Gmail tools.
"""

import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from server.auth import get_credentials
from server.gmail_client import GmailClient
from server.tools import GmailMcpTools


# Initialize server
app = Server("gmail-mcp-server")

# Initialize Gmail client and tools (lazy initialization)
_gmail_tools: GmailMcpTools | None = None


def get_gmail_tools() -> GmailMcpTools:
    """Get or initialize Gmail tools instance."""
    global _gmail_tools
    if _gmail_tools is None:
        try:
            creds = get_credentials()
            client = GmailClient(creds)
            _gmail_tools = GmailMcpTools(client)
        except Exception as e:
            print(f"Failed to initialize Gmail client: {e}", file=sys.stderr)
            raise
    return _gmail_tools


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="gmail_search_messages",
            description=(
                "Search Gmail messages using Gmail query syntax. "
                "Supports query filters, date ranges, and label filtering. "
                "Returns a list of messages with metadata (subject, from, date, snippet). "
                "See Gmail search syntax: https://support.google.com/mail/answer/7190"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (e.g., 'from:example@gmail.com', 'subject:meeting'). See https://support.google.com/mail/answer/7190"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-50)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    },
                    "newer_than_days": {
                        "type": "integer",
                        "description": "Filter messages newer than N days (optional)",
                        "minimum": 1
                    },
                    "label_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by label IDs (e.g., ['INBOX', 'STARRED']) (optional)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="gmail_get_message",
            description=(
                "Get detailed information about a Gmail message by ID. "
                "Returns headers, body content (text/HTML), and snippet."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "Gmail message ID (obtained from search results)"
                    },
                    "fmt": {
                        "type": "string",
                        "description": "Message format: 'full' (includes body) or 'metadata' (headers only)",
                        "enum": ["full", "metadata"],
                        "default": "full"
                    }
                },
                "required": ["message_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        tools = get_gmail_tools()
        
        if name == "gmail_search_messages":
            # Validate and extract parameters
            query = arguments.get("query", "")
            if not query:
                return [TextContent(
                    type="text",
                    text='{"error": "invalid_input", "message": "query parameter is required"}'
                )]
            
            max_results = arguments.get("max_results", 10)
            newer_than_days = arguments.get("newer_than_days")
            label_ids = arguments.get("label_ids")
            
            # Call tool
            result = tools.gmail_search_messages(
                query=query,
                max_results=max_results,
                newer_than_days=newer_than_days,
                label_ids=label_ids
            )
            
            # Return as JSON string
            import json
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "gmail_get_message":
            # Validate and extract parameters
            message_id = arguments.get("message_id", "")
            if not message_id:
                return [TextContent(
                    type="text",
                    text='{"error": "invalid_input", "message": "message_id parameter is required"}'
                )]
            
            fmt = arguments.get("fmt", "full")
            if fmt not in ["full", "metadata"]:
                fmt = "full"
            
            # Call tool
            result = tools.gmail_get_message(
                message_id=message_id,
                fmt=fmt
            )
            
            # Return as JSON string
            import json
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f'{{"error": "unknown_tool", "message": "Unknown tool: {name}"}}'
            )]
    
    except Exception as e:
        # Log error to stderr (not stdout, to avoid polluting STDIO)
        print(f"Tool call error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        # Return error to client
        import json
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "tool_execution_error",
                "message": str(e)
            }, ensure_ascii=False)
        )]


async def main():
    """Run MCP server with STDIO transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)

