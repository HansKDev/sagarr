from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import httpx
from openai import AsyncOpenAI
from ..config import settings
import json

class AIProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        pass

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.AI_API_KEY)
        self.model = settings.AI_MODEL

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"} # Force JSON
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return "{}"

class GenericProvider(AIProvider):
    def __init__(self):
        self.base_url = settings.AI_BASE_URL
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL

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
            try:
                resp = await client.post(url, headers=headers, json=payload, timeout=60.0)
                resp.raise_for_status()
                data = resp.json()
                return data['choices'][0]['message']['content']
            except Exception as e:
                print(f"Generic AI Error: {e}")
                return "{}"

def get_ai_provider() -> AIProvider:
    if settings.AI_PROVIDER == "openai":
        return OpenAIProvider()
    else:
        return GenericProvider()

ai_provider = get_ai_provider()
