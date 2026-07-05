from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from synthara.core.models import Report


class CLIRenderer:
    def __init__(self):
        self.console = Console()

    def show_welcome(self):
        title = Text("Synthara", style="bold cyan")
        subtitle = Text("Multi-Agent AI Research Platform", style="dim")
        self.console.print(Panel(f"{title}\n{subtitle}", border_style="cyan"))
        self.console.print()

    def show_query(self, query: str):
        self.console.print(Rule(style="dim"))
        self.console.print(f"[bold]Research Query:[/] {query}")
        self.console.print()

    def show_step(self, step: str, description: str):
        self.console.print(f"[bold yellow]⏳ {step}:[/] {description}")

    def show_plan(self, sub_questions: list[str]):
        self.console.print("\n[bold cyan]Research Plan:[/]")
        table = Table(show_header=False, box=None)
        for i, q in enumerate(sub_questions, 1):
            table.add_row(f"  {i}.", q)
        self.console.print(table)
        self.console.print()

    def show_report(self, report: Report):
        self.console.print(Rule(style="green"))
        self.console.print(f"\n[bold green]📄 Report:[/] {report.query}\n")
        self.console.print(Markdown(report.content))
        self.console.print()

        if report.sources:
            self.console.print(Rule(style="dim"))
            self.console.print("\n[bold]Sources:[/]")
            for i, src in enumerate(report.sources, 1):
                self.console.print(f"  [{i}] [link={src.url}]{src.title}[/]")

    def show_saved(self, path: Path):
        self.console.print(f"\n[bold green]✓ Report saved to:[/] {path}")
