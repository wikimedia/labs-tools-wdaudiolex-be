# WDAudioLex Backend

Flask-RESTful service that matches Lingua Libre pronunciation files on
Wikimedia Commons to Wikidata lexeme forms and adds **P443** statements.

## Docs

- [Backend plan](docs/BACKEND_PLAN.md)
- [Phase tasks](docs/TASKS.md)
- [Authentication](docs/AUTHENTICATION.md)
- [Wikidata Lexeme Pronunciation Queries](docs/wikidata_lexeme_pronunciation_queries.md)
- Swagger UI: `http://localhost:5000/api` after the server is running
- OpenAPI: [swagger/config.json](swagger/config.json)
- Postman: [postman/WDAudioLex-BE.postman_collection.json](postman/WDAudioLex-BE.postman_collection.json)
  (import this file, not the environment file). Optional env:
  [postman/WDAudioLex-BE.postman_environment.json](postman/WDAudioLex-BE.postman_environment.json)

## Requirements

- Python 3.12 or newer

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python create_db.py
python app.py
```

If port 5000 is busy:

```bash
python app.py -p 5001
```

Or set `PORT=5001` in `.env`. Then open `http://localhost:5001/api`.

The API prefix is `/api`. `GET /` redirects there. `GET /api/health` is the
liveness check.

## Tests

```bash
pytest
```

## Layout

```bash
app.py                 # resource registration
common.py              # environment
create_db.py
service/               # Flask app, models, resources
swagger/config.json
postman/
docs/
tests/
```

Phase 3 is live: languages, Commons files, matching, OAuth, and
`POST /lexeme/audio/add`. Quality guards and engagement APIs land in later
phases listed in [docs/TASKS.md](docs/TASKS.md).
