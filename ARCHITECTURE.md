# Architecture

The approved implementation has one Python entry point and one browser-native
viewer template. It uses the organizer's three Parquet inputs and no runtime
service, account, LLM, or JS framework.

```text
data/{nodes,edges,transactions}.parquet
    ↓ load, validate, reconcile
run.py: directed weighted NetworkX graph with all 2,248 nodes
    ↓ observed in/out metrics and direct seed links
    ├→ ordered, numeric role rules
    └→ seeded Louvain on a disclosed undirected KZT projection
    ↓ transparent priority score and cluster summaries
results/{nodes_roles,clusters,top_nodes}.csv
    ↓ same precomputed facts embedded into viewer template
results/viewer.html
```

`run.py` has small functions for input validation, graph/features, clusters,
roles, priority, CSV writing, and viewer generation. `viewer/index.html` is
the source template. `results/viewer.html` is standalone, so opening it does
not block pipeline verification with a local server process. `tests/` checks
the official output contract, repeatability, depth-four boundary, isolated
seeds, queue order, and exact gid strings in the viewer payload.

All roles and ranking calculations use directed observed links. Louvain
necessarily uses an undirected graph and sums reciprocal KZT values. Cluster
IDs are canonicalized by each community's minimum gid. The graph, inputs,
and exported data are local; no data is transmitted by the app.
