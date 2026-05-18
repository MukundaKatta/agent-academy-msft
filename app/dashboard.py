"""agent-academy-msft dashboard.

PYTHONPATH=src streamlit run app/dashboard.py
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_academy_msft.agent import run_review  # noqa: E402


st.set_page_config(page_title="agent-academy-msft", layout="wide", page_icon=":memo:")
st.title("agent-academy-msft")
st.caption(
    "Pull-request reviewer agent built on Microsoft Semantic Kernel + "
    "Azure OpenAI (gpt-4o-mini). Apache 2.0."
)

with st.sidebar:
    st.header("Review a PR")
    repo = st.text_input("Repo (owner/name)", value="openclaw/openclaw")
    number = st.number_input("PR number", min_value=1, value=24800, step=1)
    stub = st.toggle(
        "Use stub PR data",
        value=True,
        help="On = canned PR fixtures. Off = real GitHub API (requires GITHUB_TOKEN).",
    )
    run = st.button("Run review", type="primary", use_container_width=True)
    st.divider()
    azure_ok = bool(os.getenv("AZURE_OPENAI_ENDPOINT"))
    st.caption(
        f"Azure OpenAI configured: `{azure_ok}`  "
        f"Deployment: `{os.getenv('AZURE_OPENAI_DEPLOYMENT', 'not-set')}`"
    )

st.markdown(
    """
The agent walks the PR with three Semantic Kernel tools backed by either
canned fixtures (stub mode) or the real GitHub REST API:
- **get_pr_summary** — title, author, additions, deletions, file count
- **list_pr_files** — per-file additions/deletions and status
- **get_pr_diff** — unified diff, used only when the change is non-trivial
"""
)

if run:
    with st.status("Running Azure OpenAI agent...", expanded=True) as status:
        t0 = time.perf_counter()
        try:
            result = run_review(repo, int(number), stub=stub)
        except Exception as e:  # pragma: no cover
            status.update(label=f"Error: {e}", state="error")
            st.exception(e)
            st.stop()
        elapsed = (time.perf_counter() - t0) * 1000
        status.update(label=f"Done in {elapsed:.0f} ms", state="complete")

    st.subheader("Review")
    st.code(result.text, language=None)

    with st.expander(f"Tool calls ({len(result.fn_calls)})"):
        for fn in result.fn_calls:
            st.markdown(f"- `{fn}`")
else:
    st.info("Use the sidebar to fire a review against the stub PR fixtures or a real GitHub PR.")
