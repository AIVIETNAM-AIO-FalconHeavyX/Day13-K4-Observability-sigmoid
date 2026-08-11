from __future__ import annotations

import time
from dataclasses import dataclass

from . import metrics
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .prompt_management import resolve_prompt
from .tracing import get_langfuse_client, observe, tracing_enabled


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    @observe(name="chat-response", as_type="span", capture_input=False, capture_output=False)
    def run(self, user_id: str, feature: str, session_id: str, message: str) -> AgentResult:
        started = time.perf_counter()
        docs = self._retrieve_context(message)
        langfuse_client = get_langfuse_client()
        prompt = resolve_prompt(
            langfuse_client,
            feature=feature,
            docs=docs,
            message=message,
            enabled=tracing_enabled(),
        )
        response = self._generate_response(prompt, message=message, docs=docs)
        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        cost_usd = self._estimate_cost(response.usage.input_tokens, response.usage.output_tokens)

        langfuse_client.update_current_trace(
            user_id=hash_user_id(user_id),
            session_id=session_id,
            tags=["lab", feature, self.model],
            metadata={
                "prompt_name": prompt.name,
                "prompt_label": prompt.label,
                "prompt_version": prompt.version,
                "prompt_source": prompt.source,
            },
        )
        # Keep the trace-level payload useful without storing raw request arguments.
        update_span = getattr(langfuse_client, "update_current_span", None)
        if update_span is not None:
            update_span(
                input={"message": summarize_text(message)},
                output={"answer": summarize_text(response.text)},
                metadata={"feature": feature, "session_id": session_id},
            )
        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            quality_score=quality_score,
        )

        return AgentResult(
            answer=response.text,
            latency_ms=latency_ms,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            cost_usd=cost_usd,
            quality_score=quality_score,
        )

    @observe(name="retrieve-context", as_type="retriever", capture_input=False, capture_output=False)
    def _retrieve_context(self, message: str) -> list[str]:
        docs = retrieve(message)
        client = get_langfuse_client()
        update_span = getattr(client, "update_current_span", None)
        if update_span is not None:
            update_span(
                input={"query": summarize_text(message)},
                output={"documents": docs},
                metadata={"doc_count": len(docs)},
            )
        return docs

    @observe(name="generate-response", as_type="generation", capture_input=False, capture_output=False)
    def _generate_response(self, prompt, *, message: str, docs: list[str]):
        response = self.llm.generate(prompt.text)
        cost_usd = self._estimate_cost(
            response.usage.input_tokens, response.usage.output_tokens
        )
        get_langfuse_client().update_current_generation(
            model=self.model,
            output=summarize_text(response.text),
            metadata={
                "doc_count": len(docs),
                "query_preview": summarize_text(message),
                "prompt_name": prompt.name,
                "prompt_label": prompt.label,
                "prompt_version": prompt.version,
                "prompt_source": prompt.source,
                "prompt_fetch_error": prompt.fetch_error,
            },
            usage_details={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
            },
            cost_details={"total": cost_usd},
            prompt=prompt.managed_prompt,
        )
        return response

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(token in answer.lower() for token in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
