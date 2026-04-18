import logging
from typing import AsyncIterator, Protocol

import groq
import openai

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> str: ...

    async def classify(
        self,
        system_prompt: str,
        user_input: str,
    ) -> str: ...

    async def stream_chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> AsyncIterator[str]: ...


class GroqProvider:
    """Free, fast inference using open-source models (Llama 3, Mixtral, etc.)."""

    def __init__(self):
        settings = get_settings()
        self.client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return (response.choices[0].message.content or "").strip()

    async def classify(
        self,
        system_prompt: str,
        user_input: str,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.0,
        )
        return (response.choices[0].message.content or "").strip().lower()

    async def extract(
        self,
        system_prompt: str,
        user_input: str,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.0,
        )
        return (response.choices[0].message.content or "").strip()

    async def stream_chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class OpenAIProvider:
    def __init__(self):
        settings = get_settings()
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return (response.choices[0].message.content or "").strip()

    async def classify(
        self,
        system_prompt: str,
        user_input: str,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.0,
        )
        return (response.choices[0].message.content or "").strip().lower()

    async def extract(
        self,
        system_prompt: str,
        user_input: str,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.0,
        )
        return (response.choices[0].message.content or "").strip()

    async def stream_chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


_provider: LLMProvider | None = None


def get_llm() -> GroqProvider | OpenAIProvider:
    global _provider
    if _provider is None:
        settings = get_settings()
        if settings.LLM_PROVIDER == "openai":
            logger.info("Using OpenAI provider (%s)", settings.OPENAI_MODEL)
            _provider = OpenAIProvider()
        else:
            logger.info("Using Groq provider (%s)", settings.GROQ_MODEL)
            _provider = GroqProvider()
    return _provider
