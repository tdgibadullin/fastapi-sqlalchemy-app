# Show all available commands
default:
    @just --list --unsorted

# Build or rebuild services
build:
    docker compose build

# Create containers and start them in the background
up:
    docker compose up -d

# Stop and remove containers (including orphan containers) and networks
down:
    docker compose down --remove-orphans

# Stop and remove containers (including orphan containers), networks, and volumes
[confirm("WARNING: This will destroy the database and Flower data. Proceed? [y/N]")]
clean:
    docker compose down -v --remove-orphans

# Follow logs for a service (e.g., `just logs worker`). If not specified, the service name defaults to "api"
logs service="api":
    docker compose logs -f {{service}}

# Open an interactive Bash shell inside the API container
bash:
    docker compose exec api bash

# Open an interactive PostgreSQL shell (psql)
psql:
    docker compose exec db psql -U app_user -d app_db

# Auto-fix linting errors and format code (Ruff)
[no-exit-message]
format:
    docker compose run --rm --no-deps api bash -c "ruff check --fix . && ruff format ."

# Run strict linting and type checking (Ruff + mypy)
[no-exit-message]
lint:
    docker compose run --rm --no-deps api bash -c "ruff check . && mypy ."

# Run pytest (e.g., `just test -k test_users`)
[no-exit-message]
test *args:
    docker compose up -d --wait db
    docker compose run --rm --no-deps api pytest {{args}}

# Generate a new Alembic migration (e.g., `just revision "create comments table"`)
revision message:
    docker compose run --rm migrator alembic revision --autogenerate -m "{{message}}"

# Apply all pending Alembic migrations
migrate:
    docker compose run --rm migrator

# Revert the last applied Alembic migration
downgrade:
    docker compose run --rm migrator alembic downgrade -1

# Seed the database with initial dummy data
seed:
    docker compose up -d --wait db
    docker compose run --rm --no-deps api python -m scripts.seed_db
