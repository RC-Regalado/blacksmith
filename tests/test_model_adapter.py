"""Tests for model adapter provider selection."""

import unittest

from ai_assistant.agent.message import Message
from ai_assistant.agent.models.adapter import ModelAdapter, ModelAdapterConfig
from ai_assistant.agent.models.openai_compatible import OpenAICompatibleModel


class ModelAdapterTests(unittest.TestCase):
    def test_dummy_provider_delegates_to_dummy_model(self) -> None:
        adapter = ModelAdapter.from_config(ModelAdapterConfig(provider="dummy"))

        response = adapter.chat([Message(role="user", content="hola")])

        self.assertEqual(adapter.provider_name, "dummy")
        self.assertEqual(response, Message(role="assistant", content="Echo: hola"))

    def test_openai_provider_can_be_constructed_without_api_key(self) -> None:
        adapter = ModelAdapter.from_config(ModelAdapterConfig(provider="openai"))

        self.assertEqual(adapter.provider_name, "openai")

    def test_unknown_provider_fails_explicitly(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported model provider"):
            ModelAdapter.from_config(ModelAdapterConfig(provider="unknown"))


class OpenAICompatibleModelTests(unittest.TestCase):
    def test_build_payload_separates_system_instructions(self) -> None:
        model = OpenAICompatibleModel(model="gpt-5", api_key="test-key")

        payload = model._build_payload(
            [
                Message(role="system", content="Sistema"),
                Message(role="user", content="Hola"),
            ]
        )

        self.assertEqual(payload["instructions"], "Sistema")
        self.assertEqual(payload["input"][0]["role"], "user")
        self.assertEqual(payload["input"][0]["content"], "Hola")

    def test_extract_text_reads_responses_output(self) -> None:
        model = OpenAICompatibleModel(model="gpt-5", api_key="test-key")

        text = model._extract_text(
            {
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "Listo"}],
                    }
                ]
            }
        )

        self.assertEqual(text, "Listo")


if __name__ == "__main__":
    unittest.main()
