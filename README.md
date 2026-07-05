# Synthara

**Multi-Agent AI Research & Content Platform** — Orchestrates **12+ free LLM providers** through a team of specialized AI agents with automatic failover. Set one API key and go.

## Quick Start

```bash
pip install -e ".[dev]"
export OPENROUTER_API_KEY="sk-or-v1-..."
synthara research "Quantum computing breakthroughs 2025"
```

Or use any other free provider — just set its env var:
```bash
export GROQ_API_KEY="gsk_..."
export GEMINI_API_KEY="AI..."
synthara research "Latest AI research papers"
```

## Architecture

Four specialized agents collaborate on every task. The **MultiProviderRouter** automatically fails over across providers when one rate-limits:

1. **Planner** — decomposes your query into a structured research plan
2. **Researcher** — gathers information via web search and summarizes sources
3. **Writer** — synthesizes findings into well-structured sections
4. **Editor** — polishes prose, checks facts, adds citations

## Supported Providers

Set any combination of these env vars. The router tries them in priority order with auto-failover:

| Provider       | Env Var               | Base URL                                     |
|----------------|-----------------------|----------------------------------------------|
| OpenRouter     | `OPENROUTER_API_KEY`  | `openrouter.ai/api/v1`                       |
| Groq           | `GROQ_API_KEY`        | `api.groq.com/openai/v1`                     |
| Cerebras       | `CEREBRAS_API_KEY`    | `api.cerebras.ai/v1`                         |
| Google Gemini  | `GEMINI_API_KEY`      | `generativelanguage.googleapis.com/v1beta/openai` |
| Mistral        | `MISTRAL_API_KEY`     | `api.mistral.ai/v1`                          |
| GitHub Models  | `GITHUB_API_KEY`      | `models.github.ai/inference`                 |
| Cloudflare     | `CLOUDFLARE_API_KEY`  | `api.cloudflare.com/client/v4/.../ai/v1`     |
| NVIDIA NIM     | `NVIDIA_API_KEY`      | `integrate.api.nvidia.com/v1`                |
| HuggingFace    | `HF_API_KEY`          | `router.huggingface.co/v1`                  |
| SambaNova      | `SAMBANOVA_API_KEY`   | `api.sambanova.ai/v1`                        |
| DeepSeek       | `DEEPSEEK_API_KEY`    | `api.deepseek.com`                           |
| Cohere         | `COHERE_API_KEY`      | `api.cohere.com/v1`                          |

## License

MIT
