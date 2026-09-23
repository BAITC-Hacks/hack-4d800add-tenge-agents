# Money Graph — «Кто выше?»

> AML network analysis: from a 4-hop transaction dump to a ranked, explained map of who collects, moves, distributes and keeps the money. HackAlem AI 2026 · Finance case · solo build.

**Problem.** An AML analyst knows 81 seed clients; the real network is 2 248. Tracing by hand takes hours per node and only the couriers get blocked.
**Solution.** One command builds the graph, computes structural + temporal features, assigns an explainable role to every node, clusters the network, ranks the top 30 for review, and opens an investigation console.

## Run

```bash
pip install -r requirements.txt
python run.py --data data --out out --serve     # ~<ELAPSED> s, then http://localhost:8000
```
Outputs in `out/`: `nodes_roles.csv` (2 248 rows) · `clusters.csv` (<N> rows) · `top_nodes.csv` (30 rows) · `graph.json` · `run_report.json`.
Tests: `pytest -q`. Works offline; no API key required.

## Solution diagram
```
parquet → features (structural + temporal) → truncation model → role rules → Louvain clusters
        → priority score → CSV exports + graph.json → FastAPI → Cytoscape console
```

## Role dictionary and rules
| Role | Rule (thresholds on this dataset) | Score |
|---|---|---|
| coordinator | <fill from docs/07 with computed quantile values> | |
| consolidator | | |
| distributor | | |
| transit | | |
| terminal (observed) | | |
| terminal (inferred) | p_terminal ≥ 0.60 from truncation model | p_terminal |
| peripheral | none of the above | 0.3 / 0.5 |
Rules are applied in order; first match wins. Full definitions: `docs/07_METHODOLOGY.md`. `src/moneygraph/config.py` holds every constant.

### Truncation model (depth-4 artifact)
Trained on depth 1–3 nodes (outflows fully observed), label = money stayed. Features: <list>. Coefficients: <table from run_report>. Applied to 444 truncated nodes → `p_terminal`.

## Priority score
<formula with weights>; seeds ×0.3. `top_nodes.csv.why` lists the two largest contributions.

## Clustering
Louvain on the **undirected** weighted projection (`seed=42`) — direction is handled in roles/priority, not here. Each cluster: size, seeds, internal turnover, top gids, templated hypothesis.

## Outputs (schemas)
<3 example rows for each CSV>

## Viewer
Search a gid (Enter) → zoom + highlight neighbours + drawer with role, rule, evidence, metrics, priority contributions, counterparties. Filters: role, cluster, depth, seeds, min sum. Ego/Full toggle. Top-30 sidebar. Cluster list.

## Optional AI layer
`OPENAI_API_KEY` in `.env` enables `/api/card/{gid}` (narrative node card) and `/api/ask` (question → answer with gid references). Without a key, template text is used; numbers are identical either way.

## Limitations
- Only outgoing transfers were collected: inbound flows from outside the sample are invisible; balances are partial; seed inflows understated.
- Transfers < 5 000 KZT absent → structuring below threshold is invisible.
- Truncation model assumes depth-4 nodes behave like depth 1–3.
- No ground truth: roles are hypotheses for verification («признаки»), not findings of guilt.
- Louvain ignores direction.

## Scaling to ~1M nodes
<text: igraph/cuGraph, sampled betweenness, leiden, Polars/DuckDB features, graph DB for ego queries, rules stay O(N), UI renders ego/cluster views only>

## Results of this run
<role distribution, clusters count, top-5 gids, elapsed>

## Disclosure
See `DISCLOSURE.md`: organizer starter code, vendored Cytoscape.js (MIT) + fcose (MIT), AI coding agent (Codex) assistance, generic pre-existing utilities.
