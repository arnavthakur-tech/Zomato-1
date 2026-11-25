"""Groq chat-completion client with timeouts and basic retries."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from groq import APIConnectionError, APIStatusError, APITimeoutError, Groq, RateLimitError

from src.config import get_settings

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 45.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BASE_SECONDS = 1.0
# Retry these HTTP statuses; 401/403 fail fast (bad key / permissions).
RETRYABLE_STATUS_CODES = frozenset({408, 409, 429, 500, 502, 503, 504})


class LLMClientError(RuntimeError):
    """Raised when the Groq API call ultimately fails."""


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class LLMCompletion:
    content: str
    model: str
    latency_ms: float
    attempts: int


class GroqLLMClient:
    """Thin wrapper around the Groq chat completions API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        retry_base_seconds: float = DEFAULT_RETRY_BASE_SECONDS,
    ) -> None:
        settings = get_settings()
        key = (api_key if api_key is not None else settings.llm_api_key).strip()
        if not key:
            raise LLMClientError(
                "Missing Groq API key. Set LLM_API_KEY (or GROQ_API_KEY) in your .env file."
            )

        self.model = (model if model is not None else settings.llm_model).strip()
        if not self.model:
            raise LLMClientError("Missing LLM model name. Set LLM_MODEL in your .env file.")

        resolved_timeout = (
            settings.llm_timeout_seconds if timeout_seconds is None else timeout_seconds
        )
        resolved_retries = (
            settings.llm_max_retries if max_retries is None else max_retries
        )

        self.timeout_seconds = resolved_timeout
        self.max_retries = max(1, resolved_retries)
        self.retry_base_seconds = max(0.1, retry_base_seconds)
        self._client = Groq(api_key=key, timeout=resolved_timeout)

    def chat(
        self,
        messages: list[ChatMessage] | list[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> LLMCompletion:
        """Send a chat completion request with retry/backoff."""
        payload = [
            {"role": m.role, "content": m.content} if isinstance(m, ChatMessage) else m
            for m in messages
        ]
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            started = time.perf_counter()
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=payload,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                content = ""
                if response.choices:
                    content = (response.choices[0].message.content or "").strip()
                if not content:
                    raise LLMClientError("Groq returned an empty completion")

                latency_ms = (time.perf_counter() - started) * 1000
                return LLMCompletion(
                    content=content,
                    model=getattr(response, "model", None) or self.model,
                    latency_ms=latency_ms,
                    attempts=attempt,
                )
            except LLMClientError:
                raise
            except (APITimeoutError, APIConnectionError, RateLimitError) as exc:
                last_error = exc
                logger.warning(
                    "Groq attempt %s/%s failed (%s): %s",
                    attempt,
                    self.max_retries,
                    type(exc).__name__,
                    exc,
                )
            except APIStatusError as exc:
                last_error = exc
                status = getattr(exc, "status_code", None)
                if status not in RETRYABLE_STATUS_CODES:
                    raise LLMClientError(f"Groq API error ({status}): {exc}") from exc
                logger.warning(
                    "Groq attempt %s/%s failed with status %s: %s",
                    attempt,
                    self.max_retries,
                    status,
                    exc,
                )
            except Exception as exc:  # noqa: BLE001 — normalize provider errors
                last_error = exc
                logger.warning(
                    "Groq attempt %s/%s unexpected error (%s): %s",
                    attempt,
                    self.max_retries,
                    type(exc).__name__,
                    exc,
                )

            if attempt < self.max_retries:
                sleep_for = self.retry_base_seconds * (2 ** (attempt - 1))
                time.sleep(sleep_for)

        raise LLMClientError(
            f"Groq request failed after {self.max_retries} attempts: {last_error}"
        ) from last_error


def get_llm_client(**kwargs: object) -> GroqLLMClient:
    """Factory that reads defaults from settings."""
    return GroqLLMClient(**kwargs)  # type: ignore[arg-type]
