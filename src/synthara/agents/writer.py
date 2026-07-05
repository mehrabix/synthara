from __future__ import annotations

from synthara.agents.base import Agent


class WriterAgent(Agent):
    def system_prompt(self) -> str:
        return (
            "You are a technical writer. Given a collection of research summaries "
            "on subtopics, produce a well-structured, engaging section for each. "
            "Write in a clear, professional style suitable for a blog post or report.\n\n"
            "For each section:\n"
            "- Start with a heading (## Title)\n"
            "- Write 2-4 paragraphs synthesizing the information\n"
            "- Cite sources using [1], [2] notation\n"
            "- Connect ideas across subtopics where relevant\n\n"
            "Return the complete report in Markdown format."
        )

    async def write_section(self, title: str, summary: str, sources_context: str) -> str:
        prompt = (
            f"Write a section titled '{title}' based on this research:\n\n"
            f"{summary}\n\nSources:\n{sources_context}"
        )
        return await self.run(prompt)
