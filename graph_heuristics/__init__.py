"""Vertex cover and graph coloring heuristics implemented from scratch.

Vertex cover: the basic 2-approximation (both endpoints of an uncovered edge)
and its randomized version (one endpoint chosen at random). Graph coloring:
greedy coloring along the natural vertex order and along the smallest-last
order. All four run in O(n + m) time on the :class:`Graph` defined in
``graph.py``.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""
