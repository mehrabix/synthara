from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

try:
    import tomllib
except ImportError:
    import tomli as tomllib

RoutingStrategy = Literal["priority", "round_robin"]


@dataclass
class ProviderConfig:
    base_url: str
    api_key_env: str
    models: list[str] = field(default_factory=list)
    priority: int = 999

    def resolve_base_url(self) -> str:
        """Resolve ${VAR} placeholders in base_url from environment."""
        def _replace(m: re.Match) -> str:
            return os.environ.get(m.group(1), "")
        return re.sub(r"\$\{(\w+)\}", _replace, self.base_url)

    @property
    def api_key(self) -> str | None:
        return os.environ.get(self.api_key_env)


@dataclass
class LLMConfig:
    routing_strategy: RoutingStrategy = "priority"
    max_retries: int = 2
    request_timeout: int = 60
    providers: dict[str, ProviderConfig] = field(default_factory=dict)

    def active_providers(self) -> list[tuple[str, ProviderConfig]]:
        """Return providers sorted by priority, filtering out those without API keys."""
        active = [
            (name, p) for name, p in self.providers.items()
            if p.api_key
        ]
        if self.routing_strategy == "priority":
            active.sort(key=lambda x: x[1].priority)
        return active


@dataclass
class AgentsConfig:
    planner_model: str = "mistralai/mistral-7b-instruct:free"
    researcher_model: str = "mistralai/mistral-7b-instruct:free"
    writer_model: str = "meta-llama/llama-3-8b-instruct:free"
    editor_model: str = "llama-3.3-70b-versatile"


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

    # LLM section - providers
    if "llm" in data:
        llm = data["llm"]
        if "routing_strategy" in llm:
            config.llm.routing_strategy = llm["routing_strategy"]
        if "max_retries" in llm:
            config.llm.max_retries = llm["max_retries"]
        if "request_timeout" in llm:
            config.llm.request_timeout = llm["request_timeout"]
        if "providers" in llm:
            for name, pdata in llm["providers"].items():
                config.llm.providers[name] = ProviderConfig(
                    base_url=pdata.get("base_url", ""),
                    api_key_env=pdata.get("api_key_env", ""),
                    models=pdata.get("models", []),
                    priority=pdata.get("priority", 999),
                )

    # Agents section
    if "agents" in data:
        agents = data["agents"]
        for key in ("planner_model", "researcher_model", "writer_model", "editor_model"):
            if key in agents:
                setattr(config.agents, key, agents[key])

    # Research section
    if "research" in data:
        r = data["research"]
        if "max_sources_per_query" in r:
            config.research.max_sources_per_query = r["max_sources_per_query"]
        if "search_language" in r:
            config.research.search_language = r["search_language"]

    # Memory section
    if "memory" in data:
        mem = data["memory"]
        if "db_path" in mem:
            config.memory.db_path = mem["db_path"]

    return config
