"""Semantic Kernel plugin that exposes the GitHub PR-reading surface as
kernel functions. The Azure OpenAI agent calls these the same way an MCP
client would call MCP tools."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Annotated

from semantic_kernel.functions import kernel_function

from agent_academy_msft.github_data import fetch_pull_request


class GitHubPRPlugin:
    """A handful of read-only tools the PR-reviewer agent uses."""

    def __init__(self, stub: bool = True):
        self._stub = stub

    @kernel_function(
        name="get_pr_summary",
        description="Fetch top-level metadata for a GitHub pull request (title, "
                    "author, additions/deletions, changed file count, base/head "
                    "branches, body).",
    )
    def get_pr_summary(
        self,
        repo: Annotated[str, "GitHub owner/repo, e.g. 'openclaw/openclaw'"],
        number: Annotated[int, "Pull request number, e.g. 24643"],
    ) -> str:
        pr = fetch_pull_request(repo, number, stub=self._stub)
        d = asdict(pr)
        # The diff and per-file blobs are heavy; keep this lean.
        d.pop("diff", None)
        d.pop("files", None)
        return json.dumps(d, indent=2)

    @kernel_function(
        name="list_pr_files",
        description="List the files touched by a pull request with per-file additions, "
                    "deletions, and status.",
    )
    def list_pr_files(
        self,
        repo: Annotated[str, "GitHub owner/repo"],
        number: Annotated[int, "Pull request number"],
    ) -> str:
        pr = fetch_pull_request(repo, number, stub=self._stub)
        return json.dumps({"files": pr.files}, indent=2)

    @kernel_function(
        name="get_pr_diff",
        description="Fetch the unified diff (patch) for a pull request. Use this when "
                    "you need to read the actual code changes to evaluate risk.",
    )
    def get_pr_diff(
        self,
        repo: Annotated[str, "GitHub owner/repo"],
        number: Annotated[int, "Pull request number"],
    ) -> str:
        pr = fetch_pull_request(repo, number, stub=self._stub)
        return pr.diff or "(no diff available)"
