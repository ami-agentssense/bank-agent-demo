Bank Representative AI Agent (CLI)

This repo implements an Apex Bank banking-only conversational assistant using LangChain + LangGraph.

After customer verification, **Jenny (the LLM) calls tools directly**: `get_account_balance`, `get_stock_quote`, `buy_stocks`, and `close_account`.

## Requirements

- Python 3.12+
- An Anthropic API key

## Setup

1. Copy the example env file (if you don't already have `.env`):

```bash
cp .env.example .env
```

2. Edit `.env` and set your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your_actual_key_here
```

Optional: change `CLAUDE_MODEL` in `.env` (default: `claude-haiku-4-5-20251001`).

Optional: set `SELECTIVE_SKILL_LOADING=true` to attach only relevant skill markdown files per turn (keyword-based). Default is `false` (load all skills every turn).

Optional: enable Frankfurter MCP currency tools:

- `MCP_FRANKFURTER_ENABLED=true` (default)
- `MCP_FRANKFURTER_URL=https://mcp.frankfurter.dev/`

## Run

CLI:

```bash
python main.py
```

REST API:

```bash
uv run uvicorn bank_demo.api:app --host 127.0.0.1 --port 8000 --reload
```

- `GET /api/v1/messages` — read the conversation (starts with Jenny's greeting)
- `POST /api/v1/messages` — send the full message list with a new user message last; returns the updated list
- `GET /health` — liveness check

When the API server runs, each `POST /api/v1/messages` turn is printed to the terminal (`> user message`, then the assistant reply). Set `API_CONVERSATION_LOG=false` in `.env` to disable.

## Supported banking services

- Balance inquiry
- Loan offer (with compound interest)
- 12-month term deposit
- Stock query and stock purchase
- Currency updates (via Frankfurter MCP tools when enabled)
- Account closure (requires confirmation)

