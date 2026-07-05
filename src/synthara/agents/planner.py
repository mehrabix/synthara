from __future__ import annotations

from synthara.agents.base import Agent


class PlannerAgent(Agent):
    def system_prompt(self) -> str:
        return """You are a research planning expert. Your job is to decompose a user's research query into 3-6 specific, focused sub-questions that will help build a comprehensive report.

Rules:
- Break the main topic into logical subtopics
- Each sub-question should be specific and answerable
- Cover different angles: background, current state, key players, challenges, future outlook
- Return ONLY a numbered list of sub-questions, one per line
- No explanations, no preamble"""

    async def plan(self, query: str) -> list[str]:
        response = await self.run(query)
        questions = [
            line.strip().lstrip("0123456789.-) ").strip()
            for line in response.strip().split("\n")
            if line.strip()
        ]
        return [q for q in questions if q and "?" in q][:6]
