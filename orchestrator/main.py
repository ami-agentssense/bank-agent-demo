from orchestrator.config import load_env
from orchestrator.cli import run_cli

load_env()

if __name__ == "__main__":
    raise SystemExit(run_cli())
