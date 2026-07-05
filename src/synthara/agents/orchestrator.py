from __future__ import annotations

import asyncio
import uuid

from synthara.agents.editor import EditorAgent
from synthara.agents.planner import PlannerAgent
from synthara.agents.researcher import ResearcherAgent
from synthara.agents.writer import WriterAgent
from synthara.core.config import AppConfig
from synthara.core.llm import LLMClient
from synthara.core.models import (
    Message,
    Report,
    ReportSection,
    ResearchFindings,
    Session,
    Source,
)
from synthara.memory.store import MemoryStore


class Orchestrator:
    def __init__(
        self,
        config: AppConfig,
        llm: LLMClient,
        memory: MemoryStore,
        renderer=None,
    ):
        self.config = config
        self.llm = llm
        self.memory = memory
        self.renderer = renderer

        self.planner = PlannerAgent("planner", config.agents.planner_model, llm)
        self.researcher = ResearcherAgent(
            "researcher",
            config.agents.researcher_model,
            llm,
            max_sources=config.research.max_sources_per_query,
        )
        self.writer = WriterAgent("writer", config.agents.writer_model, llm)
        self.editor = EditorAgent("editor", config.agents.editor_model, llm)

    async def run(self, query: str) -> Report:
        session = Session(id=uuid.uuid4().hex[:8], query=query)
        session.messages.append(Message(role="user", content=query))
        self.memory.save_session(session)

        if self.renderer:
            self.renderer.show_step("Planning", "Decomposing research query...")

        research_plan = await self.planner.plan(query)

        if self.renderer:
            self.renderer.show_plan(research_plan)
            self.renderer.show_step("Research", f"Investigating {len(research_plan)} subtopics...")

        research_tasks = [self.researcher.research(q) for q in research_plan]
        findings_list: list[ResearchFindings] = await asyncio.gather(*research_tasks)

        all_sources: list[Source] = []
        for f in findings_list:
            all_sources.extend(f.sources)

        if self.renderer:
            self.renderer.show_step("Writing", "Synthesizing findings into report...")

        section_tasks = []
        for finding in findings_list:
            sources_context = self._format_sources_for_writer(finding.sources)
            title = finding.sub_question
            section_tasks.append(
                self.writer.write_section(title, finding.summary, sources_context)
            )

        section_contents = await asyncio.gather(*section_tasks)

        sections = []
        for finding, content in zip(findings_list, section_contents):
            sections.append(
                ReportSection(
                    title=finding.sub_question,
                    content=content,
                    sources=finding.sources,
                )
            )

        draft_content = "\n\n".join(s.content for s in sections)

        if self.renderer:
            self.renderer.show_step("Editing", "Polishing and reviewing...")

        final_content = await self.editor.edit(draft_content)

        report = Report(
            query=query,
            sections=sections,
            content=final_content,
            sources=all_sources,
        )

        session.report = report
        session.messages.append(Message(role="assistant", content=final_content))
        self.memory.save_session(session)

        return report

    def _format_sources_for_writer(self, sources: list[Source]) -> str:
        return "\n".join(
            f"[{i}] {s.title} — {s.url}" for i, s in enumerate(sources, 1)
        )
