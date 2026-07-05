"""Streamlit dashboard for Synthara.

Run with: streamlit run src/synthara/ui/dashboard.py
"""

from __future__ import annotations

import asyncio

import streamlit as st

from synthara.agents.orchestrator import Orchestrator
from synthara.core.config import load_config
from synthara.core.llm import LLMClient
from synthara.memory.store import MemoryStore
from synthara.ui.cli import CLIRenderer

st.set_page_config(
    page_title="Synthara",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Synthara")
st.markdown("*Multi-Agent AI Research Platform*")

config = load_config()
memory = MemoryStore(config.memory.db_path)

if "llm" not in st.session_state:
    st.session_state.llm = LLMClient(config)
if "renderer" not in st.session_state:
    st.session_state.renderer = CLIRenderer()

with st.sidebar:
    st.header("History")
    sessions = memory.list_sessions()
    for s in sessions[-10:]:
        if st.button(f"{s['query'][:50]}...", key=s["id"]):
            st.session_state.selected_session = s["id"]

    st.divider()
    if st.button("Clear History"):
        st.cache_data.clear()
        st.rerun()

col1, col2 = st.columns([2, 1])

with col1:
    query = st.text_area(
        "Research Query",
        placeholder="e.g., Quantum computing breakthroughs in 2025...",
        height=100,
    )

    if st.button("Research", type="primary") and query:
        with st.spinner("Running research pipeline..."):
            orchestrator = Orchestrator(
                config=config,
                llm=st.session_state.llm,
                memory=memory,
                renderer=st.session_state.renderer,
            )
            report = asyncio.run(orchestrator.run(query))
            st.session_state.report = report.content
            st.rerun()

    if "report" in st.session_state:
        st.markdown(st.session_state.report)

with col2:
    st.header("Status")
    provider_list = list(config.llm.providers.keys())
    provider_label = ", ".join(provider_list[:3])
    if len(provider_list) > 3:
        provider_label += "..."
    st.info(f"Providers: {provider_label}")
    st.info("Agents: Planner → Researcher → Writer → Editor")

memory.close()
