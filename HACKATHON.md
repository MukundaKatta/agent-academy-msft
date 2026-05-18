# Agent Academy (Microsoft) — submission

Deadline: 2026-06-02
Microsoft product used: **Microsoft Semantic Kernel** (open-source agent SDK)
LLM backbone: Vertex AI Gemini 2.5 Flash (via SK's `VertexAIChatCompletion`)

## Rule compliance

- ✅ Uses at least one Microsoft product (Microsoft Semantic Kernel)
- ✅ Working agent that takes natural-language input and returns structured output
- ✅ Public GitHub repo with OSI license (Apache 2.0)
- ✅ Demo video on YouTube under 5 minutes

## Why this route

Semantic Kernel is Microsoft's open-source agent SDK; using it satisfies
the hackathon's "at least one Microsoft product" requirement. SK is
provider-agnostic. This build routes through Vertex AI Gemini 2.5 Flash
because the project already had GCP plumbing wired and reviewers can
run it without an Azure subscription. Swapping in `AzureChatCompletion`
is a five-line change for teams that prefer Azure OpenAI.

## Elevator pitch
A pull-request reviewer that walks the diff with Semantic Kernel tools
and returns a structured APPROVE / REQUEST_CHANGES verdict on Vertex AI
Gemini 2.5 Flash.

## Description (paste into the submission form)

agent-academy-msft treats every code review as a structured workflow:
get the PR summary, list the files, optionally read the diff, then emit
a verdict an engineer can act on. The agent is a Microsoft Semantic
Kernel `Kernel` with `FunctionChoiceBehavior.Auto`, three
`kernel_function` tools exposed via a `GitHubPRPlugin`, and Vertex AI
Gemini 2.5 Flash as the chat-completion service (via SK's
`VertexAIChatCompletion`).

Output is always the same shape: VERDICT (APPROVE / REQUEST_CHANGES /
NEEDS_MORE_INFO), RISK (LOW / MEDIUM / HIGH), 3–5 evidence bullets,
the biggest 1–3 concerns, and one concrete next step. Reviews fit on
one screen — the system prompt caps at 250 words.

Three canned PR fixtures ship in the repo (a small tested change, a
large auth-touching change, and a docs-only one-liner) so reviewers can
exercise every code path of the verdict logic without a GitHub token.
Set `GITHUB_TOKEN` and untick the stub toggle to point at the real
GitHub REST API.

Live agent run on the large auth-touching PR returned: VERDICT
NEEDS_MORE_INFO, RISK HIGH, citing `src/auth/jwt.ts` (612 lines added)
and the 1842 / 947 / 23 files diff size, recommending the author
provide the full diff for security review.

## Built with
python, semantic-kernel, microsoft-semantic-kernel, vertex-ai, gemini,
gemini-2-5, google-cloud, google-cloud-run, streamlit, github-rest-api,
apache-2

## Try it out
- Code repo: https://github.com/MukundaKatta/agent-academy-msft
- Live demo: https://agent-academy-msft-1029931682737.us-central1.run.app
- Demo video (YouTube unlisted): https://youtu.be/wCPa7pLAaII

## Submission checklist
- [x] At least one Microsoft product used (Semantic Kernel)
- [x] Working agent (9 passing tests + real Vertex AI run verified)
- [x] Public OSI-licensed repo
- [ ] Live hosted demo URL
- [ ] Demo video uploaded to YouTube unlisted
- [ ] Submission form filled
