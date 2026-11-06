# Vertex Cover and Graph Coloring Heuristics — COSC 520 Assignment 3

Work in progress. See [docs/plan.md](docs/plan.md) for the plan.

This project implements, from scratch in Python, two algorithms for minimum
vertex cover (the basic 2-approximation and its randomized version) and two for
graph coloring (greedy coloring in natural order and in smallest-last order),
and benchmarks them on the BHOSLIB/FRB graphs.

## Setup

Requires **Python 3.10 or newer**. Run the commands from the repository root.

```bash
python -m venv .venv                     # Windows: py -3.10 -m venv .venv
source .venv/bin/activate                # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
```
