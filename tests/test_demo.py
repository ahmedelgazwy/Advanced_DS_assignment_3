"""The demo runs end to end, with and without the downloaded FRB graph.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import pytest

import demo


def test_demo_with_a_generated_graph(capsys: pytest.CaptureFixture[str]) -> None:
    # frb35-17-9 does not exist, so part 3 falls back to a planted graph.
    assert demo.main(["--quick", "--seeds", "3", "--instance", "frb35-17-9"]) == 0
    out = capsys.readouterr().out
    for part in ("Part 1", "Part 2", "Part 3", "a generated FRB-like graph"):
        assert part in out
    assert "INVALID" not in out


def test_demo_default_instance(capsys: pytest.CaptureFixture[str]) -> None:
    assert demo.main(["--quick", "--seeds", "3"]) == 0
    assert "exact chromatic number" in capsys.readouterr().out
