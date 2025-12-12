## Vittcoin API (FastAPI)

### Quickstart

1. Install dependencies with [uv](https://docs.astral.sh/uv/):
(note from ben: uv ROCKS and makes python development roughly 10,000x easier)

```bash
cd api
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
- `DATABASE_URL` – SQLAlchemy async URL (defaults to SQLite `sqlite+aiosqlite:///./example.db`)
- `ALLOWED_ORIGINS` – comma-separated CORS origins
- `API_V1_PREFIX` – versioned API prefix (default `/api/v1`)
- `AUTO_CREATE_TABLES` – create tables on startup (dev convenience)

To use Postgres instead of SQLite, set:

```bash
DATABASE_URL=postgresql+asyncpg://USER:PASS@localhost:5432/DB
```

### Project Structure

```
api/
  routes/
    v1/
      endpoints/
        health.py
        users.py
      router.py
  deps.py
  core/
    config.py
    logging.py
  db/
    base.py
    session.py
    models/
      user.py
  repositories/
    user_repository.py
  schemas/
    user.py
  services/
    user_service.py
  utils/
    pagination.py
  app.py
  pyproject.toml
  uv.lock
  env.example
  README.md
```

### Notes

- Uses async SQLAlchemy 2.x and works out of the box with SQLite. Switch to Postgres by changing `DATABASE_URL`.
- `AUTO_CREATE_TABLES=true` is for development only; use migrations in production.
