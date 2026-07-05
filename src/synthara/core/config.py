import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib


@dataclass
class LLMConfig:
    provider: str = "openrouter"
    api_key_env: str = "OPENROUTER_API_KEY"
    base_url: str = "https://openrouter.ai/api/v1"
    models: list[str] = field(default_factory=lambda: [
        "mistralai/mistral-7b-instruct",
        "meta-llama/llama-3-8b-instruct",
        "google/gemini-flash-1.5",
    ])
    max_retries: int = 3
    request_timeout: int = 60

    @property
    def api_key(self) -> str:
        key = os.environ.get(self.api_key_env)
        if not key:
            raise ValueError(f"Missing {self.api_key_env} environment variable")
        return key


@dataclass
class AgentsConfig:
    planner_model: str = "mistralai/mistral-7b-instruct"
    researcher_model: str = "mistralai/mistral-7b-instruct"
    writer_model: str = "meta-llama/llama-3-8b-instruct"
    editor_model: str = "meta-llama/llama-3-8b-instruct"


@dataclass
class ResearchConfig:
    max_sources_per_query: int = 5
    search_language: str = "en"


@dataclass
class MemoryConfig:
    db_path: str = "synthara.db"


@dataclass
class AppConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    agents: AgentsConfig = field(default_factory=AgentsConfig)
    research: ResearchConfig = field(default_factory=ResearchConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)


def load_config(path: str | None = None) -> AppConfig:
    config = AppConfig()
    if path is None:
        path = "config.toml"
    config_path = Path(path)
    if not config_path.exists():
        return config

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    if "llm" in data:
        llm = data["llm"]
        if "models" in llm:
            config.llm.models = llm["models"]
        if "base_url" in llm:
            config.llm.base_url = llm["base_url"]
        if "max_retries" in llm:
            config.llm.max_retries = llm["max_retries"]
        if "request_timeout" in llm:
            config.llm.request_timeout = llm["request_timeout"]

    if "agents" in data:
        agents = data["agents"]
        for key in ("planner_model", "researcher_model", "writer_model", "editor_model"):
            if key in agents:
                setattr(config.agents, key, agents[key])

    if "research" in data:
        r = data["research"]
        if "max_sources_per_query" in r:
            config.research.max_sources_per_query = r["max_sources_per_query"]
        if "search_language" in r:
            config.research.search_language = r["search_language"]

    if "memory" in data:
        mem = data["memory"]
        if "db_path" in mem:
            config.memory.db_path = mem["db_path"]

    return config
