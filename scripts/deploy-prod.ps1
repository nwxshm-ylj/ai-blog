param(
    [string]$EnvFile = ".env.production"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $EnvFile)) {
    throw "Environment file '$EnvFile' was not found. Copy .env.production.example to .env.production and set production secrets first."
}

python -m alembic upgrade head
docker compose -f docker-compose.prod.yml --env-file $EnvFile up -d --build
