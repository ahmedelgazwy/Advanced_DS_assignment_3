"""Measurement helpers shared by the demo and the benchmark.

A timer that pauses the garbage collector (as ``timeit`` does) so that
collection pauses do not distort the measurements, a median-of-repeats timer,
a peak-memory probe, a log-log slope fit and a plain-text table formatter.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import gc
import math
import statistics
import time
import tracemalloc
from contextlib import contextmanager
from typing import Callable, Iterator, Sequence, TypeVar

T = TypeVar("T")


@contextmanager
def gc_paused() -> Iterator[None]:
    """Disable the cyclic garbage collector for the duration of a block.

    Returns:
        Context manager; the previous GC state is restored on exit.
    """
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        yield
    finally:
        if was_enabled:
            gc.enable()


def measure(action: Callable[[], T]) -> tuple[T, float]:
    """Run an action once with the GC paused and time it.

    Args:
        action: Zero-argument function performing the work to time.

    Returns:
        ``(result of action, wall-clock seconds)``.
    """
    gc.collect()
    with gc_paused():
        start = time.perf_counter()
        result = action()
        elapsed = time.perf_counter() - start
    return result, elapsed


def median_time(action: Callable[[], T], repeats: int) -> tuple[T, float, list[float]]:
    """Run an action several times and report the median time.

    Args:
        action: Zero-argument function; it must do the same work every call.
        repeats: Number of runs, at least 1.

    Returns:
        ``(result of the last run, median seconds, every run's seconds)``.

    Raises:
        ValueError: If ``repeats`` < 1.
    """
    if repeats < 1:
        raise ValueError(f"repeats must be >= 1, got {repeats}")
    times = []
    result = None
    for _ in range(repeats):
        result, seconds = measure(action)
        times.append(seconds)
    return result, statistics.median(times), times  # type: ignore[return-value]


def peak_memory(action: Callable[[], T]) -> tuple[T, int]:
    """Run an action under ``tracemalloc`` and report its peak extra memory.

    Only memory allocated *during* the call counts, so the input graph is
    excluded. ``tracemalloc`` slows Python down, so never time the same run.

    Args:
        action: Zero-argument function.

    Returns:
        ``(result, peak bytes allocated during the call)``.
    """
    gc.collect()
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        base, _ = tracemalloc.get_traced_memory()
        result = action()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, peak - base


def loglog_slope(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Least-squares slope of log(y) against log(x).

    For y = c * x^k the slope is k, so a linear-time algorithm has slope 1
    when its time is plotted against n + m.

    Args:
        xs: Positive sizes, at least two distinct values.
        ys: Positive measurements, same length.

    Returns:
        The fitted exponent k.

    Raises:
        ValueError: If fewer than two points, or all x are equal.
    """
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("need at least two (x, y) points")
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    mx, my = statistics.fmean(lx), statistics.fmean(ly)
    sxx = sum((a - mx) ** 2 for a in lx)
    if sxx == 0:
        raise ValueError("all x values are equal")
    return sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sxx


def format_table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    """Format rows as an aligned plain-text table (numbers right-aligned).

    Args:
        headers: Column titles.
        rows: One sequence of cells per row; cells are converted with ``str``.

    Returns:
        The table, one line per row, with a dashed rule under the headers.
    """
    cells = [[str(c) for c in headers]] + [[str(c) for c in row] for row in rows]
    widths = [max(len(row[i]) for row in cells) for i in range(len(headers))]

    def line(row: list[str]) -> str:
        """Join one row's cells, padded to the column widths."""
        parts = []
        for i, cell in enumerate(row):
            numeric = cell.replace(".", "", 1).replace(",", "").replace("-", "", 1).isdigit()
            parts.append(cell.rjust(widths[i]) if numeric else cell.ljust(widths[i]))
        return "  ".join(parts).rstrip()

    rule = "  ".join("-" * w for w in widths)
    return "\n".join([line(cells[0]), rule] + [line(row) for row in cells[1:]])
