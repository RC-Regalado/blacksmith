"""Tests for Phase 4 preparation docs."""

from pathlib import Path

import pytest


pytestmark = pytest.mark.unit


def test_phase4_roadmap_records_scaffolding_without_activation() -> None:
    roadmap = Path("docs/roadmap-phase-4.md").read_text(encoding="utf-8")

    assert "M4.0" in roadmap
    assert "autonomous multi-step execution" in roadmap
    assert "not active" in roadmap
