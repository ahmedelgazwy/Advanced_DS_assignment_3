# Dataset: BHOSLIB / FRB graphs

The benchmark uses the 36 FRB graphs of the BHOSLIB collection, as hosted by
Network Repository [Rossi & Ahmed 2015]:

- **Source page:** https://networkrepository.com/bhoslib.php
- **Files:** `https://nrvis.com/download/data/bhoslib/<name>.zip`. Each zip holds `<name>.mtx`, a Matrix Market `coordinate pattern symmetric` file with vertices numbered from 1, and a `readme.html`.
- **Original benchmark:** BHOSLIB by Ke Xu, generated with Model RB [Xu et al. 2007].

The zip files (about 51 MB) are **not committed**. Download them, and check
them against the SHA-256 checksums in [manifest.json](manifest.json), with:

```bash
python -m scripts.download_dataset                       # all 36 graphs
python -m scripts.download_dataset --families frb30-15   # just the smallest family (1 MB)
```

The unit tests and the demo do not need the files. Without them, the tests
that read real FRB files are skipped, and the demo uses a generated graph with
the same structure (`planted_graph`).

## Instances

There are 7 families of 5 instances each, plus `frb100-40`. `frbN-K-i` has N
groups of K vertices, so it has N·K vertices. Vertex `g·K + j` (0-based)
belongs to group g. (`frb56-25` from the original BHOSLIB is not on Network
Repository.)

| Family | N | K | Vertices | Edges, `clq` (published) | Edges, `mis` (complement) | χ of `clq` | Min. vertex cover of `mis` |
|---|---|---|---|---|---|---|---|
| frb30-15 | 30 | 15 | 450 | 83,151–83,231 | 17,794–17,874 | 30 | 420 |
| frb35-17 | 35 | 17 | 595 | 148,572–148,873 | 27,842–28,143 | 35 | 560 |
| frb40-19 | 40 | 19 | 760 | 246,801–247,325 | 41,095–41,619 | 40 | 720 |
| frb45-21 | 45 | 21 | 945 | 386,854–387,795 | 58,245–59,186 | 45 | 900 |
| frb50-23 | 50 | 23 | 1,150 | 579,607–580,640 | 80,035–81,068 | 50 | 1,100 |
| frb53-24 | 53 | 24 | 1,272 | 714,048–714,229 | 94,127–94,308 | 53 | 1,219 |
| frb59-26 | 59 | 26 | 1,534 | 1,048,800–1,049,829 | 125,982–127,011 | 59 | 1,475 |
| frb100-40 | 100 | 40 | 4,000 | 7,425,226 | 572,774 | 100 | 3,900 |

Each family's edge counts are the range over its five instances. Every count,
file size and checksum is in [manifest.json](manifest.json), which
`python -m scripts.download_dataset --write-manifest` regenerates.

## The two forms and their exact optima

Network Repository publishes the dense **clique form** (`clq`). Its
complement, the **independent-set form** (`mis`), is the form the original
BHOSLIB used for minimum vertex cover. The code builds it in memory with
`Graph.complement()`.

- **`clq`:** no edge joins two vertices of the same group; the manifest's `groups_independent` field checks this on all 36 files. The N groups therefore form a proper N-coloring. The planted solution is a clique with one vertex per group, so at least N colors are needed. Hence **χ = N exactly**.
- **`mis`:** every group is a clique, so an independent set holds at most one vertex per group. The planted solution is an independent set of size N. Hence α = N, and the **minimum vertex cover has exactly N·K − N vertices**.

These exact optima let the benchmark report the true approximation ratio of
every algorithm.
