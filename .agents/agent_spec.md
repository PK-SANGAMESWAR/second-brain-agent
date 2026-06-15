# agent.py Spec

## Purpose
Core agentic loop — sends messages to Ollama, handles tool calls,
feeds results back, loops until LLM stops calling tools.

## Flow
1. Build initial messages (system prompt + user message)
2. Call ollama.chat() with TOOL_DEFINITIONS
3. If response has tool_calls → execute each via TOOLS registry
4. Append tool result to messages as role: "tool"
5. Loop back to step 2
6. When no tool_calls → print final briefing and exit

## System prompt goal
Tell the LLM to:
- Call all 3 tools before writing anything
- Output briefing with: top 3 priorities, focus blocks, emails needing reply

## Constraints
- Import TOOLS and TOOL_DEFINITIONS from tools.py
- Model name comes from config.py (do not hardcode)
- Print tool name each time it's called
- Loop must be a while True with a break on no tool_calls