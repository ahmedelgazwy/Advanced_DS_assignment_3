# COSC 520 Assignment 3: Plan

**Status:** draft for your review · written Fri 6 Nov 2026, 16:00
**Deadline:** **Fri 6 Nov 2026, 11:59 PM, which is tonight.** About 8 hours remain, so every phase below has a time limit (§10).

---

## 0. Summary

**Assignment.** Implement by hand, in Python, and compare:

| Problem | Algorithm 1 | Algorithm 2 |
|---|---|---|
| Vertex cover | **Basic**: take both endpoints of an arbitrary uncovered edge (2-approximation) | **Randomized**: take one endpoint chosen at random (Pitt 1985; expected 2-approximation) |
| Graph coloring | **Greedy, natural order** (lowest legal color, vertices 1..n) | **Greedy, Smallest-Last order** (Matula & Beck 1983; *recommended choice, decision D1*) |

**Data.** Benchmark the four algorithms on all 36 BHOSLIB/FRB graphs from Network Repository (the link in the PDF). Each graph is used in two forms: as published, and its complement. Each form has one exactly known optimum, so solution quality can be measured against the true optimum (§3). Synthetic sparse graphs up to 10⁶ vertices show the scaling.

**Deliverables.**
- A GitHub repository with the code, unit tests, demo, benchmark scripts, results and figures.
- A PDF report of 5–10 pages in ACM Small format, submitted on Canvas, with links to the GitHub repository and the dataset.

**Workflow.** Same as Assignment 2:
- Work happens in phases. Each phase is reviewed by you and committed as `Phase N: …`.
- `docs/review_log.md` records your decisions.
- Every file carries an AI-assisted header.

**Decisions I need from you (details in §2):**

| # | Decision | My recommendation |
|---|---|---|
| D1 | Which node ordering is the second coloring algorithm | **Smallest-Last (SL)** |
| D2 | Which parts you write yourself (GenAI policy) | **You write the two "basic" algorithm bodies, ~5 tests and one report paragraph** |
| D3 | Dataset forms | **Both the published graph and its complement** |
| D4 | Scope and stretch items | Core as in §2; stretch items only if on schedule at 20:30 |
| D5 | Repo name, visibility, package name | `Advanced_DS_assignment_3` (public), package `graph_heuristics` |

---

## 1. Requirements traceability

Every requirement in the assignment PDF, and where it will be met.

| Requirement (assignment PDF) | Where it is met | Phase |
|---|---|---|
| Basic vertex cover (lecture pseudo-code) | `graph_heuristics/vertex_cover.py` → `basic_vertex_cover` | 3 |
| Randomized vertex cover | `vertex_cover.py` → `randomized_vertex_cover` | 3 |
| Basic greedy coloring | `graph_heuristics/coloring.py` → `greedy_coloring` + `natural_order` | 4 |
| A second option: an ordering from the csc09 paper or the GCP page | `coloring.py` → `smallest_last_order` | 4 |
| "Implement the algorithms yourself", no libraries | No networkx, igraph or similar; a unit test scans the imports | 2–4 |
| Report: explanation of the selected node ordering | Report §2.4 (with a worked example figure) | 7 |
| Report: time **and space** complexity of the ordering | Report §3 and `docs/theory.md` | 1, 7 |
| Report: table summarizing the measured performance | Report Table 3 | 6, 7 |
| Report: runtime plots on a benchmark dataset (BHOSLIB/FRB) | Figures F1 (FRB) and F2 (synthetic scaling) | 6, 7 |
| Python code comparing the two VC algorithms and the two coloring algorithms | `demo.py` and `scripts/run_benchmarks.py` | 5, 6 |
| GitHub link and dataset link in the PDF | Report title footnote and §4 | 7, 8 |
| Code well documented and clean, with unit tests | §5, §6 | all |
| Names meaningful and not too long; comments on every method giving input, output and a short explanation | Docstrings with Args, Returns and a summary; audited in Phase 8 | all, 8 |
| Clear setup and running instructions | `README.md` (Windows and macOS/Linux, quick start, troubleshooting) | 0, 8 |
| ACM Small template with the ACM, journal and copyright information removed; 5–10 pages including plots and references | `report/main.tex` (A2 preamble: `acmart` with `nonacm`) | 7 |
| GenAI disclosure, showing which code is yours | Report section, README, `docs/review_log.md`, code markers (D2) | 3, 4, 7, 8 |
| Submit the PDF on Canvas | **You** | after 8 |
| Cross-check within one week | **You**, by about Fri 13 Nov (§13) | later |

### How each rubric item will be earned

| Rubric item (weight) | How we earn it |
|---|---|
| Explanation of the algorithms (7) | Pseudo-code, approximation proofs, and a worked SL example on a small graph |
| Complexity analysis (10) | Time and space of all four algorithms with proofs; the bucket-queue analysis of SL; memory measured against prediction |
| Plots and comparisons (11) | 4–5 figures, 3 tables, a verdict on each hypothesis H1–H7, and quality measured against **exact** optima |
| References (2) | About 15 primary sources (§9) |
| Naming (5), comments (5) | The conventions in §5, audited in Phase 8 |
| Running instructions (5) | README as in A2 (quick start, Windows and macOS/Linux setup, troubleshooting table) |
| Code design (15) | One `Graph` class; algorithm registries shared by tests, demo and benchmark; linear-time array-based implementations |
| Runs (10), unit tests run (10) | Fresh-clone check in Phase 8; the suite needs no dataset and runs in under 30 s |
| Convincing demo (5) | Worst-case examples where the algorithms differ sharply, plus a real FRB instance against the known optimum |
| Performance (5) | Θ(n+m) implementations using flat `array`s, with no per-edge objects; frb100-40 (7.4M edges) runs in seconds |

---

## 2. Decisions for you

### D1. The node ordering: **Smallest-Last (SL)**, recommended

The csc09 paper linked in the assignment ("Ordering for Coloring and More", Gebremedhin, Tarafdar, Nguyen & Pothen, 2009) defines four orderings through each vertex's *back degree*, its number of neighbors that come earlier in the order:

- **LF** (Largest First): the next vertex has the largest degree.
- **ID** (Incidence Degree): the next vertex has the largest back degree.
- **DLF** (Dynamic Largest First): the next vertex has the largest forward degree.
- **SL** (Smallest Last): the order is built right to left; the next vertex placed (at the end) has the smallest degree in the remaining graph.

**Why SL:**
- **It is the only one of the four with a provable guarantee beyond Δ+1.**
    - Greedy coloring along any order π uses at most B_π + 1 colors, where B_π is the largest back degree in π.
    - SL minimizes B_π over all n! orderings (csc09; Matula & Beck 1983).
    - So greedy coloring with SL uses at most **degeneracy + 1** colors, and degeneracy + 1 is the coloring number col(G).
    - Consequences: any tree gets 2 colors (where the natural order can need log₂ n + 1), and any planar graph gets at most 6.
- **Its complexity analysis is substantial but tractable,** which suits the 10-point rubric item:
    - Θ(n + m) time with a bucket queue (Batagelj & Zaversnik 2003);
    - Θ(n) extra space.
- **It has a free by-product:** the degeneracy. This gives a bound the tests and plots can check.

**Alternatives:**

| Ordering | Pros | Cons |
|---|---|---|
| LF (Welsh & Powell 1967) | Simplest; Θ(n + m) with counting sort | Weakest analysis; no guarantee beyond Δ+1 |
| ID | Θ(n + m) with buckets | Same effort as SL, weaker guarantee |
| DSATUR (Brélaz 1979; GCP page) | Often uses the fewest colors | O((n + m) log n) with a heap; a dynamic rule, not a fixed node order |

*Stretch item:* add LF as a third column in the benchmarks, about 20 minutes (D4).

### D2. Which parts you write: the GenAI policy, recommended split

The PDF says: *"Only prompting GenAI to generate all the algorithms and test cases is not allowed. You should show which part of the code is yours and which part is generated by AI."* The A2 split (you directed, reviewed and wrote the report motivation; the assistant wrote all the code) is the weaker position under this sentence.

**Recommended:**

1. **You write the bodies of `basic_vertex_cover` (about 10 lines) and `greedy_coloring` (about 15 lines).** Before you start, I write the signatures, docstrings and unit tests; you write the body until the tests pass, and I review it. This is test-driven, so it is fast.
2. **You write about 5 hand-worked unit tests** in `tests/test_author_cases.py`, for example the triangle, the path P4, the star K1,4, K3,3 and a 5-cycle, with expected covers and colorings worked out on paper.
3. **You write the report paragraph explaining why SL was chosen** (report §2.4), in your own words.
4. **Your code is marked as yours:**
    - each block you wrote carries `# Written by Ahmed Elgazwy`;
    - the file headers say "AI-assisted … except the functions marked as written by the author";
    - the README and `docs/review_log.md` list the split.

*Cost:* about 45 minutes of your time, mostly in parallel with my work in Phases 3–4.
*Options:* B, the A2 split (faster, more policy risk); C, you also write `randomized_vertex_cover`.

### D3. Dataset forms: **both**, recommended

Network Repository serves the *dense "clique" form* of the FRB graphs (verified, §3). The original BHOSLIB benchmark for **vertex cover** uses the complement (the "MIS" form). Each form has exactly one optimum known in closed form:

| Form | Exact optimum known | Gives |
|---|---|---|
| `clq` (as published, density about 0.82–0.93) | χ = N, the number of groups | The coloring ratio colors / χ |
| `mis` (complement, density about 0.07–0.18) | Minimum vertex cover = \|V\| − N | The vertex-cover ratio \|C\| / OPT |

All four algorithms run on both forms. Together they span **17.8K to 7.4M edges**, more than two orders of magnitude, for the runtime plots.

### D4. Scope

- **Core:**
    - the four algorithms;
    - all 36 FRB graphs, in both forms;
    - synthetic sparse G(n, m) graphs, n = 10³…10⁶;
    - a planted FRB-like generator, so the tests and demo need no download;
    - the worst-case demo;
    - the experiments E1–E5.
- **Stretch, in this order, only if we are on schedule at 20:30:**
    - (a) the LF ordering as a third coloring algorithm;
    - (b) the spread of the basic cover over random edge orders.
- **Out of scope:**
    - the weighted vertex cover algorithms (Pitt's weighted version, Bar-Yehuda & Even 1981): mentioned in the report, not implemented;
    - exact solvers, except brute-force oracles for tiny graphs in the tests.

### D5. Repository

- GitHub repository: `ahmedelgazwy/Advanced_DS_assignment_3`, public, matching A2's name. **You create it** (Phase 2 if we mirror the dataset, otherwise Phase 8).
- Package: `graph_heuristics`.
- Python 3.10, with the same pinned requirements as A2: matplotlib 3.9.4, numpy 2.1.3 (only for plotting and curve fitting), pytest 8.4.2.

---

## 3. Dataset: verified facts

- **Source:** https://networkrepository.com/bhoslib.php, the link in the PDF.
    - Files: `https://nrvis.com/download/data/bhoslib/<name>.zip`.
    - Each zip holds `<name>.mtx` (Matrix Market, `coordinate pattern symmetric`, vertices numbered from 1) and a `readme.html`.
- **Instances (36):** 7 families × 5 instances, plus frb100-40.
    - Families: frb30-15, frb35-17, frb40-19, frb45-21, frb50-23, frb53-24 and frb59-26.
    - frb56-25 from the original BHOSLIB is not on Network Repository.
    - Zip sizes: 181 KB to 17 MB, about 50 MB in total.
- **Origin:** `frbN-K` was generated by Model RB (Xu & Li 2000; Xu et al. 2007). It has N groups of K vertices, N·K vertices in total, and is "forced satisfiable": a hidden solution is planted.
- **Checked today on frb30-15-1** (downloaded to a scratch folder; nothing committed):
    - 450 vertices and 83,198 edges, with no self-loops and no duplicate edges;
    - **every block of 15 consecutive vertices (1–15, 16–30, …) is an independent set** (0 edges inside blocks);
    - the complement has **17,827** edges, which matches the BHOSLIB MIS file.
    - Phase 2 repeats these checks on all 36 graphs.
- **Exact optima:**
    - **`clq` form:** the N blocks are independent sets, so they form a proper N-coloring, and χ ≤ N. The planted solution is an N-clique (Xu's BHOSLIB page), so χ ≥ N. Therefore **χ = N.**
        - As a measure of how hard these graphs are: Network Repository's heuristic found a clique of only 24, not 30, on frb30-15-1.
    - **`mis` form:** the blocks are cliques, so an independent set takes at most one vertex per block, and α ≤ N. The planted solution is an independent set of size N. Therefore α = N, and **OPT_VC = N·K − N.**

| Family | N | K | \|V\| | \|E\| clq | \|E\| mis | χ (clq) | OPT_VC (mis) |
|---|---|---|---|---|---|---|---|
| frb30-15 | 30 | 15 | 450 | ≈83K | ≈17.8K | 30 | 420 |
| frb35-17 | 35 | 17 | 595 | ≈149K | ≈27.8K | 35 | 560 |
| frb40-19 | 40 | 19 | 760 | ≈247K | ≈41K | 40 | 720 |
| frb45-21 | 45 | 21 | 945 | ≈387K | ≈59K | 45 | 900 |
| frb50-23 | 50 | 23 | 1,150 | ≈581K | ≈80K | 50 | 1,100 |
| frb53-24 | 53 | 24 | 1,272 | ≈714K | ≈94K | 53 | 1,219 |
| frb59-26 | 59 | 26 | 1,534 | ≈1.05M | ≈126K | 59 | 1,475 |
| frb100-40 | 100 | 40 | 4,000 | ≈7.43M | ≈573K | 100 | 3,900 |

The exact edge counts per instance go into `data/manifest.json` in Phase 2. |E| mis = C(|V|, 2) − |E| clq.

**Handling the files:**
- `scripts/download_dataset.py` downloads the 36 zips into `data/` and checks their SHA-256 checksums against `data/manifest.json`. The zips are **not committed**.
- *Fallback:* a GitHub release `dataset-v1` mirroring the zips. You publish it, as in A2.
- The `mis` form is computed in memory when a graph is loaded: an O(n²) pass, at most 8M pairs for frb100-40.
- **Synthetic graphs:** `random_graph(n, m, seed)` generates uniform G(n, m) graphs with m = 5n (average degree 10), in memory and seeded. No files are written.
- **No download for the tests and demo:** `planted_graph(groups, size, density, seed)` builds a small FRB-like graph with the same exact optima.
    - Its blocks are independent sets, and one hidden vertex per block forms a clique, so χ = groups.
    - In its complement, OPT_VC = n − groups.

---

## 4. Algorithms and complexity

This is a summary; the full derivations go into `docs/theory.md` in Phase 1.

Notation: n = |V|, m = |E|, Δ is the largest degree, d the degeneracy, and OPT the size of a minimum vertex cover.

| Algorithm | Time | Extra space | Quality guarantee |
|---|---|---|---|
| Basic VC | Θ(n + m) | Θ(n) (a `bytearray` of flags) | \|C\| = 2\|M\| ≤ 2·OPT, tight |
| Randomized VC | Θ(n + m), one random bit per uncovered edge | Θ(n) | E\|C\| ≤ 2·OPT |
| Greedy coloring, natural order | Θ(n + m) | Θ(n) (colors and a `forbidden` stamp array) | ≤ Δ + 1 colors |
| SL ordering | Θ(n + m) | Θ(n) (`deg`, `vert`, `pos` of n entries each; `bin` of Δ + 1 ≤ n entries) | gives the degeneracy d |
| Greedy coloring, SL order | Θ(n + m) in total | Θ(n) | ≤ d + 1 = col(G) ≤ Δ + 1 colors |
| *The graph itself (CSR)* | Θ(n + m) to build | Θ(n + m): offsets n + 1, adjacency 2m, edge list 2m (4-byte `array('i')`) | — |

**Basic VC.**
- **Implementation:** one pass over the edge list in input order: if neither endpoint is covered, add both.
- **Equivalence with the lecture's while-loop:** an edge is "deleted" exactly when one of its endpoints enters the cover, so "an arbitrary remaining edge" is "the next uncovered edge in input order".
- **Proof of the bound:** the chosen edges form a maximal matching M, and any cover needs a distinct vertex for each edge of M, so OPT ≥ |M|.
- **Tight examples:** a perfect matching, and K_{n,n}.

**Randomized VC (Pitt 1985, Yale TR-404, the first link in the PDF).**
- **Implementation:** the same pass, but each uncovered edge adds *one* endpoint chosen uniformly at random.
- **Proof of the bound:** each pick lands in a fixed optimal cover with probability ≥ ½.
- **Controlled comparison:** the edge order is the same as in the basic version, so the endpoint choice is the only difference.
- **Reproducibility:** seeded `random.Random`, using `getrandbits(1)`.

**Greedy coloring.**
- For each vertex in order:
    1. stamp its neighbors' colors in `forbidden[c] = v`, which needs no clearing between vertices;
    2. take the smallest unstamped color.
- That is at most deg(v) + 1 steps per vertex, so Θ(n + m) in total.

**The SL ordering (Matula & Beck 1983; Batagelj & Zaversnik 2003).**
1. Bin-sort the vertices by degree into `vert`, recording each vertex's position in `pos` and where each degree's bin starts in `bin`.
2. Process the vertices in order of increasing current degree. When v is removed, each unprocessed neighbor u with deg[u] > deg[v] is swapped to the front of its bin and its degree is decremented, which is O(1) per edge.
3. The coloring order is the *reverse* of the removal order.
4. d = the largest degree at the moment of removal.

**Hypotheses** (stated in Phase 1, tested in Phase 6):

- **H1:** all four algorithms run in Θ(n + m): the log-log slope of time against n + m is about 1, on synthetic and on FRB graphs.
- **H2:** randomized VC and basic VC differ only by a constant factor (the cost of the random number generator).
- **H3:** SL coloring costs about 2–3× natural coloring, because of the extra ordering pass.
- **H4:** basic VC ≤ 2·OPT always. On FRB `mis`, *any* cover is at most |V|/OPT ≈ 1.03–1.07 times OPT, because OPT is 93–97.5% of the vertices. So FRB cannot separate the two VC algorithms by much, and the worst-case examples will.
- **H5:** randomized VC finds smaller covers on average than basic VC, with variance.
- **H6:** SL uses no more colors than the natural order, and always at most d + 1.
- **H7:** neither coloring reaches χ = N on FRB `clq`, because these are hard instances. The gap will be measured.

---

## 5. Code design

```
.
├── graph_heuristics/
│   ├── __init__.py          # exports + registries
│   ├── graph.py             # Graph: CSR adjacency + edge list (array('i')), complement()
│   ├── graph_io.py          # read_mtx (.mtx/.zip/.gz), read_dimacs (p edge / e u v), load_graph
│   ├── generators.py        # random_graph, planted_graph, path, cycle, star, complete,
│   │                        #   complete_bipartite, crown, perfect_matching, binomial_tree
│   ├── vertex_cover.py      # basic_vertex_cover, randomized_vertex_cover, is_vertex_cover
│   ├── coloring.py          # natural_order, smallest_last_order, greedy_coloring,
│   │                        #   is_proper_coloring, color_count, max_back_degree
│   ├── datasets.py          # FRB catalogue (names, N, K, exact optima), paths, checksums
│   └── experiment.py        # timing (gc paused, median), tracemalloc peak, slope fit, tables
├── demo.py
├── scripts/
│   ├── download_dataset.py  # fetch + SHA-256 verify the 36 zips
│   ├── run_benchmarks.py    # E1–E5 -> results/*.csv  (--quick, --max-edges)
│   └── plot_results.py      # figures + slopes + results/summary.md
├── tests/                   # pytest (see §6)
├── results/                 # CSVs, figures/, summary.md, environment.json (committed)
├── data/                    # README.md, manifest.json (zips git-ignored)
├── report/                  # main.tex, references.bib, figures/, report.pdf, README.md
├── docs/                    # plan.md (this file), theory.md, review_log.md
├── requirements.txt, pyproject.toml, README.md
```

**Main signatures:**

```python
class Graph:                                   # vertices 0..n-1, immutable
    n: int; m: int
    @classmethod
    def from_edges(cls, n, edges) -> "Graph"   # merges (u,v)/(v,u) duplicates; rejects self-loops
    def degree(self, v) -> int
    def neighbors(self, v) -> memoryview       # slice of the CSR adjacency
    def edges(self) -> Iterator[tuple[int, int]]   # input order = "arbitrary edge" order
    def max_degree(self) -> int
    def complement(self) -> "Graph"

def basic_vertex_cover(graph) -> list[int]                         # vertices in order added
def randomized_vertex_cover(graph, seed=None) -> list[int]
def is_vertex_cover(graph, cover) -> bool

def natural_order(graph) -> list[int]
def smallest_last_order(graph) -> tuple[list[int], int]            # (order, degeneracy)
def greedy_coloring(graph, order) -> list[int]                     # colors[v] in 0..k-1
def color_count(colors) -> int
def is_proper_coloring(graph, colors) -> bool

VERTEX_COVER_ALGORITHMS = {"basic": ..., "randomized": ...}
COLORING_ORDERS = {"natural": ..., "smallest_last": ...}           # (+ "largest_first" if stretch)
```

**Design rules:**
- **Plain functions plus one `Graph` class.** The tests, demo and benchmark all iterate over the registries above, so adding an algorithm touches one line.
- **Flat `array('i')` storage, and no recursion.** There are no per-vertex or per-edge objects, so frb100-40 needs about 120 MB in total.
- **No graph libraries** (networkx, igraph, graph-tool, rustworkx), and **no numpy** in the algorithm modules. A test parses the imports to enforce this.
- **Every public function has a docstring** with a one-line summary, **Args** (input), **Returns** (output), **Raises** and, for the algorithms, a **Complexity** line.
- **File headers:** each file starts with its purpose and `AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy`, plus the marker on author-written functions (D2).
- **Other rules:** lines of at most 100 characters; type hints; all randomness through a seeded `random.Random`; every command runs from the repository root as `python -m …`.

---

## 6. Test plan

The target is about 200 tests that run in under 30 s and need no downloaded dataset. The FRB integration tests are skipped when `data/` is empty.

The oracles live in `tests/reference.py`:

| Oracle | Purpose |
|---|---|
| `literal_vertex_cover(edges)` | The lecture pseudo-code word for word: an explicit edge set and explicit deletions, O(m·Δ). It must return the same cover as `basic_vertex_cover`. |
| `brute_force_min_cover(graph)` | The exact optimum for n ≤ 14 |
| `brute_force_chromatic(graph)` | The exact χ for n ≤ 8 |
| `brute_force_degeneracy(graph)` | O(n²) repeated removal of a minimum-degree vertex |
| `min_back_degree_over_all_orders(graph)` | The minimum over all permutations, for n ≤ 7. It checks the csc09 claim that SL is optimal. |

| Test file | What it checks |
|---|---|
| `test_graph.py` | CSR is correct; duplicates (u,v)/(v,u) are merged; self-loops and out-of-range vertices are rejected; degrees and `max_degree`; edge order is kept; complement edge count = C(n,2) − m; the complement of the complement is the original; empty graph; n = 0 |
| `test_graph_io.py` | Tiny `.mtx` and DIMACS files written to `tmp_path`, plain, `.gz` and `.zip`; 1-indexed → 0-indexed; a header/count mismatch raises an error |
| `test_generators.py` | Sizes and edge counts; determinism by seed; the planted graph has independent blocks and a hidden clique; the binomial tree's adversarial order |
| `test_vertex_cover.py` | **Validity:** both algorithms are valid on 200 random graphs.<br>**Small graphs:** empty graph → ∅; a single edge.<br>**Worst cases:** perfect matching (basic = 2·OPT exactly, randomized = OPT); star; K_n; K_{n,n}.<br>**The 2-approximation:** against brute force on 300 random small graphs.<br>**Basic equals the textbook algorithm:** the basic cover is the endpoints of a maximal matching (disjoint and maximal), and it agrees with `literal_vertex_cover`.<br>**Randomized:** the same seed gives the same cover; on a single edge, each endpoint is chosen with frequency ½ ± a binomial bound over 2,000 seeds; the mean over seeds is ≤ 2·OPT. |
| `test_coloring.py` | **Validity:** both orders give a proper coloring on 200 random graphs, with colors 0..k−1 and no gaps.<br>**Bounds:** natural ≤ Δ + 1; SL ≤ d + 1.<br>**SL ordering:** the SL order is a permutation; its largest back degree equals the brute-force degeneracy and the minimum over all orderings (n ≤ 7).<br>**Known graphs:** K_n needs n colors, even cycles 2, odd cycles 3, an empty graph 1; any tree gets 2 colors with SL; the binomial tree B_k with its adversarial order needs k + 1 colors in natural order and 2 with SL; the crown graph in interleaved order needs n/2 colors in natural order; a planted graph needs at least `groups` colors.<br>**Errors:** a non-permutation order raises an error. |
| `test_author_cases.py` | **Your** hand-worked cases (D2) |
| `test_datasets.py` | Name parsing (`frb30-15-1` → N = 30, K = 15); the exact-optimum formulas; checksum checking. *If the data is present:* frb30-15-1 has 450 vertices and 83,198 edges, its blocks are independent, and its complement has 17,827 edges. |
| `test_experiment.py`, `test_scripts.py`, `test_demo.py` | Timing helper; slope fit on an exact power law; table formatting; a tiny end-to-end `--quick` benchmark plus plots; the demo runs end to end |
| `test_no_libraries.py` | No graph library is imported anywhere, and no numpy in the algorithm modules |

---

## 7. Demo (`demo.py`, about 10 s)

1. **A hand-made example** (about 10 vertices):
    - the edges;
    - both covers and both colorings, each with a validity ✓;
    - the SL order, with each vertex's back degree, and the degeneracy.
2. **Where the algorithms differ:**
    - **perfect matching:** basic = 2·OPT, randomized = OPT;
    - **binomial tree B_k with an adversarial order:** the natural order uses k + 1 = log₂ n + 1 colors and SL uses 2 (Gyárfás & Lehel 1988);
    - **crown graph:** the natural order uses n/2 colors.
3. **A real instance:** frb30-15-1 if it has been downloaded, otherwise a planted graph with the same parameters.
    - **Vertex cover on `mis`:** basic against randomized (30 seeds: minimum, mean and maximum) against OPT = 420.
    - **Coloring on `clq`:** natural against SL against χ = 30, with the timings.

Options: `--instance`, `--seeds`, `--quick`.

---

## 8. Benchmark plan

The full run takes about 15–20 minutes, mostly frb100-40, and runs in the background while the report starts. `--quick` takes about 1 minute.

**Timing method (as in A2):**
- `time.perf_counter`, with the garbage collector paused.
- The median of 5 runs (3 for frb100-40 `clq`).
- Graph loading is excluded.
- SL is timed in two parts: the ordering and the coloring.

| Experiment | Graphs | Measured |
|---|---|---|
| **E1 Runtime on FRB** | 36 instances × {`clq`, `mis`} × 4 algorithms | Time; time per (n + m); the SL split |
| **E2 Quality on FRB** | Same | VC on `mis`: \|C\|/OPT (basic; randomized over 30 seeds: mean, standard deviation, minimum, maximum). Colors on `clq`: colors/χ (natural, SL), with the bounds Δ + 1 and d + 1. On the other form, values with their bounds (lower bound K colors on `mis`; OPT ≥ \|M\| on `clq`). |
| **E3 Scaling** | G(n, 5n), n = 1K … 1M in 1-2-5 steps, 3 seeds | Time against n + m; log-log slope |
| **E4 Memory** | 3–4 sizes, measured in separate runs from the timings | `tracemalloc` peak per algorithm; bytes per vertex against the Θ(n) prediction |
| **E5 Worst cases** | Perfect matching, K_{n,n}, binomial tree, crown graph | Ratios (a table shared with the demo) |

**Outputs:**
- `results/` holds `frb_runtime.csv`, `frb_quality.csv`, `scaling.csv`, `memory.csv`, `slopes.csv`, `environment.json`, `benchmark_log.txt` and `summary.md`.
- `results/figures/` holds every figure as PNG and PDF.

**Figures:** F1–F4 go into the report; F5 is used if space allows.

| # | Figure |
|---|---|
| F1 | Time against n + m on FRB, log-log, 4 algorithms, both forms (marker shape), with fitted slopes in the legend |
| F2 | Time against n + m on the synthetic graphs, with a second panel of ns per (n + m), which is flat when growth is linear |
| F3 | VC quality on FRB `mis` per family: \|C\|/OPT for basic and randomized (minimum–maximum bars), with the \|V\|/OPT ceiling |
| F4 | Colors on FRB `clq` per family: natural, SL, χ = N and d + 1 |
| F5 | SL cost split: ordering against coloring against natural coloring |

**Report Table 3:** one row per family (the mean over its 5 instances), giving n, m, the time of each of the four algorithms, the VC size and ratio, and the color count and ratio.

---

## 9. Report plan (ACM Small, about 8 pages, maximum 10)

The A2 preamble is reused: `acmart` with `acmsmall,nonacm`, no copyright, the same author block. It is compiled on Overleaf.

| Section | Pages | Rubric item |
|---|---|---|
| Abstract and 1. Introduction: the problems; NP-hardness (Karp 1972); inapproximability (Dinur & Safra 2005; Khot & Regev 2008; Zuckerman 2007); contributions; GitHub and dataset links | 0.75 | — |
| 2. Algorithms: 2.1 basic VC and the 2-approximation proof; 2.2 randomized VC (Pitt) and the expected bound; 2.3 greedy coloring and the Δ + 1 bound; **2.4 the SL ordering**: back-degree definition (csc09 Table 1), worked example figure, **why we chose it (your paragraph)**, the d + 1 guarantee | 1.5 | Explanation (7) |
| 3. Complexity analysis: proofs for all four algorithms; the bucket-queue analysis of SL in detail; Table 1; the CPython memory model, predicted against measured | 1.5 | Complexity (10) |
| 4. Experimental setup: the dataset (Table 2 and the argument for the exact optima); synthetic graphs; machine; timing method | 0.75 | — |
| 5. Results: Table 3; F1–F4; the hypothesis verdict table (H1–H7) | 2.5 | Plots and comparisons (11) |
| 6. Discussion and 7. Conclusion: surprises, limitations (Python constant factors; FRB optima close to \|V\|) | 0.5 | — |
| GenAI use and authorship | 0.25 | Policy |
| References | 0.5 | References (2) |

**Planned references:**
- **Vertex cover:**
    - Pitt 1985 (Yale TR-404);
    - Salavatipour, Approx13 lecture 1 (UAlberta);
    - Bar-Yehuda & Even 1981;
    - Skiena, *The Algorithm Design Manual*, 3rd ed., ch. 12;
    - CLRS §35.1.
- **Coloring:**
    - Gebremedhin, Tarafdar, Nguyen & Pothen 2009, "Ordering for Coloring and More" (csc09);
    - Matula & Beck 1983 (JACM);
    - Batagelj & Zaversnik 2003;
    - Welsh & Powell 1967;
    - Brélaz 1979;
    - Gyárfás & Lehel 1988;
    - Chiarandini's GCP page.
- **Dataset:**
    - Xu & Li 2000;
    - Xu, Boussemart, Hemery & Lecoutre 2007 (Model RB / BHOSLIB);
    - Rossi & Ahmed 2015 (Network Repository).
- **Hardness:**
    - Karp 1972;
    - Dinur & Safra 2005;
    - Khot & Regev 2008;
    - Zuckerman 2007.

---

## 10. Phases and timeline

**Each phase follows the same loop:**
1. I implement the phase and run the tests.
2. I summarize the results for you.
3. You review, and run anything you want to check.
4. I commit as `Phase N: <title>`, with a body and the co-author trailer.
5. I add a row to `docs/review_log.md`.

| Phase | Deliverables | Done when | Your part | Time | Target |
|---|---|---|---|---|---|
| **Plan** | This file | You approve it, with D1–D5 settled | Review and decide | 15 min | 16:20 |
| **0. Setup** | `.venv` (py -3.10), `requirements.txt`, `pyproject.toml`, README stub, `docs/review_log.md`, package skeleton | `python -m pytest` runs (0 tests) | Skim | 10 min | 16:30 |
| **1. Theory** | `docs/theory.md`: the full §4 with proofs, the memory model and H1–H7 | Every bound has a proof or a citation | Read it | 25 min | 16:55 |
| **2. Graph and data** | `graph.py`, `graph_io.py`, `generators.py`, `datasets.py`, `scripts/download_dataset.py`, `data/README.md`, `manifest.json` (exact counts and checksums); all 36 graphs downloaded and checked | Tests pass; block structure confirmed on all 36; complement counts recorded | Optional: create the GitHub repository and the dataset release | 45 min | 17:40 |
| **3. Vertex cover** | `vertex_cover.py`, the oracles, `test_vertex_cover.py` | All the VC tests pass, including yours | **Write `basic_vertex_cover`** and your test cases | 40 min | 18:20 |
| **4. Coloring** | `coloring.py` (natural, SL, checks), `test_coloring.py` | All the coloring tests pass; the SL optimality check passes | **Write `greedy_coloring`** | 50 min | 19:10 |
| **5. Demo** | `demo.py`, `test_demo.py` | Runs in about 10 s without the dataset | Run it | 20 min | 19:30 |
| **6. Benchmarks** | `run_benchmarks.py`, `plot_results.py`, the full run, `results/`, figures, `summary.md`, H1–H7 verdicts | The figures are approved | Review the figures and results | 60 min | 20:30 |
| **7. Report** | `report/` (LaTeX, bib, figures), compiled on Overleaf | 5–10 pages, links present, ACM information removed | **Write the §2.4 paragraph**; compile on Overleaf | 75 min | 21:45 |
| **8. Final QA** | Full README; docstring, line-length and header audit; tests from a fresh clone in a short path; push to GitHub; `report/report.pdf` | The §12 checklist is all ✓ | Create or push the GitHub repository; final read | 30 min | 22:15 |
| **Submit** | The PDF on Canvas | — | **You** | — | **≤ 23:00** |

That leaves a buffer of about 1 hour 45 minutes. **If we fall behind, cut in this order:**
1. the stretch items;
2. E4 reduced to a table of 3 sizes;
3. E3 capped at n = 2×10⁵;
4. frb100-40 run once instead of 3 times;
5. F5 dropped;
6. a report of 6–7 pages.

The algorithms, tests, demo, FRB runtime plots and quality results are never cut.

---

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| The deadline is tonight | Time limits per phase; the core work comes first; a fixed cut list (§10). Raise an extension with the instructor *now* if one is needed. |
| frb100-40 (7.4M edges) is slow or large in pure Python | Parse the file straight into `array('i')`; detect duplicates with an O(n + m) stamp array instead of a set; `--max-edges`; fewer repeats. Estimated: about 15 s to load and about 10 s per run of all four algorithms. |
| nrvis.com is down | Download everything in Phase 2 (early); mirror it as a GitHub release; the DIMACS reader also handles the original BHOSLIB files. The tests and demo never need the download (planted graphs). |
| Noisy timings | Median of several runs, garbage collector paused, environment recorded; conclusions rest on slopes and ratios, not absolute times. |
| GenAI policy | The D2 split, with markers in the code and the review log. |
| Overleaf compile problems | Reuse the A2 preamble, which already compiled; compile early in Phase 7. |
| Randomized results vary | 30 seeds; report the mean, standard deviation, minimum and maximum. |

## 12. Final QA checklist (Phase 8)

**Code and tests:**
- [ ] `python -m pytest` passes from a fresh clone in a short path (e.g. `C:\src`), with no dataset.
- [ ] `python demo.py` and `python -m scripts.run_benchmarks --quick` both work with no dataset.
- [ ] Every public function has a summary, Args and Returns; every file has its header; author-written blocks are marked.
- [ ] No line is longer than 100 characters; no graph-library imports; nothing unused left behind (`.DS_Store`, egg-info and similar).

**README:**
- [ ] It has a quick start, Windows and macOS/Linux setup, a table of the tests, the demo, the benchmarks, a results table with a figure, the dataset, the report, AI usage and troubleshooting.

**Report:**
- [ ] 5–10 pages, with the GitHub link and the dataset link.
- [ ] The ACM, journal and copyright information is removed.
- [ ] It has a GenAI section and about 15 references.
- [ ] `report/report.pdf` is committed.

**Submission:**
- [ ] The PDF is on Canvas.

## 13. After submission

The cross-check is due within one week, by about **Fri 13 Nov 2026**, emailed to fatemeh.fard@ubc.ca. Reuse the format of the A2 review in `../cross_check/`: a score table, each rubric part with its reasons, and suggestions.
