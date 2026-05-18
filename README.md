# agent-academy-msft

A pull-request reviewer agent built on **Microsoft Semantic Kernel** —
Microsoft's open-source agent SDK — routed through **Vertex AI Gemini 2.5 Flash**.

**Live demo:** https://agent-academy-msft-1029931682737.us-central1.run.app
**Demo video:** https://youtu.be/wCPa7pLAaII (1:59)
**License:** Apache 2.0

## What it does

You give it a GitHub repo + PR number. The agent walks the PR with three
Semantic Kernel `kernel_function` tools — `get_pr_summary`, `list_pr_files`,
`get_pr_diff` — then returns a structured review with a verdict (APPROVE /
REQUEST_CHANGES / NEEDS_MORE_INFO), a risk level (LOW / MEDIUM / HIGH),
3–5 evidence bullets, the biggest 1–3 concerns, and one next-step
instruction for the author.

## Why Semantic Kernel + Vertex AI

Semantic Kernel is Microsoft's agent SDK — that's the Microsoft product
required by the Agent Academy hackathon. SK is provider-agnostic; this
build routes through Vertex AI Gemini via the
`semantic_kernel.connectors.ai.google.vertex_ai` connector because GCP
plumbing is already wired and reviewers can run it without provisioning
an Azure tenant. Swap the connector for `AzureChatCompletion` in five
lines if you do have Azure OpenAI.

## Architecture

```
┌─────────────┐  repo + PR number    ┌────────────────────────────────────┐
│  Streamlit  │ ───────────────────▶ │  Semantic Kernel Kernel            │
│  dashboard  │                       │  VertexAIChatCompletion service    │
│             │                       │  + FunctionChoiceBehavior.Auto     │
└─────────────┘ ◀── verdict + cites ─└────┬───────────────────────────────┘
                                            │ kernel_function tool calls
                                            ▼
                                   ┌─────────────────────────────┐
                                   │  GitHubPRPlugin              │
                                   │  3 kernel_function tools     │
                                   │  (canned or real GitHub API) │
                                   └─────────────────────────────┘
```

## Try it locally

```bash
git clone https://github.com/MukundaKatta/agent-academy-msft
cd agent-academy-msft
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_CLOUD_LOCATION=us-central1

PYTHONPATH=src streamlit run app/dashboard.py
```

Without `GOOGLE_CLOUD_PROJECT`, the agent falls back to a deterministic
rule-based review so reviewers can still see something on the dashboard.

## Real GitHub PR fetching

```bash
export GITHUB_TOKEN="ghp_..."
```

Then untick "Use stub PR data" in the dashboard sidebar.

## Tests

```bash
PYTHONPATH=src pytest -q
```

9 tests cover canned PR fixtures + the offline-fallback verdict logic.

## Microsoft products used

- **Microsoft Semantic Kernel** (the agent framework — `Kernel`,
  `kernel_function`, `FunctionChoiceBehavior.Auto`)

## License

Apache 2.0. Mukunda Katta, independent developer.
