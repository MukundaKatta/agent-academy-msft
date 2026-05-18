"""Canned GitHub PR data + an httpx-backed real client. The plugin layer
calls into here so the rest of the agent doesn't care whether the data is
real or stubbed."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass
class PullRequest:
    repo: str
    number: int
    title: str
    author: str
    state: str
    base: str
    head: str
    additions: int
    deletions: int
    changed_files: int
    body: str
    files: list[dict[str, Any]] = field(default_factory=list)
    diff: str = ""


# Three canned PRs covering the patterns a reviewer agent has to handle:
# small + tested, big + risky, docs-only.
CANNED_PRS: dict[str, PullRequest] = {
    "openclaw/openclaw#24643": PullRequest(
        repo="openclaw/openclaw",
        number=24643,
        title="WhatsApp: drop streaming chunks before final reply",
        author="mukundakatta",
        state="open",
        base="main",
        head="feat/whatsapp-no-stream",
        additions=87,
        deletions=23,
        changed_files=4,
        body=(
            "WhatsApp doesn't render partial messages well; this change holds "
            "tokens in the channel router until is_final and then sends one "
            "message. Adds a unit test that the router only flushes once."
        ),
        files=[
            {"filename": "src/channels/whatsapp.ts",  "additions": 38, "deletions": 12, "status": "modified"},
            {"filename": "src/routing/index.ts",      "additions": 22, "deletions": 8,  "status": "modified"},
            {"filename": "src/routing/whatsapp.test.ts","additions": 25, "deletions": 0, "status": "added"},
            {"filename": "docs/channels/whatsapp.md", "additions": 2,  "deletions": 3,  "status": "modified"},
        ],
        diff=("--- a/src/channels/whatsapp.ts\n+++ b/src/channels/whatsapp.ts\n"
              "@@ -42,7 +42,11 @@\n-  await sendChunk(token);\n+  if (event.is_final) {\n+    await sendChunk(buffer + token);\n+    buffer = \"\";\n+  } else {\n+    buffer += token;\n+  }\n"),
    ),
    "openclaw/openclaw#24800": PullRequest(
        repo="openclaw/openclaw",
        number=24800,
        title="Replace auth library with new in-house JWT",
        author="some-contractor",
        state="open",
        base="main",
        head="feat/inhouse-jwt",
        additions=1842,
        deletions=947,
        changed_files=23,
        body=(
            "Replaces all callsites that used the third-party jose library with a "
            "minimal in-house JWT signer. Includes RS256 + HS256 paths."
        ),
        files=[
            {"filename": "src/auth/jwt.ts",         "additions": 612, "deletions": 0,   "status": "added"},
            {"filename": "src/auth/index.ts",       "additions": 184, "deletions": 290, "status": "modified"},
            {"filename": "src/gateway/auth.ts",     "additions": 220, "deletions": 180, "status": "modified"},
            {"filename": "package.json",            "additions": 1,   "deletions": 2,   "status": "modified"},
        ],
        diff="--- a/src/auth/index.ts\n+++ b/src/auth/index.ts\n@@ -1,5 +1,3 @@\n-import { jwtVerify, SignJWT } from 'jose';\n+import { jwtVerify, sign } from './jwt';\n",
    ),
    "openclaw/openclaw#24890": PullRequest(
        repo="openclaw/openclaw",
        number=24890,
        title="docs: fix broken anchor in configuration guide",
        author="docs-bot",
        state="open",
        base="main",
        head="docs/anchor-fix",
        additions=1,
        deletions=1,
        changed_files=1,
        body="Mintlify anchor in docs/configuration was using an em dash; replace with hyphen.",
        files=[
            {"filename": "docs/configuration.md", "additions": 1, "deletions": 1, "status": "modified"},
        ],
        diff="--- a/docs/configuration.md\n+++ b/docs/configuration.md\n@@ -12 +12 @@\n-## Hooks — Run scripts on Claude lifecycle events\n+## Hooks - Run scripts on Claude lifecycle events\n",
    ),
}


def _key(repo: str, number: int) -> str:
    return f"{repo}#{number}"


def fetch_pull_request(repo: str, number: int, *, stub: bool = True) -> PullRequest:
    """Either return a canned PR (stub mode) or hit the GitHub REST API.

    Real mode requires GITHUB_TOKEN env var.
    """
    key = _key(repo, number)
    if stub:
        if key not in CANNED_PRS:
            # Synthesize a small canned PR so the demo doesn't crash on unknown input.
            return PullRequest(
                repo=repo, number=number,
                title=f"(stub) untitled change in {repo}",
                author="stub-author", state="open", base="main", head="feat/stub",
                additions=42, deletions=8, changed_files=2,
                body="Stub PR. Provide a real GITHUB_TOKEN and disable stub mode to fetch the real PR.",
                files=[
                    {"filename": "src/example.py", "additions": 30, "deletions": 5, "status": "modified"},
                    {"filename": "tests/test_example.py", "additions": 12, "deletions": 3, "status": "modified"},
                ],
                diff="--- a/src/example.py\n+++ b/src/example.py\n+# stub diff\n",
            )
        return CANNED_PRS[key]

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN is required to fetch real PRs. "
            "Either set it, or call with stub=True for a canned demo."
        )
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    with httpx.Client(timeout=10.0, headers=headers) as client:
        pr_resp = client.get(f"https://api.github.com/repos/{repo}/pulls/{number}")
        pr_resp.raise_for_status()
        pr = pr_resp.json()
        files_resp = client.get(f"https://api.github.com/repos/{repo}/pulls/{number}/files")
        files_resp.raise_for_status()
        files = files_resp.json()
    return PullRequest(
        repo=repo,
        number=number,
        title=pr["title"],
        author=pr["user"]["login"],
        state=pr["state"],
        base=pr["base"]["ref"],
        head=pr["head"]["ref"],
        additions=int(pr.get("additions", 0)),
        deletions=int(pr.get("deletions", 0)),
        changed_files=int(pr.get("changed_files", 0)),
        body=pr.get("body") or "",
        files=[{
            "filename": f["filename"],
            "additions": f.get("additions", 0),
            "deletions": f.get("deletions", 0),
            "status": f.get("status", ""),
        } for f in files],
        diff="\n".join(f.get("patch", "")[:1500] for f in files if f.get("patch")),
    )
