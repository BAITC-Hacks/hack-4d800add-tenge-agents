# Disclosure of pre-existing materials and AI assistance (п. 6.4 Положения)

## Provided by the organizer
- `data/` — case dataset (edges, nodes, transactions parquet), hackathon-only use.
- `starter/` — organizer starter code (loading, validation, DiGraph build, basic metrics, CSV templates). Our `src/moneygraph/io.py` re-implements and extends this logic.

## Third-party libraries (see requirements.txt)
pandas, pyarrow, numpy, networkx, scikit-learn, fastapi, uvicorn, python-louvain (BSD/MIT-family licences).
Vendored in `viewer/vendor/`: Cytoscape.js (MIT), cytoscape-fcose + cose-base + layout-base (MIT).

## Pre-existing code brought by the participant
- <list generic utilities if any were imported, e.g. "paginated HTTP client — not used", or "none">

## AI-agent assistance
- OpenAI Codex was used as a coding agent throughout the competitive window for implementation, tests and documentation, following `AGENTS.md`. Claude was used before and during the event for planning documents in `docs/`. All domain logic, thresholds and rules were decided by the participant and are documented in `docs/07_METHODOLOGY.md`.
- Optional runtime LLM features (`narrate.py`) call the OpenAI API only if `OPENAI_API_KEY` is set; they never alter computed results.

## Data handling
No personal data. gids are synthetic identifiers. Data used only within the hackathon.
