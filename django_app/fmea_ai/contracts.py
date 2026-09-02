"""Provider-neutral AI contract for local Open-FMEA assistance."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol


AiTaskName = Literal[
    "extract_structured_data",
    "classify_characteristic",
    "classify_ishikawa_category",
    "suggest_relationships",
    "retrieve_similar_cases",
    "summarize_evidence",
]
AiTaskStatus = Literal["ok", "unavailable", "invalid_output", "timeout", "error"]


@dataclass(frozen=True, kw_only=True)
class AiTaskRequest:
    task: AiTaskName
    input_text: str
    context: dict[str, Any]
    output_schema: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.task:
            raise ValueError("task is required")
        if not isinstance(self.context, dict):
            raise ValueError("context must be a dict")
        if not isinstance(self.output_schema, dict):
            raise ValueError("output_schema must be a dict")


@dataclass(frozen=True, kw_only=True)
class AiTaskResponse:
    task: str
    status: AiTaskStatus
    structured_output: dict[str, Any] | None
    raw_provider_name: str
    raw_model_name: str | None
    model_confidence: float | None
    latency_ms: int | None

    def __post_init__(self) -> None:
        if not self.task.strip():
            raise ValueError("task is required")
        if not self.raw_provider_name.strip():
            raise ValueError("raw_provider_name is required")
        if self.model_confidence is not None and (
            self.model_confidence < 0 or self.model_confidence > 1
        ):
            raise ValueError("model_confidence must be between 0 and 1")
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("latency_ms must be >= 0")


class AiProvider(Protocol):
    def extract_structured_data(self, request: AiTaskRequest) -> AiTaskResponse:
        ...

    def classify_characteristic(self, request: AiTaskRequest) -> AiTaskResponse:
        ...

    def classify_ishikawa_category(self, request: AiTaskRequest) -> AiTaskResponse:
        ...

    def suggest_relationships(self, request: AiTaskRequest) -> AiTaskResponse:
        ...

    def retrieve_similar_cases(self, request: AiTaskRequest) -> AiTaskResponse:
        ...

    def summarize_evidence(self, request: AiTaskRequest) -> AiTaskResponse:
        ...
