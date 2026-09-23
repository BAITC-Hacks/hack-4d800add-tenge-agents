# AGENTS.md — Money Graph (HackAlem AI, Finance case)

You are building an AML network-analysis tool in a 5-hour hackathon (competitive window 13:00–18:00, 23 Sep 2026). Solo human operator. Read `docs/00_TASK_AND_SPEC.md` first, then `docs/07_METHODOLOGY.md`, then `docs/02_ARCHITECTURE.md`.

## Non-negotiables
- Work ONLY in this repository. Never add remotes, mirrors, or copy code elsewhere.
- All outputs must be reproducible with ONE command from a fresh clone, offline, on a laptop, in < 5 minutes.
- Core pipeline MUST NOT depend on an LLM or network. LLM features are optional and gated by `OPENAI_API_KEY`; without the key, template fallbacks produce identical file schemas.
- Never hardcode gid lists or results. Every role comes from a documented rule with a numeric threshold.
- Never fabricate node attributes (no names, ages, incomes). Only structure, amounts, dates.
- Wording: findings are hypotheses ("признаки консолидации"), never accusations.
- Never commit secrets. `.env.example` only.
- Determinism: fix `random_state`/`seed=42` everywhere (Louvain, sampling, layout export). Tie-break sorts by `gid`.

## Stack (fixed — do not switch)
- Python 3.11+, `pandas`, `pyarrow`, `networkx`, `numpy`, `scikit-learn` (one small logistic model), `python-louvain` or `networkx.community.louvain_communities`
- UI: single vendored HTML/JS page (`viewer/index.html`) using **Cytoscape.js + fcose** (vendored in `viewer/vendor/`, NO CDN). Served by `FastAPI` + `uvicorn` (`app.py`).
- Optional LLM: `openai` SDK, model from env `OPENAI_MODEL` (default `gpt-4.1-mini`), always wrapped in try/except with fallback.

## Commands
- Install: `pip install -r requirements.txt`
- Run pipeline: `python run.py --data data --out out`
- Run pipeline + open viewer: `python run.py --data data --out out --serve` (serves http://localhost:8000)
- Tests: `pytest -q`
- Lint (optional): `ruff check .`

## Repository layout (create exactly this)
```
run.py                  # single entrypoint: pipeline → out/ → optional serve
app.py                  # FastAPI: serves viewer/ and out/graph.json, /api/ask (optional LLM)
src/moneygraph/
  io.py                 # load parquet, validate, build DiGraph
  features.py           # node features (structural + temporal)
  truncation.py         # depth-4 terminal-vs-truncated classifier
  roles.py              # rule engine → role, role_score, evidence
  clusters.py           # Louvain + cluster summaries + hypotheses
  priority.py           # priority_score, top list, "why"
  export.py             # nodes_roles.csv, clusters.csv, top_nodes.csv, graph.json
  narrate.py            # LLM node cards / Q&A with template fallback
viewer/index.html       # the UI (see docs/06_UI_DESIGN.md)
viewer/vendor/          # cytoscape.min.js, cytoscape-fcose.js, layout-base, cose-base
tests/                  # schema, determinism, rule sanity
docs/                   # all planning docs
out/                    # generated (gitignored except a committed sample run)
data/                   # provided parquet (committed — organizer says hackathon-only use)
```

## Conventions
- Every public function typed; return DataFrames with documented columns.
- `evidence` strings ≤ 200 chars, contain numbers, Russian, template-generated. Example: `"получает от 11 плательщиков (4.2 млн ₸), отдаёт дальше 3% — признаки консолидации"`.
- All thresholds live in `src/moneygraph/config.py` as named constants with a comment on why.
- Log to stdout with timing per stage; whole pipeline must print total seconds at the end.
- Commit after every completed stage with a message like `feat(roles): rule engine + evidence`. Push after every commit.

## Working order (do not reorder)
1. `io.py` + `run.py` skeleton → writes the three CSVs with empty roles (copy logic from `starter/starter.py`). Commit.
2. `features.py` → all structural features + temporal features. Commit.
3. `roles.py` + `truncation.py` → every node has role/score/evidence. Tests for schema (2 248 rows, non-empty evidence). Commit.
4. `clusters.py` + `priority.py` → clusters.csv + top_nodes.csv (≥20). Commit.
5. `export.py` graph.json + `viewer/index.html` + `app.py`. Commit.
6. `narrate.py` (optional LLM) + README + DISCLOSURE. Commit.
7. Fresh-clone test. Final push before 17:50.

## What NOT to do
- Don't build the UI in React/Streamlit. Don't add a Node build step.
- Don't run undirected centralities on the graph without explicitly labelling them as such.
- Don't spend time on optional features before must-haves 1–5 pass (see `docs/08_ACCEPTANCE.md`).
- Don't refactor for beauty. Working > clean.
