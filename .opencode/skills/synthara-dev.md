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
| LLM client           | `src/synthara/core/llm.py`  |
| Agent base           | `src/synthara/agents/base.py` |
| Orchestrator         | `src/synthara/agents/orchestrator.py` |
| Config               | `config.toml`               |
| Masterplan           | `MASTERPLAN.md`             |

## OpenRouter API Key

Set your key before running:
```bash
set OPENROUTER_API_KEY=sk-or-v1-...
```

## Testing with Free Models

The default config uses free OpenRouter models. Rate limits are ~10-20 req/min.
For testing without API calls, mock the LLM client:
```python
from synthara.core.llm import LLMClient

class MockLLM(LLMClient):
    async def chat(self, messages, **kwargs):
        return "Mock response"
```
