from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

import requests


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "domain"))
sys.path.insert(0, str(ROOT / "django_app"))

from fmea_ai.contracts import AiTaskRequest  # noqa: E402
from fmea_ai.providers.disabled_provider import DisabledProvider  # noqa: E402
from fmea_ai.providers.ollama_provider import OllamaProvider  # noqa: E402


class AiProviderTests(unittest.TestCase):
    def test_disabled_provider_returns_unavailable_for_every_task(self):
        provider = DisabledProvider()
        task_names = (
            "extract_structured_data",
            "classify_characteristic",
            "classify_ishikawa_category",
            "suggest_relationships",
            "retrieve_similar_cases",
            "summarize_evidence",
        )

        for task_name in task_names:
            request = _request(task_name)
            response = getattr(provider, task_name)(request)
            self.assertEqual(response.status, "unavailable")
            self.assertIsNone(response.structured_output)
            self.assertEqual(response.raw_provider_name, "disabled")

    def test_ollama_extract_structured_data_validates_json_response(self):
        session = Mock()
        session.get.return_value = _response({})
        session.post.return_value = _response(
            {
                "response": json.dumps(
                    {
                        "extracted_value": "Seal leaks",
                        "suggested_domain_type": "FailureMode",
                    }
                )
            }
        )
        provider = OllamaProvider(
            enabled=True,
            endpoint="http://127.0.0.1:11434",
            model="local-test",
            timeout=1,
            session=session,
        )

        response = provider.extract_structured_data(_request("extract_structured_data"))

        self.assertEqual(response.status, "ok")
        self.assertEqual(response.structured_output["extracted_value"], "Seal leaks")
        session.get.assert_called_once()
        session.post.assert_called_once()

    def test_ollama_timeout_stays_inside_provider_boundary(self):
        session = Mock()
        session.post.side_effect = requests.exceptions.Timeout()
        provider = OllamaProvider(
            enabled=True,
            endpoint="http://127.0.0.1:11434",
            model="local-test",
            timeout=1,
            session=session,
        )
        provider._health_checked = True
        provider._healthy = True

        response = provider.extract_structured_data(_request("extract_structured_data"))

        self.assertEqual(response.status, "timeout")

    def test_ollama_classification_methods_are_unavailable_in_this_slice(self):
        provider = OllamaProvider(enabled=True, model="local-test")

        self.assertEqual(
            provider.classify_characteristic(_request("classify_characteristic")).status,
            "unavailable",
        )
        self.assertEqual(
            provider.classify_ishikawa_category(_request("classify_ishikawa_category")).status,
            "unavailable",
        )


def _request(task: str) -> AiTaskRequest:
    return AiTaskRequest(
        task=task,  # type: ignore[arg-type]
        input_text="Seal leaks",
        context={"column_name": "Failure Mode"},
        output_schema={
            "type": "object",
            "properties": {
                "extracted_value": {"type": "string"},
                "suggested_domain_type": {"type": "string"},
            },
            "required": ["extracted_value", "suggested_domain_type"],
            "additionalProperties": False,
        },
    )


def _response(payload: dict):
    response = Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


if __name__ == "__main__":
    unittest.main()
