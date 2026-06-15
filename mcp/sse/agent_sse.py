# mcp/sse/agent_sse.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import asyncio
import json
import ollama
from dotenv import load_dotenv
from mcp_client_sse import get_mcp_tools_and_client, call_mcp_tool

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

SYSTEM_PROMPT = """
You are a personal productivity assistant with access to tools.

STRICT RULES:
- You MUST call all 3 tools before writing anything
- Call in order: get_calendar_events, then get_emails, then get_tasks
- Do NOT write any text until all 3 tools have returned results
- After all 3 tools return data, write the briefing

BRIEFING FORMAT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 TODAY'S SCHEDULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[meetings or "No meetings today"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TOP 3 PRIORITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [priority 1]
2. [priority 2]
3. [priority 3]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 FOCUS BLOCKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[suggested deep work blocks]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 EMAILS NEEDING REPLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[urgent emails or "None urgent"]
"""

async def run_agent_sse():
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    # Connect to running SSE server (must already be running!)
    session, mcp_tools, transport = await get_mcp_tools_and_client()

    ollama_tools = [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.inputSchema or {"type": "object", "properties": {}}
            }
        }
        for t in mcp_tools
    ]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": "Generate my morning briefing. Call all 3 tools first."
        }
    ]

    print(f"\n🤖 Agent (SSE MCP) starting with model: {model}\n")
    tools_called = []

    try:
        while True:
            response = ollama.chat(
                model=model,
                messages=messages,
                tools=ollama_tools,
                options={"temperature": 0}
            )

            msg = response["message"]
            messages.append(msg)

            if not msg.get("tool_calls"):
                remaining = [
                    t for t in ["get_calendar_events", "get_emails", "get_tasks"]
                    if t not in tools_called
                ]
                if remaining:
                    print(f"  ⚠️  Forcing remaining tools: {remaining}")
                    messages.append({
                        "role": "user",
                        "content": f"You still need to call: {remaining}. Call them now."
                    })
                    continue

                print("\n" + "━" * 50)
                print("📋  MORNING BRIEFING  [via SSE MCP]")
                print("━" * 50 + "\n")
                print(msg["content"])
                break

            for tool_call in msg["tool_calls"]:
                name = tool_call["function"]["name"]
                print(f"  🔧 [SSE MCP] Calling: {name}...")

                result = await call_mcp_tool(session, name, {})
                tools_called.append(name)
                print(f"  ✅ Done: {name}")

                messages.append({
                    "role": "tool",
                    "name": name,
                    "content": result
                })

    finally:
        await session.__aexit__(None, None, None)
        await transport.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(run_agent_sse())