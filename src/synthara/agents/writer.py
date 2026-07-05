from __future__ import annotations

from synthara.agents.base import Agent


class WriterAgent(Agent):
    def system_prompt(self) -> str:
        return """You are a technical writer. Given a collection of research summaries on subtopics, produce a well-structured, engaging section for each. Write in a clear, professional style suitable for a blog post or report.

For each section:
- Start with a heading (## Title)
- Write 2-4 paragraphs synthesizing the information
- Cite sources using [1], [2] notation
- Connect ideas across subtopics where relevant

Return the complete report in Markdown format."""

    async def write_section(self, title: str, summary: str, sources_context: str) -> str:
        prompt = f"Write a section titled '{title}' based on this research:\n\n{summary}\n\nSources:\n{sources_context}"
        return await self.run(prompt)
