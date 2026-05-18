"""Offline-mode tests: with no AZURE_OPENAI_ENDPOINT set, the agent
falls back to a deterministic rule-based review."""

from __future__ import annotations

import os

import pytest

from agent_academy_msft.agent import run_review


@pytest.fixture(autouse=True)
def _clear_gcp_env(monkeypatch):
    """Force offline fallback for these tests."""
    for k in ("GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION", "SK_GEMINI_MODEL"):
        monkeypatch.delenv(k, raising=False)


def test_small_pr_with_tests_gets_approve():
    r = run_review("openclaw/openclaw", 24643, stub=True)
    assert "APPROVE" in r.text
    assert "RISK: LOW" in r.text or "RISK: MEDIUM" in r.text


def test_large_auth_pr_gets_request_changes_high_risk():
    r = run_review("openclaw/openclaw", 24800, stub=True)
    assert "REQUEST_CHANGES" in r.text
    assert "HIGH" in r.text
    assert "auth" in r.text.lower()


def test_docs_only_pr_has_no_concerns():
    r = run_review("openclaw/openclaw", 24890, stub=True)
    # Docs-only changes shouldn't be flagged on size or tests.
    assert "APPROVE" in r.text
    assert "- none" in r.text


def test_fn_calls_recorded_in_offline_mode():
    r = run_review("openclaw/openclaw", 24643, stub=True)
    assert "get_pr_summary" in r.fn_calls
    assert "list_pr_files" in r.fn_calls
