# Migrations

This directory contains SQLAlchemy + Alembic migrations.

## Generating a new migration

Once PostgreSQL is running and configured, generate a new migration with:

```bash
uv run alembic revision --autogenerate -m "Describe your change here"
```

## Running migrations

### Upgrade to latest

```bash
uv run alembic upgrade head
```

### Downgrade one version

```bash
uv run alembic downgrade -1
```

### View current revision

```bash
uv run alembic current
```

## Initial setup

Phase 1 establishes the migration infrastructure. The first user-defined migration will be created during Phase 2 when core models are designed.

Currently, only the system metadata table is defined in the ORM, which is used for internal bookkeeping.
