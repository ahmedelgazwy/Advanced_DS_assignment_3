# Author tasks (decision D2)

These are the parts of the assignment the author writes, so that the
report and the README can show which code is the author's (course GenAI
policy). Everything around them is already in place, including the unit tests
that check them.

| # | Task | File | Check with | When |
|---|---|---|---|---|
| 1 | Body of `basic_vertex_cover` | `graph_heuristics/vertex_cover.py` | `tests/test_vertex_cover.py` (14 tests) | now |
| 2 | Body of `greedy_coloring` | `graph_heuristics/coloring.py` | `tests/test_coloring.py` (18 tests) | now |
| 3 | About 5 hand-worked unit tests | `tests/test_author_cases.py` | runs with the suite | now |
| 4 | Report paragraph: why the smallest-last ordering | `report/main.tex`, §2.4 (I'll leave a marked spot) | — | Phase 7 |

**Rules for tasks 1–2:**
- Write only between the two marker lines `# ---- Written by Ahmed Elgazwy: begin ----` and `... end ----`. Replace the `raise NotImplementedError(...)` line with your code.
- Leave the rest of the file as it is. I won't edit these two files until you tell me you're done.
- Keep the marker lines, so the authorship is visible in the code.

**Run the tests** from the repository root, in PowerShell:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_vertex_cover.py -q
.venv\Scripts\python.exe -m pytest tests/test_coloring.py -q
.venv\Scripts\python.exe -m pytest -q                # everything
```

---

## Task 1: `basic_vertex_cover(graph)`

Location: [graph_heuristics/vertex_cover.py](../graph_heuristics/vertex_cover.py)

**The algorithm (lecture):**

```
while E is not empty:
    select an arbitrary edge (u, v) in E
    add both u and v to the cover
    delete all edges in E incident to u and v
```

**How to implement it in O(n + m):**
- Do *not* delete edges from a list: each deletion pass is O(m), so the whole loop is O(m²).
- Instead, scan the edges **once, in input order**. An edge has already been "deleted" exactly when one of its endpoints is already in the cover, so skip it. Otherwise it is the edge the lecture loop selects next.
- To check "is x already in the cover?" in O(1), keep an array of `graph.n` flags, e.g. `bytearray(graph.n)`.

**Input you can use:**

| Expression | Meaning |
|---|---|
| `graph.n` | the number of vertices; vertices are `0 .. n-1` |
| `graph.edges()` | iterates over the edges as `(u, v)` pairs, in input order |

**Output:** a `list[int]` of the cover's vertices in the order you added them. For each selected edge `(u, v)`, append `u` and then `v`. The tests compare your list exactly with the lecture pseudo-code run literally, so the order matters.

**The tests check:**
- the result is a valid cover with no repeated vertices;
- it is identical to the literal lecture algorithm on 150 random graphs;
- the selected pairs form a maximal matching;
- `|C| ≤ 2·OPT` against brute force;
- the worst cases: a perfect matching (exactly 2·OPT), K₅,₅, K₇/K₈ and a star;
- a 100,000-edge graph.

---

## Task 2: `greedy_coloring(graph, order)`

Location: [graph_heuristics/coloring.py](../graph_heuristics/coloring.py)

**The algorithm (lecture):**

```
for i = 1..n (in the given order):
    assign the lowest legal color to v_i
```

Colors are the integers `0, 1, 2, …`. The "lowest legal color" of `v` is the smallest color that none of `v`'s *already-colored* neighbors has. `order` has already been validated for you: the line above your block raises `ValueError` if it is not a permutation of `0..n-1`.

**Input you can use:**

| Expression | Meaning |
|---|---|
| `graph.n` | the number of vertices |
| `graph.neighbors(v)` | the neighbors of `v`; iterate over it like a list |
| `order` | the sequence of vertices to color, in order |

**Output:** a `list[int]` `colors` of length `n`, where `colors[v]` is the color of `v`.

**How to make it O(n + m):**
- Coloring `v` should cost O(deg(v)): look at each neighbor once, then find the smallest free color. That smallest free color is at most `deg(v)`, so the search is short.
- A Python `set` of the neighbors' colors per vertex is already linear overall.
- *A faster option, for the performance marks:* use one list `forbidden` of size `n + 1`, created once and never cleared. When coloring `v`, write `forbidden[c] = v` for each neighbor color `c`; then color `c` is taken iff `forbidden[c] == v`.
- Use something like `-1` to mean "not colored yet".

**The tests check:**
- the result is identical to a literal "lowest legal color" loop on 150 random graphs with random orders;
- the coloring is proper and its colors are 0..k−1 with no gaps;
- at most Δ+1 colors, and at least χ (against brute force);
- known graphs: K₆, even and odd cycles, paths, stars, K₄,₆;
- the crown graph in natural order uses k colors;
- the binomial tree B_k uses k+1 colors in natural order and 2 in smallest-last order;
- a 100,000-edge graph.

---

## Task 3: hand-worked tests in `tests/test_author_cases.py`

Pick about 5 small graphs, work out **on paper** what each algorithm must return, and write one test per graph. Suggestions; choose your own if you prefer:

1. a triangle `(0,1), (1,2), (0,2)`;
2. the path P₄ `0-1-2-3`, with its edges given in a different order, such as `(1,2), (2,3), (0,1)`;
3. the star K₁,₄;
4. K₃,₃;
5. a 5-cycle, or your own "house" graph (a square with a roof).

**For each graph, assert:**
- the exact `basic_vertex_cover(...)` list (it is deterministic);
- that `randomized_vertex_cover(graph, seed)` is valid, and is at most twice the optimum you computed by hand;
- the exact `colors` list for the natural order;
- the color count for the smallest-last coloring.

The file already has the imports and an empty section for your tests.

---

## Task 4: report paragraph (Phase 7)

About 5–8 sentences, in your own words, on why you chose the smallest-last ordering among the options in the csc09 paper and the GCP page. Points you might use: the guarantee of degeneracy + 1 colors, linear time, comparison with LF and DSATUR, the tree example. I'll leave a marked spot in `report/main.tex`.
