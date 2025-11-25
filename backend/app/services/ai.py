from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import httpx
from openai import AsyncOpenAI
from ..config import settings
import json

class AIProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        pass

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.AI_API_KEY
        self.model = model or settings.AI_MODEL
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"}  # Force JSON
        )
        return response.choices[0].message.content


class GenericProvider(AIProvider):
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.base_url = (base_url or settings.AI_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.AI_API_KEY
        self.model = model or settings.AI_MODEL

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        # Assumes OpenAI-compatible endpoint (like Ollama or LocalAI)
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload, timeout=60.0)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]


class ChainedProvider(AIProvider):
    """
    Tries multiple underlying providers in order until one succeeds.
    """

    def __init__(self, providers: List[AIProvider]):
        self.providers = providers

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        last_error: Optional[Exception] = None
        for idx, provider in enumerate(self.providers):
            try:
                result = await provider.generate(prompt, system_prompt)
                if result and result.strip():
                    return result
            except Exception as e:
                print(f"AI provider #{idx + 1} failed: {e}")
                last_error = e
                continue

        # If everything failed, surface a minimal JSON object so callers don't crash.
        if last_error:
            print(f"All configured AI providers failed, returning empty JSON. Last error: {last_error}")
        return "{}"


def _build_provider(kind: str, api_key: str, model: str) -> Optional[AIProvider]:
    if not kind:
        return None
    if kind == "openai":
        if not api_key:
            return None
        return OpenAIProvider(api_key=api_key, model=model)
    if kind == "generic":
        if not settings.AI_BASE_URL:
            return None
        return GenericProvider(base_url=settings.AI_BASE_URL, api_key=api_key, model=model)
    return None


def get_ai_provider() -> AIProvider:
    """
    Returns a provider that may internally fall back to a secondary provider
    if the primary fails (e.g., due to quota limits).
    """
    providers: List[AIProvider] = []

    # Primary provider from core AI_* settings
    primary = _build_provider(settings.AI_PROVIDER, settings.AI_API_KEY, settings.AI_MODEL)
    if primary:
        providers.append(primary)

    # Optional fallback provider, typically pointing at a cheaper/free option
    if settings.AI_FALLBACK_PROVIDER:
        fb_api_key = settings.AI_FALLBACK_API_KEY or settings.AI_API_KEY
        fb_model = settings.AI_FALLBACK_MODEL or settings.AI_MODEL
        fallback = _build_provider(settings.AI_FALLBACK_PROVIDER, fb_api_key, fb_model)
        if fallback:
            providers.append(fallback)

    # If nothing was configured correctly, fall back to the legacy behavior.
    if not providers:
        if settings.AI_PROVIDER == "openai":
            providers.append(OpenAIProvider())
        else:
            providers.append(GenericProvider())

    if len(providers) == 1:
        return providers[0]
    return ChainedProvider(providers)


ai_provider = get_ai_provider()
