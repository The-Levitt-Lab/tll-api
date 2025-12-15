## Vittcoin API (FastAPI)

### Quick infodump

`repositories` is data access. `services` is business logic. `routes` are endpoints. The logic bubbles backwards from there through to the end user.

### Quickstart

1. Install dependencies with [uv](https://docs.astral.sh/uv/):
(note from ben: uv ROCKS and makes python development roughly 10,000x easier)

```bash
uv sync
```

2. Configure environment:

```bash
cp env.example .env
```

3. Run the API (dev server hot reload):

```bash
# Option A: FastAPI CLI (recommended)
uv run fastapi dev app.py --host 0.0.0.0 --port 8000

# Option B: Uvicorn directly
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Open the docs at `http://localhost:8000/docs`.

### Configuration

Environment variables (see `env.example`):

- `APP_NAME` – app title
- `ENV` – environment name (development/production)
- `DEBUG` – enable verbose logging
- `DATABASE_URL` – SQLAlchemy async URL (defaults to the Vittcoin DigitalOcean Postgres DB)
- `ALLOWED_ORIGINS` – comma-separated CORS origins
- `API_V1_PREFIX` – versioned API prefix (default `/api/v1`)
- `AUTO_CREATE_TABLES` – create tables on startup (dev convenience)

To override the default Postgres database, set:

```bash
DATABASE_URL=postgresql+asyncpg://USER:PASS@localhost:5432/DB
```