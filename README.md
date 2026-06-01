# Bank Agent Demo

Monorepo for the Apex Bank demo: **bank rep** (Jenny), **customer agent** (scenario skills), and **orchestrator** (batch runs).

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Anthropic API key

## Quick start

From the repo root:

```bash
chmod +x init-projects   # once, if needed
./init-projects
```

This will:

1. Prompt for your Anthropic API key (once)
2. Create `.env` in each subproject from `.env.example` (asks before overwriting an existing `.env`)
3. Run `uv sync` in `bank-rep-agent`, `bank-customer-agent`, and `orchestrator`

`.env` files are gitignored and stay on your machine.

## Run

| Package | Docs |
|---------|------|
| Bank rep (API / CLI) | [bank-rep-agent/README.md](bank-rep-agent/README.md) |
| Customer agent | [bank-customer-agent/README.md](bank-customer-agent/README.md) |
| Orchestrator | [orchestrator/README.md](orchestrator/README.md) |

Typical orchestrator flow:

```bash
cd orchestrator
uv run python main.py
```

## Layout

```
bank-rep-agent/       # Jenny — LangGraph + REST API
bank-customer-agent/  # Autonomous customer + skills/*.md
orchestrator/         # Plans and runs customer sessions
init-projects         # Setup script
```
