# Agent Academy (Microsoft) — submission

Deadline: 2026-06-02
Microsoft products used: **Azure OpenAI Service** + **Microsoft Semantic Kernel**

## Rule compliance

- ✅ Uses at least one Microsoft product (two: Azure OpenAI + Semantic Kernel)
- ✅ Working agent that takes natural-language input and returns structured output
- ✅ Public GitHub repo with OSI license (Apache 2.0)
- ✅ Demo video on YouTube (under 5 minutes)

## Elevator pitch
A pull-request reviewer that walks the diff with Semantic Kernel tools
and returns a structured verdict on Azure OpenAI's gpt-4o-mini.

## Description (paste into the submission form)

agent-academy-msft treats every code review as a structured workflow:
get the PR summary, list the files, optionally read the diff, and emit a
verdict an engineer can act on. The agent is a Microsoft Semantic Kernel
`Kernel` with `FunctionChoiceBehavior.Auto`, three `kernel_function` tools
exposed via a `GitHubPRPlugin`, and Azure OpenAI's gpt-4o-mini as the
chat-completion service.

Output is always the same shape: VERDICT (APPROVE / REQUEST_CHANGES /
NEEDS_MORE_INFO), RISK (LOW / MEDIUM / HIGH), 3–5 evidence bullets, the
biggest 1–3 concerns, and one concrete next step. Reviews fit on one
screen — the system prompt caps at 250 words.

Three canned PR fixtures ship in the repo (a small tested change, a
large auth-touching change, and a docs-only one-liner) so reviewers can
exercise every code path of the verdict logic without a GitHub token. Set
`GITHUB_TOKEN` and untick the stub toggle to point at the real GitHub
REST API.

## Built with
python, semantic-kernel, azure-openai, gpt-4o-mini, microsoft-azure,
azure-container-apps, streamlit, github-rest-api, apache-2

## Try it out
- Code repo: https://github.com/MukundaKatta/agent-academy-msft
- Live demo: <PASTE_AFTER_DEPLOY>
- Demo video (YouTube unlisted): <PASTE_AFTER_REC>

## Submission checklist
- [x] At least one Microsoft product used (Azure OpenAI + Semantic Kernel)
- [x] Working agent (9 passing tests + offline-fallback verdict logic)
- [x] Public OSI-licensed repo
- [ ] Live hosted demo (waiting on Azure credentials)
- [ ] Demo video uploaded to YouTube unlisted
- [ ] Submission form filled
