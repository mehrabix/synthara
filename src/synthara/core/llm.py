from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, AsyncIterator

import httpx

from synthara.core.config import AppConfig, ProviderConfig

logger = logging.getLogger(__name__)


class ProviderClient:
    """HTTP client for a single LLM provider."""

    def __init__(self, name: str, config: ProviderConfig, timeout: int = 60):
        self.name = name
        self.config = config
        self._client = httpx.AsyncClient(
            base_url=config.resolve_base_url(),
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }
        response = await self._client.post("/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def close(self):
        await self._client.aclose()


class MultiProviderRouter:
    """Routes requests across multiple providers with automatic failover.

    Tries providers in priority order. On 429 / timeout / server error,
    falls back to the next available provider seamlessly.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self._providers: dict[str, ProviderClient] = {}
        self._provider_order: list[str] = []
        self._round_robin_index = 0
        self._init_providers()

    def _init_providers(self):
        for name, pconfig in self.config.llm.active_providers():
            self._providers[name] = ProviderClient(
                name, pconfig, timeout=self.config.llm.request_timeout
            )
            self._provider_order.append(name)

        if not self._providers:
            logger.warning(
                "No LLM providers configured with API keys. "
                "Set at least one: OPENROUTER_API_KEY, GROQ_API_KEY, GEMINI_API_KEY, etc."
            )

    def _resolve_model(self, model_spec: str) -> tuple[str, str | None]:
        """If model is 'provider/model', split and return (model, provider_hint)."""
        if "/" in model_spec and not model_spec.startswith("@") and not model_spec.startswith("hf:"):
            parts = model_spec.split("/", 1)
            if parts[0] in self._providers:
                return parts[1], parts[0]
        return model_spec, None

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        if not self._providers:
            raise RuntimeError(
                "No LLM providers configured. Set at least one API key env var."
            )

        resolved_model, provider_hint = self._resolve_model(model or "")

        if provider_hint and provider_hint in self._providers:
            candidates = [provider_hint]
        else:
            candidates = self._get_routing_order()

        last_error: Exception | None = None
        for provider_name in candidates:
            provider = self._providers.get(provider_name)
            if not provider:
                continue

            effective_model = resolved_model or provider.config.models[0]

            for attempt in range(self.config.llm.max_retries + 1):
                try:
                    result = await provider.chat(
                        messages,
                        model=effective_model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs,
                    )
                    return result

                except httpx.HTTPStatusError as e:
                    last_error = e
                    if e.response.status_code == 429:
                        logger.info(
                            "Rate limited on %s/%s, trying next provider...",
                            provider_name, effective_model,
                        )
                        await asyncio.sleep(0.5)
                        break  # try next provider
                    elif e.response.status_code >= 500 and attempt < self.config.llm.max_retries:
                        logger.info("Server error on %s, retrying...", provider_name)
                        await asyncio.sleep(1)
                        continue
                    else:
                        logger.warning(
                            "HTTP %d on %s: %s",
                            e.response.status_code, provider_name, e.response.text[:200],
                        )
                        break  # try next provider

                except httpx.TimeoutException:
                    last_error = TimeoutError(f"Timeout on {provider_name}")
                    logger.info("Timeout on %s, trying next provider...", provider_name)
                    break

                except httpx.RequestError as e:
                    last_error = e
                    logger.warning("Connection error on %s: %s", provider_name, e)
                    break

        raise RuntimeError(
            f"All providers exhausted. Last error: {last_error}"
        ) from last_error

    def _get_routing_order(self) -> list[str]:
        if self.config.llm.routing_strategy == "round_robin":
            idx = self._round_robin_index
            self._round_robin_index = (idx + 1) % len(self._provider_order)
            return self._provider_order[idx:] + self._provider_order[:idx]
        return self._provider_order  # priority order

    async def close(self):
        for provider in self._providers.values():
            await provider.close()


class LLMClient:
    """Backward-compatible wrapper for single-provider use."""

    def __init__(self, config: AppConfig):
        self.router = MultiProviderRouter(config)

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        return await self.router.chat(messages, model, temperature, max_tokens, **kwargs)

    async def close(self):
        await self.router.close()
