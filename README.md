# agent-academy-msft

A pull-request reviewer agent built on **Microsoft Semantic Kernel** and
**Azure OpenAI** (gpt-4o-mini).

Open source under Apache 2.0.

## What it does

You give it a GitHub repo + PR number. The agent walks the PR with three
tools — `get_pr_summary`, `list_pr_files`, `get_pr_diff` — then returns a
structured review with a verdict (APPROVE / REQUEST_CHANGES /
NEEDS_MORE_INFO), a risk level (LOW / MEDIUM / HIGH), 3–5 evidence
bullets, the biggest 1–3 concerns, and a single next-step instruction
for the author.

## Architecture

```
┌─────────────┐  repo + PR number    ┌──────────────────────────────┐
│  Streamlit  │ ───────────────────▶ │  Semantic Kernel Kernel       │
│  dashboard  │                       │  (Azure OpenAI gpt-4o-mini)   │
└─────────────┘ ◀── verdict + cites ─└────┬─────────────────────────┘
                                            │ FunctionChoiceBehavior.Auto
                                            ▼
                                   ┌─────────────────────────┐
                                   │  GitHubPRPlugin          │
                                   │  3 kernel_function tools │
                                   │  (stub or real GitHub)   │
                                   └─────────────────────────┘
```

## Try it locally (no Azure credentials needed — offline fallback)

```bash
git clone https://github.com/MukundaKatta/agent-academy-msft
cd agent-academy-msft
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
PYTHONPATH=src streamlit run app/dashboard.py
```

Without `AZURE_OPENAI_ENDPOINT`, the agent returns a deterministic
rule-based review. With Azure configured, it routes through gpt-4o-mini.

## Configure Azure OpenAI

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"
export AZURE_OPENAI_API_VERSION="2024-10-21"
```

## Configure real GitHub PR fetching

```bash
export GITHUB_TOKEN="ghp_..."
```

Then untick "Use stub PR data" in the dashboard sidebar.

## Tests

```bash
PYTHONPATH=src pytest -q
```

9 tests cover canned PR fixtures + the offline-fallback verdict logic.

## License

Apache 2.0. Mukunda Katta, independent developer.
