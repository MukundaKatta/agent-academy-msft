from agent_academy_msft.github_data import (
    CANNED_PRS,
    fetch_pull_request,
    PullRequest,
)


def test_canned_prs_loaded():
    assert len(CANNED_PRS) >= 3


def test_fetch_pull_request_small_tested():
    pr = fetch_pull_request("openclaw/openclaw", 24643, stub=True)
    assert isinstance(pr, PullRequest)
    assert pr.title.startswith("WhatsApp")
    assert pr.changed_files == 4
    assert any("test" in (f.get("filename") or "") for f in pr.files)


def test_fetch_pull_request_large_risky():
    pr = fetch_pull_request("openclaw/openclaw", 24800, stub=True)
    assert pr.additions + pr.deletions > 1000
    assert any("auth" in (f.get("filename") or "") for f in pr.files)


def test_fetch_pull_request_docs_only():
    pr = fetch_pull_request("openclaw/openclaw", 24890, stub=True)
    assert pr.additions == 1 and pr.deletions == 1
    assert pr.changed_files == 1


def test_fetch_unknown_pr_returns_stub_placeholder():
    pr = fetch_pull_request("unknown/repo", 999999, stub=True)
    assert pr.repo == "unknown/repo"
    assert pr.title.startswith("(stub)")
