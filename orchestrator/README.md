# Bank Orchestrator

Conversational agent that plans and runs batches of customer-agent sessions against the bank rep API.

## Setup

```bash
cd orchestrator
cp .env.example .env
# Set ANTHROPIC_API_KEY
uv sync
```

Requires sibling projects `bank-rep-agent` and `bank-customer-agent` with `uv` installed.

## Run

```bash
uv run python main.py
```

Example:

```
> Run 5 sessions: 40% angry, 60% random
```

Commands:
- `yes` — run pending plan
- `no` — cancel pending plan
- `refresh skills` — re-read and re-classify skills
- `quit` — exit

## How it works

1. Reads all `bank-customer-agent/skills/*.md` and classifies each with LLM (cached by file mtime)
2. Builds a run plan from your request
3. Per session: start rep server → wait 1s → run customer agent → stop rep server

## Config

See `.env.example` for all variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `ORCHESTRATOR_STREAM_TRANSCRIPT` | `true` | Stream customer turn logs live during each session |
| `ORCHESTRATOR_STREAM_TURNS_ONLY` | `true` | Only stream `--- turn`, `CUSTOMER:`, `BANK:`, and result lines |
| `CUSTOMER_CONVERSATION_LOG` | `false` | Must be `true` for the customer agent to emit turn lines |

## Skill index

On startup the orchestrator scans `bank-customer-agent/skills/*.md` and maintains `orchestrator/.skill_index.json` with persona, goal, behavior, and tags. Only skills whose file mtime is newer than the index entry are re-classified (LLM); others load instantly from the index.

CLI output example:

```
Apex Bank Orchestrator — loading skills…
Updated skill: alice_balance
Loaded 14 skill(s) (1 updated, 13 from index).
```

- `refresh skills` — force re-classify all skills and rewrite the index.
- Session runs still load the **full** skill markdown via the customer agent (`--skill <name>`); the index is for planning only.

Optional: `SKILL_INDEX_PATH` in `.env` (default `.skill_index.json` under `orchestrator/`).
