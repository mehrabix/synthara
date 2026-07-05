from __future__ import annotations

import asyncio

from ddgs import DDGS

from synthara.agents.base import Agent
from synthara.core.llm import LLMClient
from synthara.core.models import ResearchFindings, Source


class ResearcherAgent(Agent):
    def __init__(self, name: str, model: str, llm: LLMClient, max_sources: int = 5):
        super().__init__(name, model, llm)
        self.max_sources = max_sources

    def system_prompt(self) -> str:
        return (
            "You are a research analyst. Given a question and search results, "
            "produce a concise, factual summary covering the key points. "
            "Cite sources by index [1], [2], etc. "
            "Be objective and note any conflicting information."
        )

    async def research(self, sub_question: str) -> ResearchFindings:
        sources = await self._search(sub_question)
        if not sources:
            return ResearchFindings(
                sub_question=sub_question,
                sources=[],
                summary="No sources found for this question.",
            )

        context = self._format_sources(sources)
        summary = await self.run(
            input_text=f"Research question: {sub_question}\n\nSources:\n{context}",
        )

        return ResearchFindings(
            sub_question=sub_question,
            sources=sources,
            summary=summary,
        )

    async def _search(self, query: str) -> list[Source]:
        loop = asyncio.get_event_loop()

        def _sync_search():
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=self.max_sources))
                    return [
                        Source(
                            title=r.get("title", ""),
                            url=r.get("href", ""),
                            snippet=r.get("body", ""),
                        )
                        for r in results
                    ]
            except Exception:
                return []

        return await loop.run_in_executor(None, _sync_search)

    def _format_sources(self, sources: list[Source]) -> str:
        lines = []
        for i, src in enumerate(sources, 1):
            lines.append(f"[{i}] {src.title}\n    URL: {src.url}\n    {src.snippet}\n")
        return "\n".join(lines)

