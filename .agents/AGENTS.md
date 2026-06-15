# Second Brain Agent — Project Spec

## Goal
A local AI agent that fetches calendar events, emails, and tasks,
then produces a morning briefing using a local Ollama LLM.

## Stack
- Python 3.11+
- Ollama (local LLM, model: qwen2.5-coder:7b)
- No external APIs yet — all tools use mock JSON data

## Project Structure
second-brain-agent/
├── main.py
├── agent.py
├── tools.py
├── mock_data/
│   ├── calendar.json
│   ├── emails.json
│   └── tasks.json
└── requirements.txt

## Rules for Codex
- Never install packages outside requirements.txt
- Keep agent loop in agent.py, tools isolated in tools.py
- Each spec file in .agents/ maps to one source file
- Do not hardcode data — always read from mock_data/
- Add a print statement for every tool call so flow is visible