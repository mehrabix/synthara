---
name: synthara-dev
description: Development workflow for the Synthara project
---

# Synthara Development Skill

## Commands

### Install
```bash
pip install -e ".[dev]"
```

### Run CLI
```bash
synthara research "your query here"
```

### Run tests
```bash
pytest
```

### Lint
```bash
ruff check src/
```

### Type check
```bash
mypy src/
```

## Key Files

| Purpose              | Path                        |
|----------------------|-----------------------------|
| Entry point          | `src/synthara/__main__.py`  |
| Multi-provider router| `src/synthara/core/llm.py`  |
| Provider configs     | `src/synthara/core/config.py`|
| Agent base           | `src/synthara/agents/base.py` |
| Orchestrator         | `src/synthara/agents/orchestrator.py` |
| Config               | `config.toml`               |

## Free Provider API Keys

Set at least one of these. The router auto-failovers across all configured.

```bash
# Pick one — or set them all for max uptime:
set OPENROUTER_API_KEY=sk-or-v1-...
set GROQ_API_KEY=gsk_...
set GEMINI_API_KEY=AI...
set MISTRAL_API_KEY=...
set CEREBRAS_API_KEY=...
set NVIDIA_API_KEY=...
set GITHUB_API_KEY=...
set CLOUDFLARE_API_KEY=...
set HF_API_KEY=hf_...
set SAMBANOVA_API_KEY=...
set DEEPSEEK_API_KEY=...
set COHERE_API_KEY=...
```

## Testing with Mock

For tests without API calls, mock the router:

```python
class MockRouter:
    async def chat(self, messages, model=None, **kwargs):
        return "Mock response"

    async def close(self):
        pass
```
