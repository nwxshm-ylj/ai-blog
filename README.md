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
python -m alembic upgrade head
uvicorn app.main:app --reload
```

The default `.env.example` is for local host development and points to
PostgreSQL on `localhost:15432`. Docker Compose overrides the API container's
`DATABASE_URL` so the container connects to `db:5432`.

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

Before starting a freshly provisioned database, run migrations:

```bash
python -m alembic upgrade head
```

For production, create a real env file and set strong private values:

```bash
cp .env.production.example .env.production
# edit .env.production and replace POSTGRES_PASSWORD, DATABASE_URL, SECRET_KEY
docker compose -f docker-compose.prod.yml --env-file .env.production config
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

`SECRET_KEY` must be a long random value in production. Do not reuse the local
development value.

## Alembic

```bash
alembic revision --autogenerate -m "initial"
python -m alembic upgrade head
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

Login test URL:

```text
http://127.0.0.1:8000/auth/login
```
