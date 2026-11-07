"""Tests for the measurement helpers: timers, memory probe, slope fit and tables.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import gc

import pytest

from graph_heuristics.experiment import (
    format_table,
    gc_paused,
    loglog_slope,
    measure,
    median_time,
    peak_memory,
)


def test_gc_paused_restores_the_previous_state() -> None:
    assert gc.isenabled()
    with gc_paused():
        assert not gc.isenabled()
    assert gc.isenabled()


def test_measure_and_median_time() -> None:
    result, seconds = measure(lambda: sum(range(1000)))
    assert result == 499500 and seconds >= 0
    calls = []
    result, median, times = median_time(lambda: calls.append(1) or len(calls), repeats=5)
    assert result == 5 and len(times) == 5 and min(times) <= median <= max(times)
    with pytest.raises(ValueError):
        median_time(lambda: None, repeats=0)


def test_peak_memory_sees_the_allocation() -> None:
    result, peak = peak_memory(lambda: len(bytearray(2_000_000)))
    assert result == 2_000_000
    assert 2_000_000 <= peak < 3_000_000


def test_loglog_slope_of_exact_power_laws() -> None:
    xs = [10, 100, 1_000, 10_000]
    assert loglog_slope(xs, [3 * x**1.5 for x in xs]) == pytest.approx(1.5)
    assert loglog_slope(xs, [7.0] * 4) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        loglog_slope([1], [1])
    with pytest.raises(ValueError):
        loglog_slope([5, 5], [1, 2])


def test_format_table_aligns_columns() -> None:
    text = format_table(["name", "value"], [["a", 1], ["long name", 12.5]])
    lines = text.splitlines()
    assert lines[0].startswith("name") and set(lines[1]) <= {"-", " "}
    assert lines[2].endswith("    1")  # numbers are right-aligned
    assert len({len(line) for line in lines[1:]}) == 1
