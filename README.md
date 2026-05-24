# AI Blog

Production-ready FastAPI starter scaffold with SQLAlchemy 2.0, PostgreSQL, Alembic, Jinja2, and TailwindCSS.

## Project Structure

```text
app/
  api/routes/        HTTP route modules
  core/              settings and application infrastructure
  db/                async SQLAlchemy engine and sessions
  dependencies/      dependency injection providers
  middleware/        middleware registration and implementations
  models/            SQLAlchemy models and declarative base
  repositories/      data access layer
  schemas/           Pydantic schemas
  services/          service layer
  static/            static assets
  templates/         Jinja2 templates
  utils/             shared utilities
  web/               web/template helpers
alembic/             database migration environment
```

## Local Startup

```bash
cp .env.example .env
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

## TailwindCSS

```bash
npm install
npm run build:css
```

For development:

```bash
npm run dev:css
```

## Docker

```bash
cp .env.example .env
docker compose up --build
```

## Alembic

```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

## Local Development Admin

This helper creates or resets a local-only admin account:

```bash
python -m app.scripts.create_dev_admin
```

Credentials:

```text
email: admin@example.com
username: admin
password: admin123
```
