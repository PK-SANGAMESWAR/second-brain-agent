# mcp/sse/mcp_client_sse.py
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

SERVER_URL = "http://localhost:8000/sse"

async def get_mcp_tools_and_client():
    """Connect to running SSE MCP server and return session + tools."""
    transport = sse_client(SERVER_URL)
    read, write = await transport.__aenter__()

    session = ClientSession(read, write)
    await session.__aenter__()
    await session.initialize()

    tools_response = await session.list_tools()
    tools = tools_response.tools

    print(f"[MCP SSE Client] Connected to {SERVER_URL}")
    print(f"[MCP SSE Client] Tools available: {[t.name for t in tools]}")

    return session, tools, transport

async def call_mcp_tool(session: ClientSession, tool_name: str, arguments: dict = {}) -> str:
    """Call a tool on the SSE MCP server."""
    result = await session.call_tool(tool_name, arguments)
    return result.content[0].text