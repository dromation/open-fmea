from __future__ import annotations

from fmea_ai.contracts import AiTaskRequest, AiTaskResponse


class DisabledProvider:
    raw_provider_name = "disabled"

    def extract_structured_data(self, request: AiTaskRequest) -> AiTaskResponse:
        return self._unavailable(request)

    def classify_characteristic(self, request: AiTaskRequest) -> AiTaskResponse:
        return self._unavailable(request)

    def classify_ishikawa_category(self, request: AiTaskRequest) -> AiTaskResponse:
        return self._unavailable(request)

    def suggest_relationships(self, request: AiTaskRequest) -> AiTaskResponse:
        return self._unavailable(request)

    def retrieve_similar_cases(self, request: AiTaskRequest) -> AiTaskResponse:
        return self._unavailable(request)

    def summarize_evidence(self, request: AiTaskRequest) -> AiTaskResponse:
        return self._unavailable(request)

    def _unavailable(self, request: AiTaskRequest) -> AiTaskResponse:
        return AiTaskResponse(
            task=request.task,
            status="unavailable",
            structured_output=None,
            raw_provider_name=self.raw_provider_name,
            raw_model_name=None,
            model_confidence=None,
            latency_ms=None,
        )
