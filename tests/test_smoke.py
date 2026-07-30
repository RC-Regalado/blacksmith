"""Lightweight smoke tests."""

import logging

import pytest

from ai_assistant.infrastructure.models.adapter import ModelAdapter, ModelAdapterConfig
from ai_assistant.bootstrap.config import load_app_config


pytestmark = pytest.mark.smoke


def test_model_and_context_are_environment_selected(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    config = load_app_config(
        {
            "AI_ASSISTANT_PROVIDER": "ollama",
            "AI_ASSISTANT_MODEL": "installed-gemma-q4",
            "AI_ASSISTANT_CONTEXT_LIMIT": "8192",
        }
    )

    ModelAdapter.from_config(
        ModelAdapterConfig(provider=config.provider, model=config.model)
    )

    assert config.model == "installed-gemma-q4"
    assert config.context_limit == 8192
    assert "provider=ollama model=installed-gemma-q4" in caplog.text
