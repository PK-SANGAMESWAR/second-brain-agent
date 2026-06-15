# mcp/sse/mcp_server_sse.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import json
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp import types
from tools import get_calendar_events, get_emails, get_tasks
from starlette.requests import Request
from starlette.routing import Route
from starlette.applications import Starlette

# Create MCP server
app_mcp = Server("second-brain-sse")

@app_mcp.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_calendar_events",
            description="Returns today's calendar events with title and time.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="get_emails",
            description="Returns unread emails with sender, subject and snippet.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="get_tasks",
            description="Returns pending tasks from Notion with priority and due date.",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]

@app_mcp.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    print(f"[MCP SSE Server] Tool called: {name}")

    if name == "get_calendar_events":
        result = get_calendar_events()
    elif name == "get_emails":
        result = get_emails()
    elif name == "get_tasks":
        result = get_tasks()
    else:
        result = json.dumps({"error": f"Unknown tool: {name}"})

    return [types.TextContent(type="text", text=result)]

sse_transport = SseServerTransport("/messages/")

async def sse_endpoint(request: Request):
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await app_mcp.run(
            streams[0], streams[1],
            app_mcp.create_initialization_options()
        )

async def handle_messages(request: Request):
    await sse_transport.handle_post_message(
        request.scope, request.receive, request._send
    )

starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=sse_endpoint),
        Route("/messages/", endpoint=handle_messages, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    print("[MCP SSE Server] Starting on http://localhost:8000")
    print("[MCP SSE Server] SSE endpoint: http://localhost:8000/sse")
    uvicorn.run(starlette_app, host="0.0.0.0", port=8000)