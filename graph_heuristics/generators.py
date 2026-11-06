"""Graph generators: random graphs, planted FRB-like graphs and worst-case families.

* :func:`random_graph`: uniform G(n, m), used for the scaling benchmark.
* :func:`planted_graph`: a small graph with the same known optima as the FRB
  benchmark graphs, so the tests and the demo need no download.
* Small families with known answers, used by the tests and the demo:
  paths, cycles, stars, complete and complete bipartite graphs, perfect
  matchings, and two graphs on which the natural greedy order is as bad as
  possible: the crown graph and the binomial tree.

Every generator is deterministic (random ones take a seed) and iterative.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import random

from graph_heuristics.graph import Graph


def random_graph(n: int, m: int, seed: int = 0) -> Graph:
    """A uniform random graph G(n, m): m distinct edges chosen uniformly.

    Edges are listed in the (random) order they were drawn.

    Args:
        n: Number of vertices.
        m: Number of edges, at most n(n - 1)/4 (keeps rejection sampling fast).
        seed: Random seed.

    Returns:
        The graph.

    Raises:
        ValueError: If m is negative or larger than n(n - 1)/4.

    Complexity: O(n + m) expected time; O(m) extra space for the set of keys.
    """
    if m < 0 or 4 * m > n * (n - 1):
        raise ValueError(f"m must be in 0..n(n-1)/4 = {n * (n - 1) // 4}, got {m}")
    rng = random.Random(seed)
    below = rng.randrange
    keys: set[int] = set()
    edges = []
    while len(edges) < m:
        u, v = below(n), below(n)
        if u == v:
            continue
        key = u * n + v if u < v else v * n + u
        if key not in keys:
            keys.add(key)
            edges.append((u, v))
    return Graph.from_edges(n, edges)


def planted_graph(groups: int, size: int, density: float, seed: int = 0) -> tuple[Graph, list[int]]:
    """A small FRB-like graph whose chromatic number is exactly ``groups``.

    Vertices ``g*size .. g*size + size - 1`` form group g, as in the FRB
    files. Groups are independent sets (no edges inside a group), so coloring
    each group with its own color is proper: chi <= groups. One hidden vertex
    per group is joined to every other hidden vertex, so the graph contains a
    clique of size ``groups``: chi >= groups. Every other pair of vertices in
    different groups is joined with probability ``density``.

    The complement has the other FRB property: its groups are cliques, the
    hidden vertices are independent, and its minimum vertex cover has exactly
    ``groups * (size - 1)`` vertices.

    Args:
        groups: Number of groups, N.
        size: Vertices per group, K.
        density: Probability of each non-hidden edge between groups.
        seed: Random seed.

    Returns:
        ``(graph, hidden)``: the graph and the hidden clique (one vertex per
        group, in group order).

    Complexity: O((N K)^2) time.
    """
    rng = random.Random(seed)
    n = groups * size
    hidden = [g * size + rng.randrange(size) for g in range(groups)]
    is_hidden = bytearray(n)
    for v in hidden:
        is_hidden[v] = 1
    edges = []
    for u in range(n):
        for v in range((u // size + 1) * size, n):  # vertices of later groups
            if (is_hidden[u] and is_hidden[v]) or rng.random() < density:
                edges.append((u, v))
    return Graph.from_edges(n, edges), hidden


def path_graph(n: int) -> Graph:
    """The path 0 - 1 - ... - (n-1).

    Args:
        n: Number of vertices.

    Returns:
        A graph with n - 1 edges (none if n <= 1).
    """
    return Graph.from_edges(n, ((i, i + 1) for i in range(n - 1)))


def cycle_graph(n: int) -> Graph:
    """The cycle 0 - 1 - ... - (n-1) - 0.

    Args:
        n: Number of vertices, at least 3.

    Returns:
        A graph with n edges.

    Raises:
        ValueError: If n < 3.
    """
    if n < 3:
        raise ValueError(f"a cycle needs at least 3 vertices, got {n}")
    return Graph.from_edges(n, ((i, (i + 1) % n) for i in range(n)))


def star_graph(leaves: int) -> Graph:
    """The star K_{1,leaves}: center 0 joined to vertices 1..leaves.

    Args:
        leaves: Number of leaves.

    Returns:
        A graph with leaves + 1 vertices; its minimum vertex cover is {0}.
    """
    return Graph.from_edges(leaves + 1, ((0, i) for i in range(1, leaves + 1)))


def complete_graph(n: int) -> Graph:
    """The complete graph K_n.

    Args:
        n: Number of vertices.

    Returns:
        A graph with n(n - 1)/2 edges; chi = n and OPT vertex cover = n - 1.
    """
    return Graph.from_edges(n, ((u, v) for u in range(n) for v in range(u + 1, n)))


def complete_bipartite_graph(left: int, right: int) -> Graph:
    """The complete bipartite graph K_{left,right}.

    Vertices 0..left-1 form one side and left..left+right-1 the other.

    Args:
        left: Size of the first side.
        right: Size of the second side.

    Returns:
        A graph with left * right edges; OPT vertex cover = min(left, right).
    """
    n = left + right
    return Graph.from_edges(n, ((u, v) for u in range(left) for v in range(left, n)))


def perfect_matching_graph(pairs: int) -> Graph:
    """``pairs`` disjoint edges (0, 1), (2, 3), ...

    The basic vertex cover takes all 2 * pairs vertices, twice the optimum
    of ``pairs``; the randomized one is always optimal here.

    Args:
        pairs: Number of edges.

    Returns:
        A graph with 2 * pairs vertices.
    """
    return Graph.from_edges(2 * pairs, ((2 * i, 2 * i + 1) for i in range(pairs)))


def crown_graph(k: int) -> Graph:
    """The crown graph: K_{k,k} minus a perfect matching, numbered to fool greedy.

    Vertex 2i is a_i and vertex 2i + 1 is b_i; a_i is joined to every b_j
    with j != i. The graph is bipartite (2 colors suffice), but greedy
    coloring in natural order (a_0, b_0, a_1, b_1, ...) gives a_i and b_i
    color i, so it uses k colors.

    Args:
        k: Number of vertices per side, at least 1.

    Returns:
        A graph with 2k vertices and k(k - 1) edges.
    """
    return Graph.from_edges(
        2 * k, ((2 * i, 2 * j + 1) for i in range(k) for j in range(k) if i != j)
    )


def binomial_tree(order: int) -> Graph:
    """The binomial tree B_order, numbered so that natural greedy coloring is worst.

    B_0 is one vertex; B_k is two copies of B_{k-1} with an edge joining
    their roots. The vertices are numbered so that the first copy comes
    first and each root is numbered last. Greedy coloring in natural order
    then gives the root of B_k color k, so it uses order + 1 = log2(n) + 1
    colors on a tree, which needs only 2 [Gyarfas & Lehel 1988].

    Args:
        order: k >= 0; the tree has 2^k vertices.

    Returns:
        The tree; its root is vertex 2^k - 1.

    Complexity: O(2^k) time and space.
    """
    edges: list[tuple[int, int]] = []
    size = 1
    for _ in range(order):
        edges += [(u + size, v + size) for u, v in edges]  # second copy
        edges.append((size - 1, 2 * size - 1))  # join the two roots
        size *= 2
    return Graph.from_edges(size, edges)


def random_tree(n: int, seed: int = 0) -> Graph:
    """A random tree: vertex i > 0 is joined to a random earlier vertex.

    Args:
        n: Number of vertices.
        seed: Random seed.

    Returns:
        A tree with n - 1 edges (degeneracy 1 when n >= 2).
    """
    rng = random.Random(seed)
    return Graph.from_edges(n, ((rng.randrange(i), i) for i in range(1, n)))
