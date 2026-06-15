# agent.py
import json
import ollama
from tools import TOOLS, TOOL_DEFINITIONS
from dotenv import load_dotenv
import os

load_dotenv()


SYSTEM_PROMPT = """
You are a productivity assistant with access to tools.

STRICT RULES:
- You MUST call all 3 tools before writing anything
- Call them in this exact order: get_calendar_events, then get_emails, then get_tasks
- Do NOT write any text until all 3 tools have returned results
- Do NOT explain what you are going to do — just call the tools
- After all 3 tools return data, write the briefing and nothing else

BRIEFING FORMAT (use exactly this):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 TODAY'S SCHEDULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[list meetings with times, or "No meetings today"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TOP 3 PRIORITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [highest priority item]
2. [second priority item]
3. [third priority item]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 FOCUS BLOCKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[suggest 2-3 time blocks for deep work based on calendar gaps]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 EMAILS NEEDING REPLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[list emails that need action, or "None urgent"]
"""

def run_agent():
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Generate my morning briefing for today June 15 2026. "
                "You MUST call get_calendar_events, get_emails, and get_tasks "
                "before writing anything. Call all 3 tools now."
            )
        }
    ]

    print(f"🤖 Agent starting with model: {model}\n")

    tools_called = []

    while True:
        response = ollama.chat(
            model=model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            options={"temperature": 0}  # deterministic — no creativity in tool calling
        )

        msg = response["message"]
        messages.append(msg)

        # If no tool calls but not all tools called yet → force it
        if not msg.get("tool_calls"):
            remaining = [
                t for t in ["get_calendar_events", "get_emails", "get_tasks"]
                if t not in tools_called
            ]

            if remaining:
                print(f"  ⚠️  Model skipped tools, forcing: {remaining}")
                messages.append({
                    "role": "user",
                    "content": f"You have not called these tools yet: {remaining}. Call them now before writing the briefing."
                })
                continue

            # All tools called → print briefing
            print("\n" + "━" * 50)
            print("📋  MORNING BRIEFING")
            print("━" * 50 + "\n")
            print(msg["content"])
            break

        # Execute tool calls
        for tool_call in msg["tool_calls"]:
            name = tool_call["function"]["name"]
            print(f"  🔧 Calling: {name}...")

            fn = TOOLS.get(name)
            if fn:
                result = fn()
                tools_called.append(name)
                print(f"  ✅ Done: {name}")
            else:
                result = json.dumps({"error": f"Unknown tool: {name}"})

            messages.append({
                "role": "tool",
                "name": name,
                "content": result
            })