"""Benchmark the two vertex cover and the two coloring algorithms.

Usage (from the repository root)::

    python -m scripts.run_benchmarks --quick    # about 1 minute  -> results/quick/
    python -m scripts.run_benchmarks            # about 15 minutes -> results/

Experiments (docs/plan.md, section 8), each written to a CSV file:

* **E1 ``frb_runtime.csv``**: running time of every algorithm on the 36 FRB
  graphs, in both forms (``clq`` as published, ``mis`` its complement).
* **E2 ``frb_quality.csv``**: cover sizes and color counts against the exact
  optima, in the file's numbering and on randomly relabeled copies.
* **E3 ``scaling.csv``**: running time on random graphs G(n, 5n), n = 10^3..10^6.
* **E4 ``memory.csv``**: peak extra memory of every algorithm.
* **E5 ``worst_cases.csv``**: the graph families where the algorithms differ most.

Times are medians of repeated runs with the garbage collector paused; loading
and building the graphs are not timed. The FRB experiments are skipped for
instances that have not been downloaded (``python -m scripts.download_dataset``).

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, Sequence

from graph_heuristics.coloring import (
    color_count,
    greedy_coloring,
    is_proper_coloring,
    natural_coloring,
    smallest_last_coloring,
    smallest_last_order,
)
from graph_heuristics.datasets import (
    DATA_DIR,
    FAMILIES,
    FrbInstance,
    frb_instances,
    is_available,
    load_frb,
)
from graph_heuristics.experiment import median_time, peak_memory
from graph_heuristics.generators import (
    binomial_tree,
    complete_bipartite_graph,
    complete_graph,
    crown_graph,
    perfect_matching_graph,
    random_graph,
    random_relabeling,
    star_graph,
)
from graph_heuristics.graph import Graph
from graph_heuristics.vertex_cover import (
    basic_vertex_cover,
    is_vertex_cover,
    randomized_vertex_cover,
)

ROOT = Path(__file__).resolve().parent.parent
#: The timed algorithms, in display order (sl_order and sl_greedy split sl_coloring).
TIMED = ("basic_vc", "randomized_vc", "natural_coloring", "sl_coloring", "sl_order", "sl_greedy")
#: Graphs with more edges than this get fewer repeats and relabeled copies.
LARGE_M = 2_000_000


class Log:
    """Print progress to the console and to ``benchmark_log.txt``."""

    def __init__(self, path: Path) -> None:
        """Open the log file.

        Args:
            path: Where to write the log.
        """
        self._file = open(path, "w", encoding="utf-8")
        self._start = time.perf_counter()

    def __call__(self, message: str) -> None:
        """Write one line, prefixed with the elapsed time.

        Args:
            message: The text.
        """
        line = f"[{time.perf_counter() - self._start:7.1f} s] {message}"
        print(line, flush=True)
        self._file.write(line + "\n")
        self._file.flush()

    def close(self) -> None:
        """Close the log file."""
        self._file.close()


class CsvSink:
    """A CSV file written row by row (flushed after each row, so a crash keeps the data)."""

    def __init__(self, path: Path, fields: Sequence[str]) -> None:
        """Create the file and write the header.

        Args:
            path: The CSV file.
            fields: Column names.
        """
        self._file = open(path, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=list(fields))
        self._writer.writeheader()

    def write(self, row: dict) -> None:
        """Append one row.

        Args:
            row: Values keyed by column name.
        """
        self._writer.writerow(row)
        self._file.flush()

    def close(self) -> None:
        """Close the file."""
        self._file.close()


def timed_actions(graph: Graph) -> dict[str, Callable[[], object]]:
    """The zero-argument calls timed for one graph, keyed as in :data:`TIMED`.

    The smallest-last order is computed once here so that ``sl_greedy`` times
    the coloring pass alone.

    Args:
        graph: The graph.

    Returns:
        Mapping from algorithm name to a call that runs it on ``graph``.
    """
    order, _ = smallest_last_order(graph)
    return {
        "basic_vc": lambda: basic_vertex_cover(graph),
        "randomized_vc": lambda: randomized_vertex_cover(graph, 0),
        "natural_coloring": lambda: natural_coloring(graph),
        "sl_coloring": lambda: smallest_last_coloring(graph),
        "sl_order": lambda: smallest_last_order(graph),
        "sl_greedy": lambda: greedy_coloring(graph, order),
    }


def time_graph(graph: Graph, repeats: int) -> dict[str, tuple[float, list[float]]]:
    """Time every algorithm on one graph.

    Args:
        graph: The graph.
        repeats: Runs per algorithm.

    Returns:
        ``{name: (median seconds, all run times)}``.
    """
    results = {}
    for name, action in timed_actions(graph).items():
        _, median, times = median_time(action, repeats)
        results[name] = (median, times)
    return results


def frb_experiments(instances: list[FrbInstance], args: argparse.Namespace,
                    runtime: CsvSink, quality: CsvSink, log: Log) -> None:
    """E1 and E2: time every algorithm and measure its quality on each FRB graph.

    Args:
        instances: The downloaded instances to run.
        args: Command-line options (repeats, seeds, copies).
        runtime: Sink for ``frb_runtime.csv``.
        quality: Sink for ``frb_quality.csv``.
        log: Progress log.
    """
    for instance in instances:
        clq = load_frb(instance, "clq", args.data_dir)
        mis = clq.complement()
        for form, graph in (("clq", clq), ("mis", mis)):
            large = graph.m > LARGE_M
            repeats = max(1, args.repeats - 2) if large else args.repeats
            timings = time_graph(graph, repeats)
            for name in TIMED:
                median, times = timings[name]
                runtime.write({
                    "instance": instance.name, "family": instance.family, "form": form,
                    "n": graph.n, "m": graph.m, "algorithm": name, "repeats": repeats,
                    "median_s": f"{median:.6g}", "min_s": f"{min(times):.6g}",
                    "max_s": f"{max(times):.6g}",
                })
            log(f"E1 {instance.name:11} {form}  m={graph.m:>9,}  " + "  ".join(
                f"{name}={timings[name][0] * 1e3:.1f}ms" for name in TIMED[:4]))
        copies = max(1, args.copies - 2) if clq.m > LARGE_M else args.copies
        row = {"instance": instance.name, "family": instance.family, "n": clq.n,
               "m_clq": clq.m, "m_mis": mis.m, "groups": instance.groups,
               "group_size": instance.group_size, "copies": copies, "seeds": args.seeds}
        row.update(cover_quality(mis, instance.min_vertex_cover, args.seeds, copies))
        row.update(coloring_quality(clq, instance.chromatic_number, copies))
        quality.write(row)
        log(f"E2 {instance.name:11} VC/OPT basic={row['basic_file'] / row['opt_cover']:.4f} "
            f"rand={row['randomized_file_mean'] / row['opt_cover']:.4f}  colors natural="
            f"{row['natural_file']} ({row['natural_relabeled_mean']:.1f}) sl={row['sl_file']} "
            f"({row['sl_relabeled_mean']:.1f}) chi={row['chi']}")


def cover_quality(graph: Graph, opt: int, seeds: int, copies: int) -> dict:
    """E2 for vertex cover: sizes in file order and on relabeled copies.

    Args:
        graph: The ``mis`` form.
        opt: Its exact minimum vertex cover.
        seeds: Randomized runs in file order.
        copies: Number of relabeled copies.

    Returns:
        Columns of ``frb_quality.csv`` for vertex cover.

    Raises:
        AssertionError: If a cover is invalid.
    """
    basic = basic_vertex_cover(graph)
    assert is_vertex_cover(graph, basic)
    randomized = []
    for seed in range(seeds):
        cover = randomized_vertex_cover(graph, seed)
        assert is_vertex_cover(graph, cover)
        randomized.append(len(cover))
    basic_relabeled, randomized_relabeled = [], []
    for seed in range(copies):
        copy, _ = random_relabeling(graph, 1000 + seed)
        basic_relabeled.append(len(basic_vertex_cover(copy)))
        randomized_relabeled.append(len(randomized_vertex_cover(copy, seed)))
    return {
        "opt_cover": opt,
        "basic_file": len(basic),
        "randomized_file_mean": statistics.fmean(randomized),
        "randomized_file_std": statistics.pstdev(randomized),
        "randomized_file_min": min(randomized),
        "randomized_file_max": max(randomized),
        "basic_relabeled_mean": statistics.fmean(basic_relabeled),
        "basic_relabeled_min": min(basic_relabeled),
        "basic_relabeled_max": max(basic_relabeled),
        "randomized_relabeled_mean": statistics.fmean(randomized_relabeled),
        "randomized_relabeled_min": min(randomized_relabeled),
        "randomized_relabeled_max": max(randomized_relabeled),
    }


def coloring_quality(graph: Graph, chi: int, copies: int) -> dict:
    """E2 for coloring: color counts in file order and on relabeled copies.

    Args:
        graph: The ``clq`` form.
        chi: Its exact chromatic number.
        copies: Number of relabeled copies.

    Returns:
        Columns of ``frb_quality.csv`` for coloring, with the bounds
        Delta + 1 and degeneracy + 1.

    Raises:
        AssertionError: If a coloring is not proper.
    """
    natural = natural_coloring(graph)
    order, degeneracy = smallest_last_order(graph)
    sl = greedy_coloring(graph, order)
    assert is_proper_coloring(graph, natural) and is_proper_coloring(graph, sl)
    natural_relabeled, sl_relabeled = [], []
    for seed in range(copies):
        copy, _ = random_relabeling(graph, 2000 + seed)
        natural_relabeled.append(color_count(natural_coloring(copy)))
        sl_relabeled.append(color_count(smallest_last_coloring(copy)))
    return {
        "chi": chi,
        "max_degree": graph.max_degree(),
        "degeneracy": degeneracy,
        "natural_file": color_count(natural),
        "sl_file": color_count(sl),
        "natural_relabeled_mean": statistics.fmean(natural_relabeled),
        "natural_relabeled_min": min(natural_relabeled),
        "natural_relabeled_max": max(natural_relabeled),
        "sl_relabeled_mean": statistics.fmean(sl_relabeled),
        "sl_relabeled_min": min(sl_relabeled),
        "sl_relabeled_max": max(sl_relabeled),
    }


def scaling_sizes(max_n: int) -> list[int]:
    """The 1-2-5 ladder of vertex counts from 1,000 up to ``max_n``.

    Args:
        max_n: Largest n.

    Returns:
        Sizes 1000, 2000, 5000, 10000, ... not above ``max_n``.
    """
    sizes, base = [], 1_000
    while base <= max_n:
        sizes += [s for s in (base, 2 * base, 5 * base) if s <= max_n]
        base *= 10
    return sizes


def scaling_experiment(args: argparse.Namespace, sink: CsvSink, log: Log) -> None:
    """E3: time every algorithm on G(n, 5n) for growing n.

    Args:
        args: Command-line options (max_n, repeats).
        sink: Sink for ``scaling.csv``.
        log: Progress log.
    """
    for n in scaling_sizes(args.max_n):
        graph = random_graph(n, 5 * n, seed=n)
        repeats = args.repeats if n <= 200_000 else max(1, args.repeats - 2)
        timings = time_graph(graph, repeats)
        for name in TIMED:
            median, times = timings[name]
            sink.write({"n": n, "m": graph.m, "algorithm": name, "repeats": repeats,
                        "median_s": f"{median:.6g}", "min_s": f"{min(times):.6g}",
                        "max_s": f"{max(times):.6g}"})
        log(f"E3 n={n:>9,} m={graph.m:>10,}  " + "  ".join(
            f"{name}={timings[name][0] * 1e3:.1f}ms" for name in TIMED[:4]))


def memory_experiment(args: argparse.Namespace, sink: CsvSink, log: Log) -> None:
    """E4: peak extra memory of every algorithm on sparse and dense graphs.

    Args:
        args: Command-line options (quick, data_dir).
        sink: Sink for ``memory.csv``.
        log: Progress log.
    """
    sizes = [10_000, 100_000] if args.quick else [10_000, 100_000, 1_000_000]
    graphs = [(f"G(n,5n) n={n:,}", random_graph(n, 5 * n, seed=n)) for n in sizes]
    for name in ("frb30-15-1", "frb59-26-1"):
        instance = next(i for i in frb_instances() if i.name == name)
        if is_available(instance, args.data_dir) and not args.quick:
            graphs.append((f"{name} clq", load_frb(instance, "clq", args.data_dir)))
    for title, graph in graphs:
        for algorithm, action in timed_actions(graph).items():
            if algorithm in ("sl_greedy",):
                continue  # its order is allocated outside the call
            _, peak = peak_memory(action)
            sink.write({"graph": title, "n": graph.n, "m": graph.m, "algorithm": algorithm,
                        "peak_bytes": peak, "bytes_per_vertex": f"{peak / graph.n:.2f}"})
        log(f"E4 {title} done")


def worst_case_experiment(args: argparse.Namespace, sink: CsvSink, log: Log) -> None:
    """E5: the families where the two algorithms of each problem differ most.

    Args:
        args: Command-line options (seeds).
        sink: Sink for ``worst_cases.csv``.
        log: Progress log.
    """
    cover_cases = [
        ("perfect matching, 1000 edges", perfect_matching_graph(1000), 1000),
        ("complete bipartite K100,100", complete_bipartite_graph(100, 100), 100),
        ("star, 1000 leaves", star_graph(1000), 1),
        ("complete graph K50", complete_graph(50), 49),
    ]
    for title, graph, opt in cover_cases:
        sizes = [len(randomized_vertex_cover(graph, seed)) for seed in range(args.seeds)]
        sink.write({"problem": "vertex cover", "graph": title, "n": graph.n, "m": graph.m,
                    "optimum": opt, "first": len(basic_vertex_cover(graph)),
                    "second": f"{statistics.fmean(sizes):.2f}",
                    "second_min": min(sizes), "second_max": max(sizes)})
    color_cases = [
        ("crown graph, 200 vertices", crown_graph(100), 2),
        ("binomial tree B12, 4096 vertices", binomial_tree(12), 2),
        ("complete graph K50", complete_graph(50), 50),
    ]
    for title, graph, chi in color_cases:
        sl = color_count(smallest_last_coloring(graph))
        sink.write({"problem": "coloring", "graph": title, "n": graph.n, "m": graph.m,
                    "optimum": chi, "first": color_count(natural_coloring(graph)),
                    "second": sl, "second_min": sl, "second_max": sl})
    log("E5 worst cases done")


def environment(args: argparse.Namespace) -> dict:
    """Describe the machine and software for ``environment.json``.

    Args:
        args: Command-line options, recorded with the run.

    Returns:
        Python version, OS, CPU, git commit and the options.
    """
    cpu = platform.processor()
    if sys.platform == "win32":
        try:
            import winreg

            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        except OSError:
            pass
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "unknown"
    return {
        "date": datetime.now().isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "os": platform.platform(),
        "cpu": cpu,
        "logical_cpus": os.cpu_count(),
        "git_commit": commit,
        "options": {k: str(v) for k, v in vars(args).items()},
    }


def main(argv: Optional[list[str]] = None) -> int:
    """Command-line entry point.

    Args:
        argv: Arguments (default: ``sys.argv[1:]``).

    Returns:
        Exit status 0.
    """
    parser = argparse.ArgumentParser(description="Benchmark the vertex cover and coloring "
                                                 "algorithms.")
    parser.add_argument("--quick", action="store_true",
                        help="smallest FRB family, n up to 100,000: about 1 minute")
    parser.add_argument("--results", type=Path, help="output folder (default results/, "
                                                     "or results/quick/ with --quick)")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--families", nargs="+", choices=list(FAMILIES) + ["frb100-40"],
                        help="FRB families to run (default: all, or frb30-15 with --quick)")
    parser.add_argument("--repeats", type=int, help="timed runs per algorithm (default 5)")
    parser.add_argument("--seeds", type=int, default=30, help="randomized vertex cover runs")
    parser.add_argument("--copies", type=int, help="relabeled copies per FRB graph (default 5)")
    parser.add_argument("--max-n", type=int, help="largest n of the scaling experiment")
    parser.add_argument("--skip", nargs="+", default=[], choices=["frb", "scaling", "memory",
                                                                  "worst"])
    args = parser.parse_args(argv)
    args.results = args.results or ROOT / ("results/quick" if args.quick else "results")
    args.repeats = args.repeats or (3 if args.quick else 5)
    args.copies = args.copies or (3 if args.quick else 5)
    args.max_n = args.max_n or (100_000 if args.quick else 1_000_000)
    families = args.families or (["frb30-15"] if args.quick else None)

    args.results.mkdir(parents=True, exist_ok=True)
    log = Log(args.results / "benchmark_log.txt")
    env = environment(args)
    (args.results / "environment.json").write_text(json.dumps(env, indent=2) + "\n",
                                                   encoding="utf-8")
    log(f"{env['cpu']}, Python {env['python']}, {env['os']}, commit {env['git_commit']}")

    if "frb" not in args.skip:
        all_instances = frb_instances(families)
        instances = [i for i in all_instances if is_available(i, args.data_dir)]
        if len(instances) < len(all_instances):
            log(f"{len(all_instances) - len(instances)} FRB instance(s) not downloaded: "
                "skipped (python -m scripts.download_dataset)")
        runtime = CsvSink(args.results / "frb_runtime.csv", [
            "instance", "family", "form", "n", "m", "algorithm", "repeats", "median_s",
            "min_s", "max_s"])
        quality_fields = ["instance", "family", "n", "m_clq", "m_mis", "groups",
                          "group_size", "copies", "seeds"]
        quality_fields += list(cover_quality(Graph.from_edges(2, [(0, 1)]), 1, 1, 1))
        quality_fields += list(coloring_quality(Graph.from_edges(2, [(0, 1)]), 2, 1))
        quality = CsvSink(args.results / "frb_quality.csv", quality_fields)
        frb_experiments(instances, args, runtime, quality, log)
        runtime.close()
        quality.close()
    if "scaling" not in args.skip:
        sink = CsvSink(args.results / "scaling.csv",
                       ["n", "m", "algorithm", "repeats", "median_s", "min_s", "max_s"])
        scaling_experiment(args, sink, log)
        sink.close()
    if "memory" not in args.skip:
        sink = CsvSink(args.results / "memory.csv",
                       ["graph", "n", "m", "algorithm", "peak_bytes", "bytes_per_vertex"])
        memory_experiment(args, sink, log)
        sink.close()
    if "worst" not in args.skip:
        sink = CsvSink(args.results / "worst_cases.csv",
                       ["problem", "graph", "n", "m", "optimum", "first", "second",
                        "second_min", "second_max"])
        worst_case_experiment(args, sink, log)
        sink.close()
    log("done")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
