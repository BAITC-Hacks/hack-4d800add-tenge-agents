# Status

Update this file at every commit. It is the hourly-checkpoint evidence trail (§6.6) and the first thing Codex reads to resume.

## Now

- **Phase:** plan approved; required pipeline and generated viewer implemented, final delivery checks in progress.
- **Selected task:** Finance — Money Graph, verified in the official portal.
- **Last verified commands:** `python3 run.py --data data --out results` ✅
  (0.25 seconds locally, 2.05 seconds in a fresh venv from a clean remote
  clone); `python3 -m unittest discover -s tests -v` ✅ (4 tests).
- **Verified inputs:** 2,248 nodes, 3,119 edges, 4,840 transactions,
  81 seeds; edge aggregates reconcile with transactions.
- **Input distribution:** user approved including the small official Parquet
  package in this official repository for judging; it was committed and pushed
  in `5eaae53`.
- **Important correction:** the proposed depth-four logistic classifier is not
  approved for the MVP; it reproduced the truncation trap and cannot be called
  a calibrated terminal probability.
- **Next step:** push the sticky-search viewer update, verify a fresh clone from
  the final remote state, and complete the official platform submission form.

## Checkpoints

| # | Time | What changed | What is runnable | Tested | Remaining |
|---|---|---|---|---|---|
| 1 | 14:55 | official materials + audited design baseline | organizer starter → 3 schema CSVs | data integrity + starter sanity | implementation plan |
| 2 | 15:28–15:31 | approved plan; deterministic roles, clusters, ranking, generated viewer | `python3 run.py --data data --out results` | 4 acceptance tests green, 0.23 s run; `5eaae53` pushed | viewer visual inspection; clean-clone rehearsal |
| 3 | 15:33 | user requested `docs/` ignored; public documents and diagram moved to repository root | same pipeline and viewer | 4 tests green; `6fb99b5` pushed | clean-clone rehearsal; submission |
| 4 | 15:36 | clean remote clone and fresh virtual environment install passed; output wording improved | `python3 run.py --data data --out results` from clone | 2.05 s pipeline, 4 tests green, clone remains clean | user visual viewer check; final remote/submission verification |
| 5 | 15:41–15:43 | screenshot review found hidden incoming arrows and right-pane clipping; SVG offsets, layout, short/full gid labels updated | generated `results/viewer.html` | 4 tests green; generated JS parses; `29cdcf7` pushed | refreshed visual confirmation |
| 6 | 15:44 | sidebar search remains visible while the priority list scrolls | regenerated `results/viewer.html` | 4 tests green; generated JS parses | final remote rehearsal; platform submission |

## Known issues / decisions taken during the build

- The organizer archive is hackathon-use-only. Commit it only to this official
  repository, with no extra remote, and verify the remote and submission.
- Browser automation blocked opening the local `file://` viewer and explicitly
  disallowed an alternate browser route. The user-provided screenshot confirmed
  base rendering and exposed arrow/layout issues that have been fixed;
  refreshed visual confirmation remains unavailable.

## Metrics from the last run
- organizer starter elapsed: about 1 second
- role distribution: coordinator 5, consolidator 39, distributor 61, transit
  38, terminal 306, peripheral 1,799
- clusters: 91, including 19 isolated seeds as singletons
- top-5 gids: see `results/top_nodes.csv`; no hardcoded gid list
