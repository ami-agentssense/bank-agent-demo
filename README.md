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

Optional: change `CLAUDE_MODEL` in `.env` (default: `claude-sonnet-4-20250514`).

Optional: set `SELECTIVE_SKILL_LOADING=true` to attach only relevant skill markdown files per turn (keyword-based). Default is `false` (load all skills every turn).

Optional: enable Frankfurter MCP currency tools:

- `MCP_FRANKFURTER_ENABLED=true` (default)
- `MCP_FRANKFURTER_URL=https://mcp.frankfurter.dev/`

## Run

```bash
python main.py
```

## Supported banking services

- Balance inquiry
- Loan offer (with compound interest)
- 12-month term deposit
- Stock query and stock purchase
- Currency updates (via Frankfurter MCP tools when enabled)
- Account closure (requires confirmation)

