from pathlib import Path

import pytest

from bank_customer import config


def test_load_env_from_project_root(monkeypatch, tmp_path: Path):
    customer_root = tmp_path / "bank-customer-agent"
    customer_root.mkdir()
    env_file = customer_root / ".env"
    env_file.write_text(
        "ANTHROPIC_API_KEY=sk-test-key\nCLAUDE_MODEL=test-model\n"
        "BANK_REP_BASE_URL=http://example.test\n"
    )

    monkeypatch.setattr(config, "PROJECT_ROOT", customer_root)
    monkeypatch.setattr(config, "ENV_FILE", env_file)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("CLAUDE_MODEL", raising=False)
    monkeypatch.delenv("BANK_REP_BASE_URL", raising=False)

    config.load_env()

    assert config.get_anthropic_api_key() == "sk-test-key"
    assert config.get_claude_model() == "test-model"
    assert config.get_bank_rep_base_url() == "http://example.test"


def test_anthropic_key_error_message_when_env_missing(monkeypatch, tmp_path: Path):
    customer_root = tmp_path / "bank-customer-agent"
    customer_root.mkdir()
    env_file = customer_root / ".env"

    monkeypatch.setattr(config, "ENV_FILE", env_file)

    message = config.anthropic_key_error_message()
    assert "Missing `.env` file" in message
