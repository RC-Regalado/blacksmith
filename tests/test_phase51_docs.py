"""Tests for Phase 5.1 operator docs."""

from pathlib import Path

import pytest


pytestmark = pytest.mark.unit


def test_phase51_operator_docs_cover_required_workflows() -> None:
    guide = Path("docs/knowledge-engine.md").read_text(encoding="utf-8")

    assert "AI_ASSISTANT_MODEL=blacksmith-tools" in guide
    assert "AI_ASSISTANT_TOOL_SOCKET=/tmp/blacksmith-toolserver.sock" in guide
    assert "python main.py chat --context" in guide
    assert "python main.py chat --context --metrics" in guide
    assert 'python main.py objective --metrics "Explain why ExecutionEngine cannot write files"' in guide
    assert 'python main.py knowledge query "ExecutionEngine" --metrics' in guide
    assert "Empty and stale-only query diagnostics never trigger indexing or rebuilds." in guide
    assert "semantic user memory, automatic skills, MCP, network retrieval" in guide
