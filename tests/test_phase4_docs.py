"""Tests for Phase 4 preparation docs."""

from pathlib import Path

import pytest


pytestmark = pytest.mark.unit


def test_phase4_roadmap_starts_with_baseline_freeze() -> None:
    roadmap = Path("docs/roadmap-phase-4.md").read_text(encoding="utf-8")

    assert "M4.1 — Freeze Phase 3 baseline" in roadmap
    assert "Autonomous plans may not use `write`" in roadmap
    assert "retries, replanning, parallel execution or subagents" in roadmap
