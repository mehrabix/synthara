# Synthara

**Multi-Agent AI Research & Content Platform** — Orchestrates free OpenRouter models through a team of specialized AI agents to research topics and generate polished reports.

## Quick Start

```bash
pip install -e ".[dev]"
export OPENROUTER_API_KEY="sk-or-v1-..."
synthara research "Quantum computing breakthroughs 2025"
```

## Architecture

Four specialized agents collaborate on every task:

1. **Planner** — decomposes your query into a structured research plan
2. **Researcher** — gathers information via web search and summarizes sources
3. **Writer** — synthesizes findings into well-structured sections
4. **Editor** — polishes prose, checks facts, adds citations

See [MASTERPLAN.md](MASTERPLAN.md) for the full architecture.

## Models

Configure any OpenRouter model in `config.toml`. Free-tier defaults:
- `mistralai/mistral-7b-instruct`
- `meta-llama/llama-3-8b-instruct`
- `google/gemini-flash-1.5`

## License

MIT
