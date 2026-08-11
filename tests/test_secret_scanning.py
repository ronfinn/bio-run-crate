"""Tests for the repository's secret-scanning configuration.

These guard the configuration itself, not gitleaks' detection behaviour: they
check that the config stays parseable, keeps inheriting the upstream rule set,
keeps its allowlist narrow, and stays wired into CI for both triggers required
by the project's security policy.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
GITLEAKS_CONFIG = REPO_ROOT / ".gitleaks.toml"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


@pytest.fixture(scope="module")
def gitleaks_config() -> dict[str, Any]:
    with GITLEAKS_CONFIG.open("rb") as handle:
        config: dict[str, Any] = tomllib.load(handle)
    return config


@pytest.fixture(scope="module")
def ci_workflow() -> dict[str, Any]:
    workflow: dict[str, Any] = yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))
    return workflow


def test_gitleaks_config_inherits_default_rules(
    gitleaks_config: dict[str, Any],
) -> None:
    assert gitleaks_config["extend"]["useDefault"] is True


def test_gitleaks_config_does_not_disable_default_rules(
    gitleaks_config: dict[str, Any],
) -> None:
    """A global rule opt-out would silently remove protection; use an allowlist."""
    assert "disabledRules" not in gitleaks_config
    assert "stopwords" not in gitleaks_config.get("allowlist", {})


def test_allowlist_paths_are_narrow(gitleaks_config: dict[str, Any]) -> None:
    """Allowlisted paths must be anchored, specific files rather than globs."""
    paths = gitleaks_config["allowlist"]["paths"]
    assert paths, "the allowlist mechanism should be present and documented"
    for pattern in paths:
        assert pattern.startswith("^"), f"unanchored allowlist path: {pattern}"
        assert pattern.endswith("$"), f"unanchored allowlist path: {pattern}"
        assert "*" not in pattern.replace(r"\.", ""), (
            f"wildcard allowlist path: {pattern}"
        )


def test_allowlist_covers_the_env_example_template(
    gitleaks_config: dict[str, Any],
) -> None:
    assert r"^\.env\.example$" in gitleaks_config["allowlist"]["paths"]
    assert (REPO_ROOT / ".env.example").is_file()


def test_ci_runs_secret_scanning_on_pull_requests_and_main(
    ci_workflow: dict[str, Any],
) -> None:
    # PyYAML parses the unquoted key `on` as the boolean True.
    triggers = ci_workflow[True]
    assert "pull_request" in triggers
    assert triggers["push"]["branches"] == ["main"]

    job = ci_workflow["jobs"]["secret-scan"]
    steps = job["steps"]
    assert any(
        step.get("uses", "").startswith("gitleaks/gitleaks-action@") for step in steps
    )


def test_ci_secret_scan_checks_out_full_history(ci_workflow: dict[str, Any]) -> None:
    """Gitleaks must see every commit, not just the tip, to catch removed secrets."""
    steps = ci_workflow["jobs"]["secret-scan"]["steps"]
    checkout = next(
        step for step in steps if step.get("uses", "").startswith("actions/checkout@")
    )
    assert checkout["with"]["fetch-depth"] == 0


def test_ci_secret_scan_uses_the_repository_config(ci_workflow: dict[str, Any]) -> None:
    steps = ci_workflow["jobs"]["secret-scan"]["steps"]
    scan = next(step for step in steps if step.get("uses", "").startswith("gitleaks/"))
    assert scan["env"]["GITLEAKS_CONFIG"].endswith("/.gitleaks.toml")
