# Theory notes: vertex cover and greedy graph coloring

Phase 1. This is the analysis behind report sections 2 and 3, and the
hypotheses tested by the benchmark. References are in brackets, with the full
list at the end.

AI-assisted: generated with Claude Code; reviewed by Ahmed Elgazwy.

## 0. Notation and cost model

- G = (V, E) is undirected and simple, with n = |V| vertices numbered 0..n−1 and m = |E| edges.
- deg(v) is the degree of v; Δ is the largest degree; d is the degeneracy (§4.2).
- OPT is the size of a minimum vertex cover; α is the size of a maximum independent set; ω is the size of a maximum clique; χ is the chromatic number.
- **Cost model:** the word RAM. Each array access, comparison and random bit costs O(1).
- **The graph representation counts as input, not as extra space.** It is stored twice, as flat arrays:
    - the **edge list** `edge_u`, `edge_v` (2m entries) in input order;
    - the **CSR adjacency**: `offsets` (n + 1 entries) and `adjacency` (2m entries).
    - Total: Θ(n + m) words. The extra space of each algorithm is measured on top of this.

## 1. Background: both problems are hard

- **Minimum vertex cover** is NP-hard [Karp 1972].
    - It cannot be approximated within 1.36 unless P = NP [Dinur & Safra 2005], nor within 2 − ε under the Unique Games Conjecture [Khot & Regev 2008].
    - So the simple factor 2 below is essentially the best known for polynomial algorithms.
- **Chromatic number** is NP-hard [Karp 1972], and cannot be approximated within n^(1−ε) unless P = NP [Zuckerman 2007].
    - Greedy coloring therefore gives no worst-case ratio guarantee. Its guarantees are *upper bounds* in terms of Δ and d.

## 2. Basic vertex cover (the lecture algorithm)

```
VertexCover(G):
    C = ∅
    while E ≠ ∅:
        select an arbitrary edge (u, v) ∈ E
        C = C ∪ {u, v}
        delete from E every edge incident to u or v
    return C
```

### 2.1 Implementation: one scan of the edge list

- The algorithm keeps a flag array `in_cover` and scans the edges in input order. When an edge has neither endpoint in C, it adds both endpoints.
- **Equivalence with the pseudo-code.** At any moment the edges the pseudo-code has not deleted are exactly the edges with no endpoint in C: an edge is deleted precisely when one of its endpoints enters C.
    - So "select an arbitrary remaining edge" can be "the next edge in the scan that has no endpoint in C".
    - Edges skipped by the scan are deleted edges, and an edge never comes back once deleted.
    - The scan therefore returns the same C as the pseudo-code that always selects the first remaining edge in input order. A unit test checks this against a literal implementation with explicit deletions.

### 2.2 Approximation ratio: |C| ≤ 2·OPT

1. **The selected edges form a matching M:** each selected edge has both endpoints outside C, and both are then added to C, so no two selected edges share a vertex.
2. **M is maximal:** every edge has an endpoint in C, which is the set of matched vertices.
3. **|C| = 2|M|.**
4. **OPT ≥ |M|:** any cover must contain at least one endpoint of each edge of M, and these endpoints are distinct because M is a matching.
5. Hence |C| = 2|M| ≤ 2·OPT.

**The bound is tight:**
- **Perfect matching:** on k disjoint edges, |C| = 2k and OPT = k.
- **K_{k,k}:** every maximal matching of K_{k,k} is perfect, so |C| = 2k, while OPT = k (one side).

### 2.3 Complexity

- **Time Θ(n + m):** allocating the flag array is Θ(n). Each edge is examined once with O(1) work: two flag reads, plus at most two writes and two appends.
- **Extra space Θ(n):** the flag array has n bytes, and the output has at most n entries.

## 3. Randomized vertex cover [Pitt 1985]

The edge scan is the same, but for an uncovered edge (u, v) **one** endpoint is added, each with probability 1/2. Edges are scanned in the same order as in §2, so the coin flip is the only difference. This is the unweighted case of Pitt's algorithm; the weighted version picks u with probability w(v)/(w(u) + w(v)).

### 3.1 Expected ratio: E|C| ≤ 2·OPT

Fix an optimal cover C\*. For edge t of the scan (t = 1..m), define two indicators:

- G_t = 1 if edge t is selected and the picked endpoint is in C\*;
- B_t = 1 if edge t is selected and the picked endpoint is not in C\*.

Then |C| = Σ_t (G_t + B_t).

1. **Σ_t G_t ≤ |C\*|.** The picked vertices are distinct: a vertex, once picked, covers all its edges, so it is never picked again.
2. **For each t, E[B_t] ≤ E[G_t].**
    - Whether edge t is selected is decided by the coin flips of earlier edges.
    - Given that it is selected, at least one endpoint of edge (u, v) lies in C\*, because C\* is a cover. So the fair coin picks a vertex of C\* with probability ≥ 1/2.
    - Hence E[B_t | history] ≤ E[G_t | history], and taking expectations gives E[B_t] ≤ E[G_t].
3. **Combining:** by linearity of expectation, E|C| = Σ_t E[G_t] + Σ_t E[B_t] ≤ 2·Σ_t E[G_t] ≤ 2|C\*| = 2·OPT.

**Notes:**
- The guarantee holds only *in expectation*; a single run can exceed 2·OPT.
- On a perfect matching the randomized algorithm is always optimal (k vertices), while the basic one takes 2k.
- On a star with the center listed first in every edge, the randomized algorithm picks leaves until it first picks the center, so its expected size is about 2. The basic algorithm always takes 2.

### 3.2 Complexity

- **Time Θ(n + m):** one random bit (`getrandbits(1)`) per selected edge, and at most n selected edges.
- **Extra space Θ(n),** as in §2.

## 4. Greedy coloring

```
GreedyColoring(G, order v_1..v_n):
    for i = 1..n: color v_i with the smallest color not used by its colored neighbors
```

### 4.1 Bounds: back degree

- In an order π, the **back degree** of v is the number of neighbors of v placed before v [Gebremedhin et al. 2009]. Let B_π be the largest back degree in π.
- When v is colored, at most back(v) colors are blocked, so v gets a color ≤ back(v). Greedy coloring therefore uses **at most B_π + 1 ≤ Δ + 1 colors.**
- **Natural order** (v_i = i − 1): any graph gives ≤ Δ + 1. Some graphs are adversarial in this order:
    - **Crown graph:** K_{k,k} minus a perfect matching, numbered a_0, b_0, a_1, b_1, … It is bipartite (χ = 2), but greedy coloring gives a_i and b_i color i, so it uses k = n/2 colors.
    - **Binomial tree B_k:** numbered in post-order, each root numbered last. Greedy coloring gives the root of B_j color j, so it uses k + 1 = log₂ n + 1 colors on a tree (χ = 2) [Gyárfás & Lehel 1988].

### 4.2 Smallest-last order [Matula & Beck 1983]

**Definition [Gebremedhin et al. 2009, Table 1]:** build the order from the end. v_n is a vertex of minimum degree in G; remove it. v_{n−1} is a vertex of minimum degree in what remains; and so on. The back degree of v_i in the order equals its degree in G[v_1..v_i] at the moment it is removed.

**Theorem:** smallest-last minimizes B_π over all n! orders, and min_π B_π = d, the **degeneracy** (the largest k such that G has a subgraph of minimum degree k, i.e. a non-empty k-core). Proof:

- **Every order has B_π ≥ d.** Take a subgraph H with minimum degree d. In any order π, the last vertex of H has ≥ d neighbors in H before it.
- **SL achieves B_π ≤ d.** When v_i is removed, its degree is the minimum degree of the remaining subgraph G[v_1..v_i], and that minimum is ≤ d by the definition of d.

**Corollary:** greedy coloring along the smallest-last order uses at most d + 1 colors. The number d + 1 is called the *coloring number* col(G). Examples:
- every forest has d ≤ 1, so 2 colors;
- every planar graph has d ≤ 5, so at most 6 colors;
- in general d ≤ Δ, and d can be much smaller (e.g. a star: Δ = n − 1, d = 1).

### 4.3 Computing the order in Θ(n + m): bucket queue [Batagelj & Zaversnik 2003]

**Data structure.**
- `deg[v]` is the current degree of v.
- `vert` is an array of the not-yet-removed vertices, kept **sorted by current degree**.
- `pos[v]` is the position of v in `vert`.
- `start[k]` is the first position of the degree-k bucket.

**Setup.** One counting sort by degree fills `vert`, `pos` and `start` in Θ(n + Δ).

**Main loop:** for i = 0..n−1:
1. Remove v = `vert[i]`, which is a vertex of minimum current degree because `vert[i..]` is sorted.
2. For each neighbor u that is not yet removed (`pos[u] > i`), let k = `deg[u]`.
3. Swap u with the first vertex of bucket k (position `start[k]`, clamped to i + 1 if it has fallen behind the removed prefix).
4. Advance `start[k]`. u is now the last element of bucket k − 1, so `vert[i+1..]` stays sorted.
5. Decrement `deg[u]`.

The vertex removed at step i is placed at position n − 1 − i of the coloring order (the order is reversed at the end). The degeneracy is the largest `deg[v]` seen at removal.

**Time Θ(n + m):**
- the counting sort is Θ(n + Δ) = Θ(n), since Δ < n;
- each vertex is removed once;
- each adjacency entry is examined once, when its vertex is removed: 2m examinations, each O(1) (a comparison, at most one swap of four array writes, two increments);
- reversing the order is Θ(n).

**Extra space Θ(n):** `deg`, `pos` and `vert` have n entries each, and `start` has Δ + 2 ≤ n + 1. That is about 4n words in total.

**Correctness of the clamp.** Positions ≤ i hold removed vertices and are never swapped again.
- For degrees k ≤ the current minimum, the true bucket start is i + 1, and a stored value can only be smaller, because stored values only move forward.
- For larger k the stored value is exact.
- A unit test checks the defining property (each removal has minimum remaining degree) on 100 random graphs, and checks optimality against all n! orders on small graphs.

### 4.4 Greedy coloring itself in Θ(n + m)

- A `forbidden` array of n + 1 entries is reused across vertices with a *stamp*: `forbidden[c] = v` means a neighbor of v has color c, so it never needs clearing.
- Coloring v reads its deg(v) neighbors, then scans colors 0, 1, … until it finds a free one, which takes at most deg(v) + 1 steps.
- **Time:** Σ_v (deg(v) + 1) = 2m + n = Θ(n + m).
- **Extra space Θ(n):** the colors and the stamps.

### 4.5 Summary (Table 1 of the report)

| Algorithm | Time | Extra space | Guarantee |
|---|---|---|---|
| Basic VC | Θ(n + m) | Θ(n) | \|C\| = 2\|M\| ≤ 2·OPT (tight) |
| Randomized VC | Θ(n + m) | Θ(n) | E\|C\| ≤ 2·OPT |
| Greedy, natural order | Θ(n + m) | Θ(n) | ≤ Δ + 1 colors |
| Smallest-last order | Θ(n + m) | Θ(n) (≈ 4n words) | B_π = d, the minimum possible |
| Greedy, SL order (total) | Θ(n + m) | Θ(n) | ≤ d + 1 = col(G) ≤ Δ + 1 colors |

**Context: other orderings [Gebremedhin et al. 2009; Chiarandini, GCP page]:**
- **Largest First** [Welsh & Powell 1967]: sort by degree; Θ(n + m) with a counting sort; bound ≤ max_i min(deg(v_i) + 1, i).
- **Incidence Degree:** Θ(n + m) with buckets.
- **DSATUR** [Brélaz 1979]: a dynamic rule; Θ((n + m) log n) with a heap.
- Of these, only SL has the d + 1 guarantee.

## 5. Memory in CPython (for the measured-space plot)

**The graph (input):**
- `array('i')` costs 4 bytes per entry and `array('q')` 8 bytes.
- The graph takes about 8(n + 1) + 4·2m + 4·2m = 8n + 16m bytes.
- frb100-40 (n = 4,000, m ≈ 7.43M) needs about 119 MB, and frb30-15 (m = 83,198) about 1.3 MB.

**The algorithms' extra space:**
- **Vertex cover:** a bytearray of n bytes, plus a list of up to n ints (8 bytes per slot; small ints are cached objects). About 9n bytes, Θ(n).
- **Greedy coloring:** two lists of n ints (colors and stamps), about 16n bytes plus the int objects for large values. Θ(n).
- **Smallest-last:** `deg`, `pos` and `vert` are `array('i')` (4 bytes per entry, 12n bytes), `start` has Δ + 2 entries, and the returned order is a list of n ints (8n bytes of pointers plus the int objects). Θ(n). Flat arrays rather than lists avoid a pointer dereference per access: the ordering takes 5.8 s instead of 9.0 s at n = 10⁶. On the small dense FRB graphs, which fit in the CPU cache, lists are about 30% faster instead (423 ms against 589 ms on frb59-26-1), because every array read creates an integer object. The flat arrays were kept.
- Extra space should therefore grow with n only, not with m. The benchmark checks this.

## 6. Dataset optima (FRB / BHOSLIB)

`frbN-K-i` comes from Model RB [Xu & Li 2000; Xu et al. 2007]: N groups of K vertices (vertex g·K + j is in group g), with a planted solution.

- **As published (`clq` form, Network Repository [Rossi & Ahmed 2015]):**
    - the groups are independent sets (checked on all instances in Phase 2), so χ ≤ N;
    - the planted solution is an N-clique, so ω ≥ N, and hence **χ = ω = N**.
- **The complement (`mis` form, the original BHOSLIB vertex cover benchmark):**
    - the groups are cliques, so any independent set has at most one vertex per group, and α ≤ N;
    - the planted solution is an independent set of size N, and hence **OPT_VC = N·K − N**.
- **Why the vertex cover comparison is coarse here:** OPT_VC / n = 1 − 1/K is between 93% and 97.5%, so any cover C ⊆ V has |C| / OPT ≤ n / OPT = K / (K − 1) ≤ 1.072. FRB therefore separates the two vertex cover algorithms only within this narrow band, and the worst-case families (§2.2, §3.1) show the real difference.

## 7. Hypotheses (checked in Phase 6)

| # | Hypothesis | Measured by |
|---|---|---|
| H1 | All four algorithms run in Θ(n + m): the log-log slope of time against n + m is about 1. | E1 (FRB), E3 (synthetic) |
| H2 | Basic and randomized vertex cover differ in time by a constant factor only (the coin). | E1, E3 |
| H3 | SL coloring costs a constant factor (about 2–3×) more than natural coloring: it makes one more Θ(n + m) pass. | E1, E3, the SL split |
| H4 | Basic VC ≤ 2·OPT always. On FRB `mis` both algorithms are within K/(K − 1) ≤ 1.072 of OPT. | E2, E5 |
| H5 | Randomized VC finds smaller covers than basic VC on average (one vertex per selected edge instead of two), with run-to-run variance. | E2 (30 seeds), E5 |
| H6 | SL never uses more than d + 1 colors, and uses fewer colors than the natural order on FRB and on the adversarial families. | E2, E5 |
| H7 | Neither coloring reaches χ = N on FRB `clq` (these are hard instances); the gap is measured. | E2 |
| H8 | Extra memory grows with n, not m. | E4 |

## References

- Batagelj, V., Zaversnik, M. (2003). An O(m) algorithm for cores decomposition of networks. arXiv:cs/0310049.
- Brélaz, D. (1979). New methods to color the vertices of a graph. *CACM* 22(4):251–256.
- Chiarandini, M. Graph coloring benchmarks and heuristics. https://www.imada.sdu.dk/u/marco/gcp/
- Dinur, I., Safra, S. (2005). On the hardness of approximating minimum vertex cover. *Annals of Mathematics* 162(1):439–485.
- Gebremedhin, A. H., Tarafdar, A., Nguyen, D., Pothen, A. (2009). Ordering for coloring and more. Extended abstract, CSC09. https://eecs.wsu.edu/~assefaw/publications/csc09.pdf
- Gyárfás, A., Lehel, J. (1988). On-line and first fit colorings of graphs. *J. Graph Theory* 12(2):217–227.
- Karp, R. M. (1972). Reducibility among combinatorial problems. In *Complexity of Computer Computations*, 85–103.
- Khot, S., Regev, O. (2008). Vertex cover might be hard to approximate to within 2 − ε. *JCSS* 74(3):335–349.
- Matula, D. W., Beck, L. L. (1983). Smallest-last ordering and clustering and graph coloring algorithms. *JACM* 30(3):417–427.
- Pitt, L. (1985). A simple probabilistic approximation algorithm for vertex cover. Tech. Rep. YALEU/DCS/TR-404, Yale University.
- Rossi, R. A., Ahmed, N. K. (2015). The network data repository with interactive graph analytics and visualization. *AAAI*. https://networkrepository.com
- Salavatipour, M. R. (2013). Approximation algorithms, lecture 1 (§1.4). University of Alberta.
- Skiena, S. S. (2020). *The Algorithm Design Manual*, 3rd ed., ch. 12. Springer.
- Welsh, D. J. A., Powell, M. B. (1967). An upper bound for the chromatic number of a graph and its application to timetabling problems. *The Computer Journal* 10(1):85–86.
- Xu, K., Li, W. (2000). Exact phase transitions in random constraint satisfaction problems. *JAIR* 12:93–103.
- Xu, K., Boussemart, F., Hemery, F., Lecoutre, C. (2007). Random constraint satisfaction: easy generation of hard (satisfiable) instances. *Artificial Intelligence* 171(8–9):514–534.
