# Verification Checklist

This is the definition of done. Checkboxes reflect tests actually run on
23 September; unmarked items still need the final rehearsal or human action.

## Organizer must-haves

- [x] One documented pipeline command creates all three CSV files locally in
  less than five minutes without manual steps.
- [x] `nodes_roles.csv` has exactly 2,248 rows and the required non-empty
  columns: `gid`, `role`, `role_score`, `cluster_id`, `priority_score`, and
  numeric `evidence`.
- [x] Every role has a documented formal rule/metric and three arbitrary gids
  can be explained from computed evidence in under one minute each.
- [x] Every node has a cluster; `clusters.csv` contains cluster size, seed
  count, internal turnover, top gids, and a cautious hypothesis.
- [x] `top_nodes.csv` contains 30 sorted rows with numeric `why` text.
- [x] The generated viewer embeds all 2,248 exact gids as strings, all 3,119
  directed edges, roles, and detail facts; its JavaScript parses.
- [ ] Refreshed visual check of the viewer search and directed arrows. Browser
  automation blocked the local `file://` page and disallowed alternate routes;
  the earlier user screenshot confirmed base rendering before the layout fix.

## Data and scientific checks

- [x] All 19 isolated seeds remain in the output.
- [x] Depth-four no-outflow nodes are not labelled terminal merely because
  traversal stopped.
- [x] Seed pass-through rules do not rely on incomplete incoming amounts.
- [x] Directed and weighted calculations remain directed/weighted; every
  undirected projection is disclosed.
- [x] Repeated runs produce stable CSVs with deterministic tie-breaking.
- [x] All interpretations say “observed graph” and use hypothesis language.

## Repository and judging checks

- [x] README contains the actual install, pipeline, viewer, output, limitations,
  role-threshold, and one-million-node scaling instructions.
- [x] The solution diagram is present.
- [x] Core functionality works without a personal account or LLM key.
- [x] Secrets and private organizer/event materials are not tracked.
- [x] Organizer starter code, third-party libraries, and AI assistance are
  accurately disclosed.
- [x] Data distribution is resolved: either allowed inputs are committed or the
  exact organizer-approved placement step is documented and tested.
- [x] Pipeline verification and viewer structural smoke testing ran separately;
  the viewer needs no local server.
- [x] A fresh clone of the pushed `7ac91e1` installed dependencies, rebuilt
  outputs in 2.93 seconds, passed four tests, and remained clean.
- [x] Final remote repository state and platform submission were verified
  before the 18:00 deadline; the portal displayed “Решение сдано” at 15:47.

## Optional score boosters

- [ ] At least one useful temporal pattern appears in evidence.
- [ ] Resilience, cycles, or anomaly findings are reproducible and explained.
- [ ] Any LLM feature is grounded in computed facts and has a working fallback.
