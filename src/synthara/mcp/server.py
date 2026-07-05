"""MCP server providing Synthara agent tools for AI assistants.

This allows AI assistants (like Claude, opencode) to use Synthara's
research capabilities directly.
"""

from __future__ import annotations

import asyncio
import json
import sys

from synthara.agents.orchestrator import Orchestrator
from synthara.core.config import load_config
from synthara.core.llm import LLMClient
from synthara.memory.store import MemoryStore


def handle_request(request: dict) -> dict:
    method = request.get("method", "")
    params = request.get("params", {})

    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "research",
                    "description": "Research a topic using multi-agent AI pipeline",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Research topic or question",
                            },
                        },
                        "required": ["query"],
                    },
                },
            ],
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "research":
            query = arguments.get("query", "")
            if not query:
                return {"error": "Missing 'query' argument"}

            config = load_config()
            llm = LLMClient(config)
            memory = MemoryStore(config.memory.db_path)
            orchestrator = Orchestrator(config=config, llm=llm, memory=memory)

            report = asyncio.run(orchestrator.run(query))
            llm.close()
            memory.close()

            return {
                "content": [
                    {"type": "text", "text": report.content},
                ],
            }

        return {"error": f"Unknown tool: {tool_name}"}

    if method == "mcp/initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "synthara", "version": "0.1.0"},
        }

    return {"error": f"Unknown method: {method}"}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except (json.JSONDecodeError, Exception) as e:
            print(json.dumps({"error": str(e)}), flush=True)


if __name__ == "__main__":
    main()
