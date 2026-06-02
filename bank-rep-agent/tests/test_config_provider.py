import importlib

import bank_demo.config as config


def test_get_llm_provider_defaults_to_anthropic(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert config.get_llm_provider() == "anthropic"


def test_get_llm_provider_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    assert config.get_llm_provider() == "openai"


def test_get_llm_provider_invalid_falls_back(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "something-else")
    assert config.get_llm_provider() == "anthropic"


def test_get_openai_api_key_placeholder_returns_none(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "your_openai_api_key_here")
    assert config.get_openai_api_key() is None


def test_get_openai_model_default(monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    assert config.get_openai_model() == "gpt-4o-mini"
