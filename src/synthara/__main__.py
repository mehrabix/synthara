import asyncio
from pathlib import Path

import typer

from synthara.core.config import load_config
from synthara.core.llm import LLMClient
from synthara.memory.store import MemoryStore
from synthara.agents.orchestrator import Orchestrator
from synthara.ui.cli import CLIRenderer

app = typer.Typer(
    name="synthara",
    help="Multi-agent AI research & content platform",
    no_args_is_help=True,
)


@app.command()
def research(
    query: str = typer.Argument(..., help="Research topic or question"),
    output: Path = typer.Option(None, "--output", "-o", help="Save report to file"),
    model: str = typer.Option(None, "--model", "-m", help="Override model for all agents"),
):
    asyncio.run(_run_research(query, output, model))


async def _run_research(query: str, output: Path | None, model: str | None):
    config = load_config()
    if model:
        for agent_name in ["planner", "researcher", "writer", "editor"]:
            setattr(config.agents, f"{agent_name}_model", model)

    llm = LLMClient(config)
    memory = MemoryStore(config.memory.db_path)
    renderer = CLIRenderer()

    orchestrator = Orchestrator(config=config, llm=llm, memory=memory, renderer=renderer)

    renderer.show_welcome()
    renderer.show_query(query)

    report = await orchestrator.run(query)

    renderer.show_report(report)

    if output:
        output.write_text(report.content)
        renderer.show_saved(output)

    memory.close()


if __name__ == "__main__":
    app()
