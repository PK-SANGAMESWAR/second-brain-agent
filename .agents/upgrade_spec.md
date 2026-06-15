# upgrade_spec.md — Future API Swap Guide

## Goal
Document how to replace mock tools with real APIs
without touching agent.py at all.

## Swap plan
| File              | Mock source         | Real replacement         |
|-------------------|---------------------|--------------------------|
| calendar.json     | static file         | Google Calendar API      |
| emails.json       | static file         | Gmail API                |
| tasks.json        | static file         | Notion API / local DB    |

## Rule
Only tools.py changes during upgrade.
agent.py, main.py, prompts stay identical.
Each real API function must return json.dumps(list) — same as mock.