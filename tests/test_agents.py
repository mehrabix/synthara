from __future__ import annotations

import pytest

from synthara.core.config import AppConfig, LLMConfig
from synthara.core.models import ResearchFindings, Source


class MockLLM:
    def __init__(self, responses: list[str] | None = None):
        self.responses = responses or ["Mock response"]
        self.call_index = 0

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048, **kwargs):
        response = self.responses[self.call_index % len(self.responses)]
        self.call_index += 1
        return response


def test_planner_parses_sub_questions():
    from synthara.agents.planner import PlannerAgent

    mock_llm = MockLLM(responses=[
        "1. What are the key breakthroughs in quantum computing?\n"
        "2. Which companies are leading quantum computing research?\n"
        "3. What are the main challenges facing quantum computing?"
    ])
    config = AppConfig()
    agent = PlannerAgent("planner", config.agents.planner_model, mock_llm)
    questions = agent.plan("Quantum computing")
    assert len(questions) == 3
    assert "breakthroughs" in questions[0].lower()


@pytest.mark.asyncio
async def test_researcher_creates_findings():
    from synthara.agents.researcher import ResearcherAgent

    config = AppConfig()
    mock_llm = MockLLM(responses=["Quantum computing uses qubits."])
    agent = ResearcherAgent("researcher", config.agents.researcher_model, mock_llm, max_sources=2)

    findings = await agent.research("What is quantum computing?")
    assert isinstance(findings, ResearchFindings)
    assert findings.sub_question == "What is quantum computing?"


@pytest.mark.asyncio
async def test_writer_creates_content():
    from synthara.agents.writer import WriterAgent

    config = AppConfig()
    mock_llm = MockLLM(responses=["## Introduction\nQuantum computing is..."])
    agent = WriterAgent("writer", config.agents.writer_model, mock_llm)

    content = await agent.write_section(
        "Introduction", "Quantum computing uses qubits.", "[1] Source"
    )
    assert "Quantum" in content


@pytest.mark.asyncio
async def test_editor_polishes_content():
    from synthara.agents.editor import EditorAgent

    config = AppConfig()
    mock_llm = MockLLM(responses=["## Summary\nQuantum computing advances rapidly."])
    agent = EditorAgent("editor", config.agents.editor_model, mock_llm)

    edited = await agent.edit("Quantum computing advances.")
    assert "Summary" in edited


def test_config_loading(tmp_path):
    config_content = """
[llm]
models = ["test-model"]
max_retries = 5

[agents]
planner_model = "test-planner"
"""
    config_file = tmp_path / "config.toml"
    config_file.write_text(config_content)

    from synthara.core.config import load_config
    config = load_config(str(config_file))
    assert config.llm.models == ["test-model"]
    assert config.llm.max_retries == 5
    assert config.agents.planner_model == "test-planner"


@pytest.mark.asyncio
async def test_llm_client_retry_on_failure():
    from synthara.core.llm import LLMClient

    config = LLMConfig(models=["test-model"])
    # Key error expected — no API key set
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        LLMClient(config)
