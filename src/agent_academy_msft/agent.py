"""Semantic Kernel agent wired to Azure OpenAI + the GitHubPRPlugin.

The agent is a pull-request reviewer. You give it a repo and PR number, it
calls the plugin tools to fetch metadata + files + diff, then returns a
structured review.

Environment variables (real Azure mode):
    AZURE_OPENAI_ENDPOINT      https://your-resource.openai.azure.com/
    AZURE_OPENAI_API_KEY       Key 1 or 2 from the resource's Keys & Endpoint tab
    AZURE_OPENAI_DEPLOYMENT    Your model deployment name (e.g. 'gpt-4o-mini')
    AZURE_OPENAI_API_VERSION   default: 2024-10-21

Offline fallback: if no AZURE_OPENAI_ENDPOINT is set, the agent returns a
deterministic canned review so the tests + dashboard render without
credentials.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

from agent_academy_msft.github_data import fetch_pull_request
from agent_academy_msft.plugins.github_plugin import GitHubPRPlugin


SYSTEM_PROMPT = """\
You are a senior reviewer. The user hands you a GitHub repo + PR number.

Workflow:
1. Call `get_pr_summary` first to see size, author, title.
2. Call `list_pr_files` to see which files moved and by how much.
3. If the PR is non-trivial (more than ~100 lines) OR touches auth, billing,
   or security, call `get_pr_diff` and read the patch before grading.

Output a structured review with EXACTLY these sections:

VERDICT: <APPROVE | REQUEST_CHANGES | NEEDS_MORE_INFO>
RISK: <LOW | MEDIUM | HIGH>

EVIDENCE:
- 3-5 bullets, each citing a specific file or number from the tool output.

CONCERNS:
- The biggest 1-3 issues, or "none" if there are none.

NEXT STEP:
- One concrete action the author should take before merge.

Keep the whole review under 250 words.
"""


@dataclass
class ReviewResult:
    text: str
    fn_calls: list[str]
    error: str | None = None


def _try_import_sk() -> bool:
    try:
        import semantic_kernel  # noqa: F401
        from openai import AsyncAzureOpenAI  # noqa: F401
        return True
    except ImportError:
        return False


def _offline_review(repo: str, number: int, stub: bool) -> ReviewResult:
    pr = fetch_pull_request(repo, number, stub=stub)
    risk = "LOW"
    verdict = "APPROVE"
    concerns: list[str] = []
    if pr.additions + pr.deletions > 500:
        risk = "HIGH"
        verdict = "REQUEST_CHANGES"
        concerns.append(f"Large change: +{pr.additions} / -{pr.deletions} across {pr.changed_files} files.")
    if any("auth" in (f.get("filename") or "").lower() for f in pr.files):
        risk = "HIGH"
        verdict = "REQUEST_CHANGES"
        concerns.append("Touches auth code path; requires manual security review.")
    if not any("test" in (f.get("filename") or "").lower() for f in pr.files):
        if pr.additions > 30:
            concerns.append("No test file in changeset; reviewer should ask for one.")
    return ReviewResult(
        text=(
            f"VERDICT: {verdict}\n"
            f"RISK: {risk}\n\n"
            "EVIDENCE:\n"
            f"- Title: {pr.title}\n"
            f"- Author: {pr.author}\n"
            f"- Size: +{pr.additions} / -{pr.deletions} across {pr.changed_files} files.\n"
            f"- Files: {', '.join((f.get('filename') or '') for f in pr.files[:5])}\n\n"
            "CONCERNS:\n"
            + ("\n".join(f"- {c}" for c in concerns) if concerns else "- none\n")
            + "\n\nNEXT STEP:\n"
            + (f"- Address the concerns above before merge.\n" if concerns
               else "- Looks good. Squash + merge when CI is green.\n")
            + "\n(offline-fallback review; no Azure OpenAI credentials configured)\n"
        ),
        fn_calls=["get_pr_summary", "list_pr_files"],
    )


async def _arun_review(repo: str, number: int, stub: bool) -> ReviewResult:
    if not _try_import_sk():
        return _offline_review(repo, number, stub)

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not endpoint:
        return _offline_review(repo, number, stub)

    # Real path: Azure OpenAI via Semantic Kernel.
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import (
        AzureChatCompletion,
        AzureChatPromptExecutionSettings,
    )
    from semantic_kernel.connectors.ai.function_choice_behavior import (
        FunctionChoiceBehavior,
    )
    from semantic_kernel.contents import ChatHistory

    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(
        service_id="azure-chat",
        deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        endpoint=endpoint,
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
    ))
    kernel.add_plugin(GitHubPRPlugin(stub=stub), plugin_name="github")

    settings = AzureChatPromptExecutionSettings(
        service_id="azure-chat",
        function_choice_behavior=FunctionChoiceBehavior.Auto(),
        max_tokens=1000,
        temperature=0.2,
    )

    history = ChatHistory()
    history.add_system_message(SYSTEM_PROMPT)
    history.add_user_message(f"Review pull request {repo}#{number}.")

    chat_completion = kernel.get_service("azure-chat")
    response = await chat_completion.get_chat_message_content(
        chat_history=history,
        settings=settings,
        kernel=kernel,
    )
    fn_calls: list[str] = []
    for item in getattr(response, "items", []) or []:
        if getattr(item, "function_name", None):
            fn_calls.append(item.function_name)
    return ReviewResult(text=str(response.content or "").strip(), fn_calls=fn_calls)


def run_review(repo: str, number: int, stub: bool = True) -> ReviewResult:
    """Synchronous entry point used by the dashboard + tests."""
    return asyncio.run(_arun_review(repo, number, stub))
