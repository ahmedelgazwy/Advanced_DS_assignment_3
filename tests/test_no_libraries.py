"""The algorithms are implemented by hand: no graph or numeric library is imported.

The assignment forbids library implementations of the algorithms. This test
parses every module of the package and fails if one imports a graph library
(networkx, igraph, ...) or a numeric package (numpy, scipy). Plotting, which
is not part of the algorithms, may use matplotlib in ``scripts/``.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN = {"networkx", "igraph", "graph_tool", "rustworkx", "snap", "numpy", "scipy",
             "sklearn", "pandas", "sage"}
SOURCES = sorted((ROOT / "graph_heuristics").glob("*.py")) + [ROOT / "demo.py"]


def imported_modules(path: Path) -> set[str]:
    """The top-level names of every module imported by a source file."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


@pytest.mark.parametrize("path", SOURCES, ids=lambda p: p.name)
def test_no_library_imports(path: Path) -> None:
    assert not imported_modules(path) & FORBIDDEN
