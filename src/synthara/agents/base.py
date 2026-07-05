from __future__ import annotations

from abc import ABC, abstractmethod

from synthara.core.llm import LLMClient


class Agent(ABC):
    def __init__(self, name: str, model: str, llm: LLMClient):
        self.name = name
        self.model = model
        self.llm = llm

    @abstractmethod
    def system_prompt(self) -> str:
        ...

    async def run(self, input_text: str, context: str | None = None) -> str:
        messages = [{"role": "system", "content": self.system_prompt()}]
        if context:
            messages.append({"role": "system", "content": f"Context:\n{context}"})
        messages.append({"role": "user", "content": input_text})
        return await self.llm.chat(messages, model=self.model)
