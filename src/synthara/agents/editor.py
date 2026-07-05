from __future__ import annotations

from synthara.agents.base import Agent


class EditorAgent(Agent):
    def system_prompt(self) -> str:
        return """You are a senior editor. Review the following report and improve it:

1. Fix any grammatical errors or awkward phrasing
2. Ensure consistent tone and style throughout
3. Verify citations are properly formatted
4. Add a brief executive summary at the top
5. Return the FULL edited report

Do NOT change factual content or add new information not supported by the sources."""

    async def edit(self, report_content: str) -> str:
        return await self.run(f"Please edit the following report:\n\n{report_content}")
