"""Integration tests that call the real OpenRouter API.

These tests require OPENROUTER_API_KEY environment variable to be set.
Marked with @pytest.mark.integration — excluded from default `pytest` run.
Run with: pytest -m integration
"""

from __future__ import annotations

import asyncio
import os

import pytest

from synthara.core.config import load_config
from synthara.core.llm import LLMClient, MultiProviderRouter

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("OPENROUTER_API_KEY"),
        reason="OPENROUTER_API_KEY not set",
    ),
]


@pytest.fixture
def config():
    return load_config()


@pytest.fixture
async def client(config):
    c = LLMClient(config)
    yield c
    await c.close()


@pytest.fixture(autouse=True)
async def rate_limit_delay():
    """3s delay between tests to stay within OpenRouter free tier limits (~20 RPM)."""
    yield
    await asyncio.sleep(3.0)


# ── Provider Router ───────────────────────────────────────────────────


class TestRouter:
    @pytest.mark.asyncio
    async def test_router_initializes_with_openrouter(self, config):
        router = MultiProviderRouter(config)
        assert len(router._providers) >= 1
        assert "openrouter" in router._providers
        await router.close()

    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_basic_chat_completion(self, client):
        response = await client.chat(
            messages=[{"role": "user", "content": "Reply with just: OK"}],
            model="google/gemma-4-26b-a4b-it:free",
            temperature=0.1,
            max_tokens=10,
        )
        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.timeout(30)
    @pytest.mark.asyncio
    async def test_empty_messages_raises(self, client):
        with pytest.raises(Exception):
            await client.chat(messages=[], model="google/gemma-4-26b-a4b-it:free")


# ── Agents ─────────────────────────────────────────────────────────────


class TestAgents:
    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_planner_agent(self, config):
        from synthara.agents.planner import PlannerAgent

        llm = LLMClient(config)
        agent = PlannerAgent("planner", config.agents.planner_model, llm)
        try:
            questions = await agent.plan("What is Python programming?")
            assert len(questions) >= 2
            assert all("?" in q for q in questions)
        finally:
            await llm.close()

    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_writer_agent(self, config):
        from synthara.agents.writer import WriterAgent

        llm = LLMClient(config)
        agent = WriterAgent("writer", config.agents.writer_model, llm)
        try:
            content = await agent.write_section(
                "Python Overview",
                "Python is a high-level programming language created by Guido van Rossum.",
                "[1] python.org",
            )
            assert "#" in content or "Python" in content
            assert len(content) > 50
        finally:
            await llm.close()

    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_editor_agent(self, config):
        from synthara.agents.editor import EditorAgent

        llm = LLMClient(config)
        agent = EditorAgent("editor", config.agents.editor_model, llm)
        try:
            edited = await agent.edit(
                "Python is a language. It is used for web development."
            )
            assert len(edited) > 20
        finally:
            await llm.close()


# ── Memory (no API needed) ─────────────────────────────────────────────


class TestMemory:
    def test_save_and_retrieve_session(self):
        import tempfile

        from synthara.core.models import Message, Report, Session
        from synthara.memory.store import MemoryStore
        db = tempfile.mktemp(suffix=".db")
        store = MemoryStore(db)
        try:
            session = Session(id="test-1", query="test query")
            session.messages.append(Message(role="user", content="hello"))
            session.report = Report(query="test query", sections=[], content="test report")
            store.save_session(session)

            loaded = store.get_session("test-1")
            assert loaded is not None
            assert loaded.query == "test query"
            assert len(loaded.messages) == 1
            assert loaded.report is not None
            assert loaded.report.content == "test report"

            sessions = store.list_sessions()
            assert len(sessions) >= 1
        finally:
            store.close()
            os.remove(db)

    def test_get_nonexistent_session(self):
        import tempfile

        from synthara.memory.store import MemoryStore
        db = tempfile.mktemp(suffix=".db")
        store = MemoryStore(db)
        try:
            result = store.get_session("nonexistent")
            assert result is None
        finally:
            store.close()
            os.remove(db)


# ── Full Orchestrator E2E (slow, uses multiple API calls) ─────────────


@pytest.mark.slow
@pytest.mark.timeout(300)
@pytest.mark.asyncio
async def test_orchestrator_e2e():
    """End-to-end test of the full research pipeline.

    This test uses multiple API calls and is excluded from standard
    integration test runs. Run with: pytest -m "integration and slow"
    """
    import tempfile

    from synthara.agents.orchestrator import Orchestrator
    from synthara.memory.store import MemoryStore
    from synthara.ui.cli import CLIRenderer
    db = tempfile.mktemp(suffix=".db")

    config = load_config()
    llm = LLMClient(config)
    memory = MemoryStore(db)
    renderer = CLIRenderer()
    orchestrator = Orchestrator(config=config, llm=llm, memory=memory, renderer=renderer)

    try:
        report = await orchestrator.run("What is Python used for? (keep it very brief)")
        assert report is not None
        assert report.content is not None
        assert len(report.content) > 50
        assert "Python" in report.content
    finally:
        await llm.close()
        memory.close()
        os.remove(db)
