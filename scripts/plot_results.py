"""Turn the benchmark CSV files into figures, fitted slopes and a Markdown summary.

Usage (from the repository root)::

    python -m scripts.plot_results                          # reads results/
    python -m scripts.plot_results --results results/quick

Writes ``figures/*.png`` and ``figures/*.pdf``, ``slopes.csv`` and
``summary.md`` into the results folder. Experiments whose CSV is missing are
skipped.

Figure style: each panel compares the two algorithms of one problem. The first
algorithm (basic vertex cover, natural order) is blue with circles; the second
(randomized vertex cover, smallest-last) is orange with squares, so identity
never rests on color alone. The palette was checked for color-vision
deficiency. Filled markers are the published FRB graphs (``clq``), hollow
markers their complements (``mis``).

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (the backend must be chosen first)

from graph_heuristics.experiment import format_table, loglog_slope  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"  # categorical slots 1-3
INK, INK_2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"

#: Panels: (title, [(algorithm key, label, color, marker)]).
PANELS = [
    ("Vertex cover", [("basic_vc", "basic", BLUE, "o"),
                      ("randomized_vc", "randomized", ORANGE, "s")]),
    ("Graph coloring", [("natural_coloring", "natural order", BLUE, "o"),
                        ("sl_coloring", "smallest-last", ORANGE, "s")]),
]
#: Display names of every timed algorithm.
NAMES = {"basic_vc": "basic VC", "randomized_vc": "randomized VC",
         "natural_coloring": "greedy, natural order", "sl_coloring": "greedy, smallest-last",
         "sl_order": "smallest-last order only", "sl_greedy": "greedy pass along SL order"}


def style() -> None:
    """Apply the shared figure style: thin marks, recessive grid and axes."""
    plt.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 200, "font.size": 8.5,
        "axes.edgecolor": AXIS, "axes.labelcolor": INK, "axes.titlesize": 9,
        "axes.titleweight": "bold", "axes.grid": True, "grid.color": GRID,
        "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
        "xtick.color": INK_2, "ytick.color": INK_2, "legend.frameon": False,
        "lines.linewidth": 1.5, "lines.markersize": 4.5, "text.color": INK,
    })


def read_csv(path: Path) -> list[dict]:
    """Read a CSV file into a list of row dicts.

    Args:
        path: The file.

    Returns:
        The rows, or an empty list if the file does not exist.
    """
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def save(fig: plt.Figure, folder: Path, name: str) -> None:
    """Save a figure as PNG and PDF and close it.

    Args:
        fig: The figure.
        folder: The ``figures`` folder.
        name: File name without extension.
    """
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(folder / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)


def size_of(row: dict) -> int:
    """n + m of a result row.

    Args:
        row: A row with ``n`` and ``m``.

    Returns:
        n + m.
    """
    return int(row["n"]) + int(row["m"])


def runtime_figure(rows: list[dict], folder: Path, name: str,
                   by_form: bool) -> dict[str, float]:
    """Log-log running time against n + m, one panel per problem, with fitted slopes.

    Args:
        rows: Rows of ``frb_runtime.csv`` or ``scaling.csv``.
        folder: The ``figures`` folder.
        name: Output file name.
        by_form: Draw ``clq`` filled and ``mis`` hollow (FRB only).

    Returns:
        ``{algorithm: fitted log-log slope}`` for every timed algorithm.
    """
    slopes = {}
    for algorithm in NAMES:
        points = [(size_of(r), float(r["median_s"])) for r in rows if r["algorithm"] == algorithm]
        if len(points) >= 2:
            slopes[algorithm] = loglog_slope([p[0] for p in points], [p[1] for p in points])
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8), sharey=True)
    for ax, (panel, series) in zip(axes, PANELS):
        for key, label, color, marker in series:
            mine = [r for r in rows if r["algorithm"] == key]
            forms = ("clq", "mis") if by_form else ("",)
            for form in forms:
                part = [r for r in mine if not by_form or r["form"] == form]
                xs = [size_of(r) for r in part]
                ys = [float(r["median_s"]) for r in part]
                ax.plot(xs, ys, linestyle="none", marker=marker, color=color,
                        markerfacecolor=color if form != "mis" else "white",
                        markeredgewidth=1.0, alpha=0.9)
            if key in slopes:
                xs = sorted(size_of(r) for r in mine)
                ys = [float(r["median_s"]) for r in mine]
                fit = _fit_line(xs, [size_of(r) for r in mine], ys, slopes[key])
                ax.plot(xs, fit, color=color, linewidth=1.2,
                        label=f"{label} (slope {slopes[key]:.2f})")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(panel, loc="left")
        ax.set_xlabel("graph size n + m")
        ax.legend(loc="lower right")
    axes[0].set_ylabel("running time (s)")
    if by_form:
        handles = [
            plt.Line2D([], [], linestyle="none", marker="o", color=MUTED,
                       label="filled: published graph (clq)"),
            plt.Line2D([], [], linestyle="none", marker="o", color=MUTED,
                       markerfacecolor="white", label="hollow: complement (mis)"),
        ]
        fig.legend(handles=handles, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.06))
    save(fig, folder, name)
    return slopes


def _fit_line(xs_sorted: list[int], xs: list[int], ys: list[float], slope: float) -> list[float]:
    """The least-squares power law y = c x^slope evaluated at ``xs_sorted``.

    Args:
        xs_sorted: Where to evaluate the fit.
        xs: Measured sizes.
        ys: Measured times.
        slope: The fitted exponent.

    Returns:
        Fitted times at ``xs_sorted``.
    """
    import math

    log_c = statistics.fmean(math.log(y) - slope * math.log(x) for x, y in zip(xs, ys))
    return [math.exp(log_c) * x**slope for x in xs_sorted]


def per_element_figure(rows: list[dict], folder: Path) -> None:
    """Nanoseconds per (n + m) on the synthetic graphs: flat lines mean linear time.

    Args:
        rows: Rows of ``scaling.csv``.
        folder: The ``figures`` folder.
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.4))
    for ax, (panel, series) in zip(axes, PANELS):
        for key, label, color, marker in series:
            mine = sorted((r for r in rows if r["algorithm"] == key), key=size_of)
            ax.plot([size_of(r) for r in mine],
                    [float(r["median_s"]) * 1e9 / size_of(r) for r in mine],
                    marker=marker, color=color, label=label)
        ax.set_xscale("log")
        ax.set_ylim(bottom=0)
        ax.set_title(panel, loc="left")
        ax.set_xlabel("graph size n + m (random graphs, m = 5n)")
        # Empty regions: below the vertex cover lines, between the coloring lines.
        ax.legend(loc="lower right" if panel == "Vertex cover" else "center right")
    axes[0].set_ylabel("ns per (n + m)")
    save(fig, folder, "scaling_per_element")


def family_order(rows: list[dict]) -> list[str]:
    """The FRB families present in ``rows``, smallest first.

    Args:
        rows: Rows with ``family`` and ``n``.

    Returns:
        Family names sorted by vertex count.
    """
    sizes = {r["family"]: int(r["n"]) for r in rows}
    return sorted(sizes, key=sizes.get)


def quality_figure(rows: list[dict], folder: Path, problem: str) -> None:
    """Solution quality per FRB family against the exact optimum.

    Args:
        rows: Rows of ``frb_quality.csv``.
        folder: The ``figures`` folder.
        problem: ``"cover"`` (cover size / OPT on the mis form) or ``"coloring"``
            (colors / chi on the clq form).
    """
    families = family_order(rows)
    if problem == "cover":
        optimum = "opt_cover"
        series = [("basic", "basic_file", "basic_relabeled", BLUE, "o"),
                  ("randomized", "randomized_file_mean", "randomized_relabeled", ORANGE, "s")]
        ylabel, name = "cover size / minimum cover", "vc_quality"
    else:
        optimum = "chi"
        series = [("natural order", "natural_file", "natural_relabeled", BLUE, "o"),
                  ("smallest-last", "sl_file", "sl_relabeled", ORANGE, "s")]
        ylabel, name = "colors / chromatic number", "coloring_quality"
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    xs = range(len(families))
    for offset, (label, file_key, relabeled_key, color, marker) in zip((-0.16, 0.16), series):
        file_ratio, mean_ratio, low, high = [], [], [], []
        for family in families:
            mine = [r for r in rows if r["family"] == family]
            opt = [float(r[optimum]) for r in mine]
            file_ratio.append(statistics.fmean(float(r[file_key]) / o for r, o in zip(mine, opt)))
            mean_ratio.append(statistics.fmean(
                float(r[relabeled_key + "_mean"]) / o for r, o in zip(mine, opt)))
            low.append(min(float(r[relabeled_key + "_min"]) / o for r, o in zip(mine, opt)))
            high.append(max(float(r[relabeled_key + "_max"]) / o for r, o in zip(mine, opt)))
        positions = [x + offset + 0.06 for x in xs]
        ax.errorbar(positions, mean_ratio,
                    yerr=[[m - lo for m, lo in zip(mean_ratio, low)],
                          [hi - m for m, hi in zip(mean_ratio, high)]],
                    fmt=marker, color=color, ecolor=color, elinewidth=1.0, capsize=2,
                    label=f"{label}, relabeled (mean, min-max)")
        ax.plot([x + offset - 0.06 for x in xs], file_ratio, linestyle="none",
                marker=marker, color=color,
                markerfacecolor="white", markeredgewidth=1.0, label=f"{label}, file order")
    if problem == "cover":
        ceiling = [statistics.fmean(int(r["n"]) / float(r["opt_cover"])
                                    for r in rows if r["family"] == f) for f in families]
        ax.plot(xs, ceiling, linestyle="none", marker="_", markersize=22, color=MUTED,
                markeredgewidth=1.5, label="n / OPT (largest possible)")
    else:
        ax.axhline(1.0, color=MUTED, linewidth=1.0, linestyle="--", label="optimum (chi)")
        ax.set_ylim(bottom=0)
    ax.set_xlim(-0.5, len(families) - 0.5)
    ax.grid(axis="x", visible=False)  # categories need no vertical lines
    ax.set_xticks(list(xs), families)
    ax.set_ylabel(ylabel)
    handles, labels = ax.get_legend_handles_labels()
    # Column 1: file order and the reference; column 2: relabeled copies.
    order = sorted(range(len(labels)), key=lambda i: ("relabeled" in labels[i], i))
    ax.legend([handles[i] for i in order], [labels[i] for i in order], loc="upper center",
              bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=7.5)
    save(fig, folder, name)


def sl_split_figure(rows: list[dict], folder: Path) -> None:
    """Time of natural coloring against the two passes of smallest-last coloring (clq form).

    Args:
        rows: Rows of ``frb_runtime.csv``.
        folder: The ``figures`` folder.
    """
    families = family_order(rows)
    keys = [("natural_coloring", "greedy, natural order", BLUE),
            ("sl_order", "smallest-last: ordering", ORANGE),
            ("sl_greedy", "smallest-last: greedy pass", AQUA)]
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    width = 0.26
    for i, (key, label, color) in enumerate(keys):
        values = []
        for family in families:
            mine = [r for r in rows if r["family"] == family and r["form"] == "clq"
                    and r["algorithm"] == key]
            values.append(statistics.fmean(float(r["median_s"]) * 1e9 / size_of(r)
                                           for r in mine))
        ax.bar([x + (i - 1) * (width + 0.02) for x in range(len(families))], values,
               width=width, color=color, label=label)
    ax.set_xticks(range(len(families)), families)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("ns per (n + m)")
    ax.set_title("Where smallest-last coloring spends its time (clq form)", loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    save(fig, folder, "sl_split")


def summary_tables(results: Path, runtime: list[dict], scaling: list[dict],
                   quality: list[dict], memory: list[dict], worst: list[dict],
                   slopes: dict[str, dict[str, float]]) -> str:
    """Build ``summary.md``: every table the report draws on.

    Args:
        results: The results folder (for the title).
        runtime, scaling, quality, memory, worst: The CSV rows.
        slopes: ``{experiment: {algorithm: slope}}``.

    Returns:
        The Markdown text.
    """
    parts = [f"# Benchmark summary ({results.name})\n"]
    if slopes:
        rows = [[NAMES[a]] + [f"{slopes[e][a]:.2f}" if a in slopes[e] else "" for e in slopes]
                for a in NAMES]
        parts.append("## Log-log slopes of time against n + m (1 = linear)\n\n```\n"
                     + format_table(["algorithm"] + list(slopes), rows) + "\n```\n")
    if runtime:
        table = []
        for family in family_order(runtime):
            for form in ("clq", "mis"):
                mine = [r for r in runtime if r["family"] == family and r["form"] == form]
                if not mine:
                    continue
                cell = defaultdict(list)
                for r in mine:
                    cell[r["algorithm"]].append(float(r["median_s"]))
                m = statistics.fmean(int(r["m"]) for r in mine)
                table.append([family, form, f"{m:,.0f}"] + [
                    f"{statistics.fmean(cell[a]) * 1e3:.1f}" for a in NAMES])
        parts.append("## FRB running time (ms, mean of the instances' medians)\n\n```\n"
                     + format_table(["family", "form", "m", *NAMES], table) + "\n```\n")
    if quality:
        table = []
        for family in family_order(quality):
            mine = [r for r in quality if r["family"] == family]

            def mean(key: str) -> float:
                """Mean of one column over the family's instances."""
                return statistics.fmean(float(r[key]) for r in mine)
            table.append([
                family, f"{mean('opt_cover'):.0f}", f"{mean('basic_file'):.1f}",
                f"{mean('basic_relabeled_mean'):.1f}", f"{mean('randomized_file_mean'):.1f}",
                f"{mean('randomized_relabeled_mean'):.1f}", f"{mean('chi'):.0f}",
                f"{mean('natural_file'):.1f}", f"{mean('natural_relabeled_mean'):.1f}",
                f"{mean('sl_file'):.1f}", f"{mean('sl_relabeled_mean'):.1f}",
                f"{mean('degeneracy') + 1:.0f}", f"{mean('max_degree') + 1:.0f}"])
        parts.append(
            "## FRB solution quality (mean over the family's instances)\n\n"
            "Vertex cover on the mis form (OPT exact); colors on the clq form (chi exact). "
            "`file` = the file's numbering, `relab` = mean over randomly relabeled copies.\n\n"
            "```\n" + format_table(
                ["family", "OPT", "basic file", "basic relab", "rand file", "rand relab",
                 "chi", "natural file", "natural relab", "SL file", "SL relab", "d+1",
                 "Delta+1"], table) + "\n```\n")
    if memory:
        table = [[r["graph"], f"{int(r['n']):,}", f"{int(r['m']):,}", NAMES[r["algorithm"]],
                  f"{int(r['peak_bytes']) / 1024:,.0f}", r["bytes_per_vertex"]] for r in memory]
        parts.append("## Peak extra memory (tracemalloc)\n\n```\n" + format_table(
            ["graph", "n", "m", "algorithm", "KiB", "bytes/vertex"], table) + "\n```\n")
    if worst:
        table = [[r["problem"], r["graph"], r["optimum"], r["first"], r["second"],
                  f"{r['second_min']}-{r['second_max']}"] for r in worst]
        parts.append("## Worst cases (first = basic VC / natural order; second = randomized "
                     "VC mean / smallest-last)\n\n```\n" + format_table(
                         ["problem", "graph", "optimum", "first", "second", "range"], table)
                     + "\n```\n")
    return "\n".join(parts)


def main(argv: Optional[list[str]] = None) -> int:
    """Command-line entry point.

    Args:
        argv: Arguments (default: ``sys.argv[1:]``).

    Returns:
        Exit status 0.
    """
    parser = argparse.ArgumentParser(description="Plot the benchmark results.")
    parser.add_argument("--results", type=Path, default=ROOT / "results")
    args = parser.parse_args(argv)
    folder = args.results / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    style()

    runtime = read_csv(args.results / "frb_runtime.csv")
    scaling = read_csv(args.results / "scaling.csv")
    quality = read_csv(args.results / "frb_quality.csv")
    memory = read_csv(args.results / "memory.csv")
    worst = read_csv(args.results / "worst_cases.csv")
    slopes: dict[str, dict[str, float]] = {}
    if runtime:
        slopes["FRB (both forms)"] = runtime_figure(runtime, folder, "frb_runtime", by_form=True)
        sl_split_figure(runtime, folder)
    if scaling:
        slopes["random G(n, 5n)"] = runtime_figure(scaling, folder, "scaling", by_form=False)
        per_element_figure(scaling, folder)
    if quality:
        quality_figure(quality, folder, "cover")
        quality_figure(quality, folder, "coloring")
    with open(args.results / "slopes.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["experiment", "algorithm", "slope"])
        for experiment, values in slopes.items():
            for algorithm, slope in values.items():
                writer.writerow([experiment, algorithm, f"{slope:.4f}"])
    summary = summary_tables(args.results, runtime, scaling, quality, memory, worst, slopes)
    (args.results / "summary.md").write_text(summary, encoding="utf-8")
    print(f"wrote {folder} and {args.results / 'summary.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
