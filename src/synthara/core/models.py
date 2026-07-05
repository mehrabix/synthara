from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal


class AgentRole(str, Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    WRITER = "writer"
    EDITOR = "editor"


MessageRole = Literal["system", "user", "assistant"]


@dataclass
class Message:
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Source:
    title: str
    url: str
    snippet: str


@dataclass
class ResearchPlan:
    query: str
    sub_questions: list[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchFindings:
    sub_question: str
    sources: list[Source]
    summary: str


@dataclass
class ReportSection:
    title: str
    content: str
    sources: list[Source] = field(default_factory=list)


@dataclass
class Report:
    query: str
    sections: list[ReportSection]
    content: str
    sources: list[Source] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Session:
    id: str
    query: str
    messages: list[Message] = field(default_factory=list)
    report: Report | None = None
    created_at: datetime = field(default_factory=datetime.now)
