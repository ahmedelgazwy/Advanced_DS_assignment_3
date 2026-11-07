"""Live comparison of the two vertex cover and the two graph coloring algorithms.

Usage (from the repository root)::

    python demo.py                          # about 10 s
    python demo.py --instance frb35-17-1 --seeds 50
    python demo.py --quick                  # smaller graphs, about 2 s

Three parts:

1. **How they work**: a small graph, both covers, both colorings, and the
   smallest-last removal sequence with each vertex's degree when removed.
2. **Where they differ**: graphs on which one algorithm is as bad as its
   worst case and the other is optimal.
3. **A real benchmark graph**: an FRB instance against its exact optima
   (minimum vertex cover of the complement, chromatic number of the graph).
   If the instance has not been downloaded, a generated graph with the same
   structure is used instead.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import argparse
import statistics
import sys
from typing import Optional

from graph_heuristics.coloring import (
    COLORING_ALGORITHMS,
    color_count,
    greedy_coloring,
    is_proper_coloring,
    max_back_degree,
    smallest_last_order,
)
from graph_heuristics.datasets import is_available, load_frb, parse_instance
from graph_heuristics.experiment import format_table, measure
from graph_heuristics.generators import (
    binomial_tree,
    complete_bipartite_graph,
    complete_graph,
    crown_graph,
    perfect_matching_graph,
    planted_graph,
    random_relabeling,
    star_graph,
)
from graph_heuristics.graph import Graph
from graph_heuristics.vertex_cover import (
    basic_vertex_cover,
    is_vertex_cover,
    randomized_vertex_cover,
)

#: The small graph of part 1: a "house" (square 0-1-3-2 with roof 4) plus a tail 5-6-7.
HOUSE_EDGES = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 4), (3, 5), (5, 6), (6, 7)]


def heading(title: str) -> None:
    """Print a section heading.

    Args:
        title: The heading text.
    """
    print(f"\n{title}\n{'=' * len(title)}")


def mean_randomized_cover(graph: Graph, seeds: int) -> tuple[float, int, int]:
    """Run the randomized vertex cover with seeds 0..seeds-1.

    Args:
        graph: The graph.
        seeds: Number of runs.

    Returns:
        ``(mean, min, max)`` cover size.
    """
    sizes = []
    for seed in range(seeds):
        cover = randomized_vertex_cover(graph, seed)
        assert is_vertex_cover(graph, cover)
        sizes.append(len(cover))
    return statistics.fmean(sizes), min(sizes), max(sizes)


def part_how_they_work() -> None:
    """Part 1: both algorithms of each problem on a small hand-checkable graph."""
    heading("Part 1. How they work: a house with a tail")
    graph = Graph.from_edges(8, HOUSE_EDGES)
    print("Edges, in input order:", ", ".join(f"{u}-{v}" for u, v in graph.edges()))

    basic = basic_vertex_cover(graph)
    pairs = ", ".join(f"({basic[i]}, {basic[i + 1]})" for i in range(0, len(basic), 2))
    print(f"\nBasic vertex cover:      {sorted(basic)}  size {len(basic)}"
          f"  (selected edges {pairs})")
    for seed in (1, 2):
        cover = randomized_vertex_cover(graph, seed)
        print(f"Randomized, seed {seed}:      {sorted(cover)}  size {len(cover)}"
              f"  (one endpoint per selected edge)")

    order, degeneracy = smallest_last_order(graph)
    removal = list(reversed(order))
    alive = set(range(graph.n))
    steps = []
    for v in removal:
        steps.append(f"{v}(deg {sum(u in alive for u in graph.neighbors(v))})")
        alive.remove(v)
    print("\nSmallest-last: remove a vertex of minimum degree, repeatedly:")
    print("  removal sequence:", " ".join(steps))
    print(f"  coloring order = the reverse: {order}")
    print(f"  degeneracy d = {degeneracy} (largest degree at removal), so at most d + 1 = "
          f"{degeneracy + 1} colors")

    for name, algorithm in COLORING_ALGORITHMS.items():
        colors = algorithm(graph)
        print(f"{name:>14} coloring: {colors}  -> {color_count(colors)} colors"
              f"{'' if is_proper_coloring(graph, colors) else '  INVALID'}")


def part_where_they_differ(quick: bool, seeds: int) -> None:
    """Part 2: graphs that separate the two algorithms of each problem.

    Args:
        quick: Use smaller graphs.
        seeds: Runs of the randomized vertex cover per graph.
    """
    heading("Part 2. Where they differ")
    k = 20 if quick else 100
    cover_cases = [
        (f"perfect matching, {k} edges", perfect_matching_graph(k), k),
        (f"complete bipartite K{k // 5},{k // 5}",
         complete_bipartite_graph(k // 5, k // 5), k // 5),
        (f"star with {k} leaves", star_graph(k), 1),
        ("complete graph K12", complete_graph(12), 11),
    ]
    rows = []
    for title, graph, opt in cover_cases:
        basic = basic_vertex_cover(graph)
        assert is_vertex_cover(graph, basic)
        mean, low, high = mean_randomized_cover(graph, seeds)
        rows.append([title, opt, len(basic), f"{len(basic) / opt:.2f}",
                     f"{mean:.1f} ({low}-{high})", f"{mean / opt:.2f}"])
    print(f"Vertex cover (randomized: mean and range over {seeds} seeds):\n")
    print(format_table(["graph", "OPT", "basic", "ratio", "randomized", "ratio"], rows))

    tree_order = 7 if quick else 12
    crown_k = 20 if quick else 100
    color_cases = [
        (f"crown graph, {2 * crown_k} vertices", crown_graph(crown_k), 2),
        (f"binomial tree B{tree_order}, {2 ** tree_order} vertices",
         binomial_tree(tree_order), 2),
        ("complete graph K12", complete_graph(12), 12),
    ]
    rows = []
    for title, graph, chi in color_cases:
        counts = []
        for algorithm in COLORING_ALGORITHMS.values():
            colors = algorithm(graph)
            assert is_proper_coloring(graph, colors)
            counts.append(color_count(colors))
        _, degeneracy = smallest_last_order(graph)
        rows.append([title, chi, graph.max_degree() + 1, degeneracy + 1, *counts])
    print("\nColoring (number of colors; chi = optimum):\n")
    print(format_table(["graph", "chi", "Delta+1", "d+1", "natural", "smallest-last"], rows))
    print("\nThe crown graph and the binomial tree are numbered so that the natural order\n"
          "is as bad as possible; smallest-last ignores the numbering.")


def part_real_graph(instance_name: str, seeds: int, quick: bool) -> None:
    """Part 3: an FRB instance against its exact optima.

    Args:
        instance_name: FRB instance, e.g. ``frb30-15-1``.
        seeds: Runs of the randomized vertex cover.
        quick: Use a smaller generated graph if the instance is missing.
    """
    instance = parse_instance(instance_name)
    groups, size = instance.groups, instance.group_size
    if is_available(instance):
        title = f"{instance_name} (BHOSLIB, Network Repository)"
        clq = load_frb(instance, "clq")
    else:
        if quick:
            groups, size = 10, 6
        title = (f"a generated FRB-like graph, {groups} groups of {size} "
                 f"({instance_name} not downloaded: python -m scripts.download_dataset)")
        clq, _ = planted_graph(groups, size, density=0.82, seed=1)
    mis = clq.complement()
    opt_cover = groups * size - groups
    copies = 3 if quick else 5
    heading(f"Part 3. A real benchmark graph: {title}")
    print(f"'file order' uses the numbering of the file; 'relabeled' is the mean over {copies}\n"
          "copies with random vertex numbers and edge order (range in brackets).")

    def summary(values: list[int], scale: int) -> list[str]:
        """Format sizes as "mean (min-max)" and the mean divided by the optimum.

        Args:
            values: Cover sizes or color counts.
            scale: The optimum to divide by.

        Returns:
            ``[mean text, ratio text]``.
        """
        mean = statistics.fmean(values)
        text = f"{mean:.1f} ({min(values)}-{max(values)})" if len(values) > 1 else str(values[0])
        return [text, f"{mean / scale:.3f}"]

    relabeled_mis = [random_relabeling(mis, seed)[0] for seed in range(copies)]
    print(f"\nVertex cover of the complement (n = {mis.n}, m = {mis.m:,}); "
          f"exact minimum = {opt_cover}\n")
    basic, basic_s = measure(lambda: basic_vertex_cover(mis))
    assert is_vertex_cover(mis, basic)
    random_sizes, random_times = [], []
    for seed in range(seeds):
        cover, seconds = measure(lambda: randomized_vertex_cover(mis, seed))
        assert is_vertex_cover(mis, cover)
        random_sizes.append(len(cover))
        random_times.append(seconds)
    rows = [
        ["basic", "file order", *summary([len(basic)], opt_cover), f"{basic_s * 1e3:.1f}"],
        ["basic", "relabeled",
         *summary([len(basic_vertex_cover(g)) for g in relabeled_mis], opt_cover), ""],
        ["randomized", f"file order, {seeds} seeds", *summary(random_sizes, opt_cover),
         f"{statistics.median(random_times) * 1e3:.1f}"],
        ["randomized", "relabeled", *summary(
            [len(randomized_vertex_cover(g, seed)) for seed, g in enumerate(relabeled_mis)],
            opt_cover), ""],
    ]
    print(format_table(["algorithm", "numbering", "cover size", "size / OPT", "time (ms)"],
                       rows))
    print(f"Any cover is at most n / OPT = {mis.n / opt_cover:.3f} times the optimum here.")

    relabeled_clq = [random_relabeling(clq, seed)[0] for seed in range(copies)]
    print(f"\nColoring the graph (n = {clq.n}, m = {clq.m:,}); "
          f"exact chromatic number = {groups}\n")
    (order, degeneracy), order_s = measure(lambda: smallest_last_order(clq))
    natural, natural_s = measure(lambda: COLORING_ALGORITHMS["natural"](clq))
    sl_colors, sl_color_s = measure(lambda: greedy_coloring(clq, order))
    assert is_proper_coloring(clq, natural) and is_proper_coloring(clq, sl_colors)
    rows = []
    for name, file_colors, seconds in (("natural", natural, natural_s),
                                       ("smallest-last", sl_colors, order_s + sl_color_s)):
        algorithm = COLORING_ALGORITHMS["natural" if name == "natural" else "smallest_last"]
        rows.append([name, "file order", *summary([color_count(file_colors)], groups),
                     f"{seconds * 1e3:.1f}"])
        rows.append([name, "relabeled", *summary(
            [color_count(algorithm(g)) for g in relabeled_clq], groups), ""])
    print(format_table(["algorithm", "numbering", "colors", "colors / chi", "time (ms)"],
                       rows))
    print(f"Bounds: Delta + 1 = {clq.max_degree() + 1}, degeneracy + 1 = {degeneracy + 1} "
          f"(largest back degree of the smallest-last order: {max_back_degree(clq, order)}).")
    print(f"Smallest-last time = {order_s * 1e3:.1f} ms ordering + {sl_color_s * 1e3:.1f} ms "
          "coloring.")
    print("\nThe file numbers the vertices group by group, and each group is an independent\n"
          "set, so in file order greedy coloring recovers the planted coloring. On relabeled\n"
          "copies, where the order is truly arbitrary, smallest-last uses far fewer colors.")


def main(argv: Optional[list[str]] = None) -> int:
    """Command-line entry point.

    Args:
        argv: Arguments (default: ``sys.argv[1:]``).

    Returns:
        Exit status 0.
    """
    parser = argparse.ArgumentParser(description="Compare the vertex cover and coloring "
                                                 "algorithms.")
    parser.add_argument("--instance", default="frb30-15-1", help="FRB instance for part 3")
    parser.add_argument("--seeds", type=int, default=30, help="randomized vertex cover runs")
    parser.add_argument("--quick", action="store_true", help="smaller graphs")
    args = parser.parse_args(argv)
    part_how_they_work()
    part_where_they_differ(args.quick, args.seeds)
    part_real_graph(args.instance, args.seeds, args.quick)
    return 0


if __name__ == "__main__":
    sys.exit(main())
