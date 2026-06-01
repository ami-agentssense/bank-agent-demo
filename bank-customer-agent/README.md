# Bank Customer Agent

Autonomous LLM customer that talks to [bank-rep-agent](../bank-rep-agent) (Jenny) over REST.

Behavior is driven by a **skill file** — markdown with customer details, goal, and behavior.

## Setup

```bash
cd bank-customer-agent
cp .env.example .env
# Set ANTHROPIC_API_KEY in .env
uv sync
```

## Run

**Terminal 1** — bank rep (must be running first):

```bash
cd bank-rep-agent
uv run uvicorn bank_demo.api:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2** — customer agent:

```bash
cd bank-customer-agent
uv run python main.py --skill alice_balance
uv run python main.py --list-skills
```

Multi-step skills need `MAX_TURNS=30` or higher in `.env`.

## Skills

### Basic (4)

| Skill | Description |
|-------|-------------|
| `alice_balance` | Log in as CUST-1001, check balance |
| `david_loan` | Log in as CUST-1002, apply for $2k loan |
| `sara_buy_stock` | Log in as CUST-1003, buy 2 AAPL shares |
| `john_forgot_id` | Forgot ID, recover CUST-1001, check balance |

### Multi-step — balance + EUR + loan (6)

| Skill | Description |
|-------|-------------|
| `marcus_angry_triple` | Angry customer: balance → EUR → loan |
| `rachel_angry_balance_loan` | Angry: disputes balance, EUR, $5k/5y loan |
| `elena_planned_borrower` | Calm methodical: balance → EUR → $10k loan |
| `tommy_quick_check_rate_loan` | Rushed polite: balance → EUR → loan |
| `nina_skeptical_researcher` | Questioning: balance → EUR → loan with explanations |
| `viktor_forgot_id_full_tour` | Forgot ID, then balance → EUR → loan |

### Personality — complex behaviors (4)

| Skill | Description |
|-------|-------------|
| `owen_balance_dispute` | Argues balance should be ~$15k, then continues |
| `lily_overly_polite` | Excessively polite / lightly flirtatious |
| `ben_confused_customer` | Often confused; asks Jenny to re-explain |
| `carl_frustrated_quit` | Frustrated, mild cursing, hangs up (no loan) |

Add your own in `skills/*.md`.

## Skill format

```markdown
# Customer Details
- Name: ...
- Customer ID: ...

# Goal
...

# Behavior
...
```

## Config (.env)

| Variable | Default |
|----------|---------|
| `ANTHROPIC_API_KEY` | required |
| `BANK_REP_BASE_URL` | `http://127.0.0.1:8000` |
| `MAX_TURNS` | `30` |
| `CUSTOMER_CONVERSATION_LOG` | `true` |

## Tests

```bash
uv run pytest
```
