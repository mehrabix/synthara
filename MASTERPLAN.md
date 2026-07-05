# Synthara — Multi-Agent AI Research & Content Platform

## Vision

Synthara is an agentic AI system that orchestrates **free OpenRouter models** through a team of specialized agents to research any topic, synthesize findings, and produce polished, publication-ready reports. It demonstrates production-grade system design, LLM orchestration, prompt engineering, and full-stack AI development.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User Interface                     │
│          CLI (Rich)          Streamlit Dashboard     │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                 Orchestrator Agent                    │
│  ─ Routes tasks → manages workflow → collates output │
└──────┬──────────┬──────────┬──────────┬─────────────┘
       │          │          │          │
┌──────▼──┐ ┌─────▼────┐ ┌──▼──────┐ ┌▼──────────┐
│ Planner  │ │Researcher│ │  Writer  │ │  Editor   │
│ (decom-  │ │(web      │ │(generates│ │(polishes  │
│ pose     │ │ search,  │ │ sections,│ │ grammar,  │
│ task)    │ │summarize)│ │ articles)│ │style,cite)│
└──────────┘ └──────────┘ └──────────┘ └───────────┘
       │          │          │          │
       └──────────┴──────────┴──────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                    Core Layer                        │
│  LLM Router (OpenRouter free models)                 │
│  Web Search (DuckDuckGo, Wikipedia)                  │
│  Memory (SQLite conversation store)                  │
└─────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component           | Technology                                |
|---------------------|-------------------------------------------|
| Language            | Python 3.12+                              |
| LLM Providers       | 12+ free providers with auto-failover     |
| Agent Orchestration | Custom agent graph (no heavy framework)   |
| CLI                 | Rich (beautiful terminal formatting)      |
| Dashboard           | Streamlit                                 |
| Storage             | SQLite (via sqlite3)                      |
| Web Research        | duckduckgo_search + wikipedia-api         |
| Async               | httpx + asyncio (for parallel agents)     |
| Packaging           | uv / pip + pyproject.toml                 |

---

## Free LLM Providers (All Supported)

Synthara's `MultiProviderRouter` tries providers in priority order. If one rate-limits, times out, or errors, it automatically falls back to the next.

| # | Provider | Base URL | Free Models | Get Key | Priority |
|---|----------|----------|-------------|---------|----------|
| 1 | **OpenRouter** | `openrouter.ai/api/v1` | 28+ free (`:free`) models | [Get key](https://openrouter.ai/keys) | 1 |
| 2 | **Groq** | `api.groq.com/openai/v1` | Llama 3.3 70B, Llama 4, Qwen3 | [Get key](https://console.groq.com/keys) | 2 |
| 3 | **Cerebras** | `api.cerebras.ai/v1` | Llama 3.1 8B, Llama 3.3 70B | [Get key](https://cloud.cerebras.ai/) | 3 |
| 4 | **Google Gemini** | `generativelanguage.googleapis.com/v1beta/openai` | Gemini 2.5 Flash, 2.0 Flash | [Get key](https://aistudio.google.com/apikey) | 4 |
| 5 | **Mistral** | `api.mistral.ai/v1` | Mistral Small 3.1, Ministral 8B | [Get key](https://console.mistral.ai/) | 5 |
| 6 | **GitHub Models** | `models.github.ai/inference` | GPT-4o-mini, Llama 3.1 | [Get key](https://github.com/marketplace/models) | 6 |
| 7 | **Cloudflare** | `api.cloudflare.com/.../ai/v1` | Llama 3.3 70B, Mistral 7B | [Get key](https://dash.cloudflare.com) | 7 |
| 8 | **NVIDIA NIM** | `integrate.api.nvidia.com/v1` | Llama 3.3 70B, Nemotron | [Get key](https://build.nvidia.com) | 8 |
| 9 | **HuggingFace** | `router.huggingface.co/v1` | Llama 3.3, Qwen2.5 | [Get key](https://huggingface.co/settings/tokens) | 9 |
| 10 | **SambaNova** | `api.sambanova.ai/v1` | Llama 3.1 405B | [Get key](https://cloud.sambanova.ai) | 10 |
| 11 | **DeepSeek** | `api.deepseek.com` | DeepSeek Chat | [Get key](https://platform.deepseek.com) | 11 |
| 12 | **Cohere** | `api.cohere.com/v1` | Command R+ | [Get key](https://dashboard.cohere.com) | 12 |

**Need just one key to start.** Set `OPENROUTER_API_KEY` and you're live. Add more keys and the router auto-balances across them.

---

## Project Structure

```
synthara/
├── MASTERPLAN.md
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── config.toml                    # User-facing config (model choice, paths)
├── .opencode/
│   ├── skills/
│   │   └── synthara-dev.md        # opencode skill for dev workflow
│   └── mcp/
│       └── synthara.json          # MCP server config
├── src/
│   └── synthara/
│       ├── __init__.py
│       ├── __main__.py            # CLI entry point
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py          # Config loader
│       │   ├── llm.py             # OpenRouter client (async httpx)
│       │   └── models.py          # Pydantic data models
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py            # Abstract base agent
│       │   ├── planner.py         # Task decomposition
│       │   ├── researcher.py      # Web research + summarization
│       │   ├── writer.py          # Content generation
│       │   ├── editor.py          # Polish + fact-check
│       │   └── orchestrator.py    # Workflow orchestrator
│       ├── memory/
│       │   ├── __init__.py
│       │   └── store.py           # SQLite conversation store
│       └── ui/
│           ├── __init__.py
│           ├── cli.py             # Rich CLI renderer
│           └── dashboard.py       # Streamlit app
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   └── test_core.py
└── docs/
    └── api.md
```

---

## Implementation Phases

### Phase 1 — Foundation (Days 1-2)
- [x] Project scaffold + git init
- [ ] `pyproject.toml` + dependencies
- [ ] `config.py` — load config from TOML + env vars
- [ ] `models.py` — Pydantic models for agents, messages, reports
- [ ] `llm.py` — OpenRouter client with retry, rate limiting, streaming
- [ ] `store.py` — SQLite session + message persistence

### Phase 2 — Agent Core (Days 3-4)
- [ ] `base.py` — abstract agent with prompt template + LLM call
- [ ] `planner.py` — decomposes user query into research plan
- [ ] `researcher.py` — executes web searches, summarizes sources
- [ ] `writer.py` — generates structured sections from research
- [ ] `editor.py` — revises for clarity, consistency, citations
- [ ] `orchestrator.py` — runs agent DAG with error handling

### Phase 3 — Interfaces (Days 5-6)
- [ ] `cli.py` — Rich-powered interactive CLI
- [ ] `dashboard.py` — Streamlit UI with session history
- [ ] Report export (Markdown → PDF)

### Phase 4 — Polish (Day 7+)
- [ ] Tests for each agent
- [ ] Error handling + graceful degradation
- [ ] Prompt optimization per model
- [ ] GitHub Actions CI
- [ ] PyPI publish / Docker image

---

## Data Flow

```
User Input
    │
    ▼
┌─────────────┐
│  Orchestrator │  receives task, initializes session in DB
└──────┬───────┘
       │
┌──────▼───────┐
│   Planner    │  "Research quantum computing advances in 2025"
│              │  → [sub-question 1, sub-q 2, ..., sub-q N]
└──────┬───────┘
       │ (parallel)
┌──────▼───────┐
│  Researcher  │  for each sub-question:
│              │  → DuckDuckGo search → scrape snippets → LLM summarize
└──────┬───────┘
       │
┌──────▼───────┐
│    Writer    │  synthesizes all summaries into sections
│              │  → Introduction, Deep Dive, Analysis, Conclusion
└──────┬───────┘
       │
┌──────▼───────┐
│    Editor    │  checks facts, improves prose, adds citations
│              │  → final polished report (Markdown)
└──────┬───────┘
       │
┌──────▼───────┐
│    Output    │  → CLI preview + save to file + (optional) PDF
└──────────────┘
```

---

## Key Design Decisions

1. **No heavy agent framework** — custom agent abstraction keeps deps minimal and shows architectural skill.
2. **Async by default** — httpx + asyncio enables parallel research agents.
3. **Free-tier first** — designed to work with rate-limited free OpenRouter models.
4. **Graceful degradation** — if a model is rate-limited, fall back to another model.
5. **Prompt templates as data** — prompts live in config/JSON, not hardcoded.

---

## Why This for a Portfolio

| Skill Demonstrated         | Evidence                                        |
|----------------------------|-------------------------------------------------|
| System Design              | Multi-agent architecture, DAG workflow          |
| LLM Integration            | OpenRouter API, prompt engineering, rate limits |
| Async Python               | httpx + asyncio parallel agent execution        |
| Clean Code                 | Abstract base classes, dependency injection     |
| Testing                    | pytest, mock LLM responses, CI pipeline         |
| Full Stack                 | CLI (Rich) + Web (Streamlit)                    |
| DevOps                     | pyproject.toml, Docker, GitHub Actions          |
| Documentation              | Masterplan, README, API docs, architecture diagram |

---

## Getting Started

```bash
# Clone & install
git clone https://github.com/<your-username>/synthara
cd synthara
pip install -e ".[dev]"

# Set your OpenRouter API key
set OPENROUTER_API_KEY=sk-or-v1-...

# Run CLI
synthara research "Quantum computing breakthroughs 2025"

# Or launch dashboard
streamlit run src/synthara/ui/dashboard.py
```

---

## License

MIT — free to use, modify, and showcase.
