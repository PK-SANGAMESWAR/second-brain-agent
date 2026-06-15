# tools.py Spec

## Purpose
Expose 3 tool functions to the agent. Each reads from mock_data/.

## Functions
- get_calendar_events() → reads mock_data/calendar.json, returns JSON string
- get_emails()          → reads mock_data/emails.json, returns JSON string  
- get_tasks()           → reads mock_data/tasks.json, returns JSON string

## Exports
- TOOLS dict: maps tool name (string) → function
- TOOL_DEFINITIONS list: Ollama-compatible tool schema for all 3 tools

## Tool schema format (Ollama expects this)
{
  "type": "function",
  "function": {
    "name": "...",
    "description": "...",
    "parameters": {"type": "object", "properties": {}}
  }
}

## Constraints
- No external imports beyond json and pathlib
- Functions must return strings (json.dumps), not dicts