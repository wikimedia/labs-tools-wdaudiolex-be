# WDAudioLex Backend Tasks

Check items off as they land. Details live in [BACKEND_PLAN.md](BACKEND_PLAN.md).

## Phase 0 — Scaffold

- [x] Recreate agpb-api layout (`app.py`, `common.py`, `service/`, Swagger UI)
- [x] Env file (`.env.example`) with PREFIX, OAuth, Commons, SPARQL, DB URI
- [x] SQLite default + `SQLALCHEMY_DATABASE_URI` for MariaDB
- [x] CORS for `/api/*`, JSON 404/405 handlers
- [x] User-Agent helper for Wikimedia requests
- [x] `UserModel` and `ContributionModel`
- [x] `GET /health` and `/` → `/api` redirect
- [x] OpenAPI contract in `swagger/config.json`
- [x] Postman collection + environment
- [x] Docs: this file + `BACKEND_PLAN.md`
- [x] Remove blueprint / templates app factory
- [x] Phase 0 tests (health, swagger, models, sanitize)
- [x] Pin current Flask 3.1 / Werkzeug 3.1 / SQLAlchemy 2.0 stack (not the old agpb 2.3 pins)

## Phase 1 — Languages + Commons list

- [x] `GET /languages` with `iso`, `iso3`, `qid`, `commons_category`, localized labels
- [x] `GET /languages/<lang_code>` accepts `ig`, `ibo`, or `Q33578`
- [x] `langcodes` mapping; do not copy agpb's static ISO-1-only list
- [x] `GET /commons/files` paginated (`lang`, `continue`, `limit`, optional `speaker`)
- [x] Lingua Libre filename parser + optional Commons SDC `P9533`
- [x] `GET /file/url/<titles>` playable URL
- [x] Tests for parser and language resolution (mocked Commons)

## Phase 2 — Matching

- [x] `POST /match-lexemes` language-scoped Wikidata lexeme search
- [x] Return **forms** with grammatical features
- [x] Rank exact lemma/form, then close matches
- [x] `already_has_audio` and `confidence` (`exact` / `close`)
- [x] Never match across languages
- [x] Tests with mocked Wikidata responses

## Phase 3 — OAuth + write + contributions

- [ ] `GET /auth/login`, `POST /oauth-callback`, `POST /auth/logout`
- [ ] JWT `Authorization: Bearer` via `require_token`
- [ ] `POST /lexeme/audio/add` writes P443 on the form
- [ ] Optional P5237 (and P407) qualifiers
- [ ] Insert `ContributionModel` only after Wikidata succeeds
- [ ] `GET /contributions` filter by username / language
- [ ] `GET/PATCH /users/<id>`
- [ ] Expand `AUTHENTICATION.md`

## Phase 4 — Duplicate / quality guards

- [ ] Reject if that Commons file is already P443 on the form
- [ ] Reject if file language QID ≠ lexeme language
- [ ] Reject replay of the same filename in local contributions
- [ ] Allow extra P443 on a form that already has audio, but keep the flag
- [ ] Tests for each guard

## Phase 5 — Engagement APIs

- [ ] `POST /skips` hide a file for the current user
- [ ] Needs-audio filter on matching / file list
- [ ] `GET /varieties` suggested P5237 items
- [ ] `GET /stats/me` and `GET /stats/leaderboard`
- [ ] Recent activity + session progress fields on add/skip
- [ ] Audio URL present on every file/match payload

## Phase 6 — Swagger + Postman sync

- [ ] Keep `swagger/config.json` in sync with implemented routes
- [ ] Keep Postman collection examples current
- [ ] Swagger UI served at `/api`

## Phase 7 — Tests

- [ ] Parser, lang mapping, sanitize
- [ ] Resource tests with mocked Commons / Wikidata
- [ ] Auth-required write test
- [ ] Guard tests

## Phase 8 — Toolforge harden

- [ ] MariaDB via `SQLALCHEMY_DATABASE_URI`
- [ ] Secrets in env (never commit consumer secret)
- [ ] Gunicorn / Toolforge webservice runbook in README
- [ ] Confirm User-Agent and Python 3.12+
