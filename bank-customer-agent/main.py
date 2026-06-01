from bank_customer.config import load_env
from bank_customer.cli import run_cli

load_env()

if __name__ == "__main__":
    raise SystemExit(run_cli())
