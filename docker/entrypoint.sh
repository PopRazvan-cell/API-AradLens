#!/bin/sh
set -e

echo "[entrypoint] Initializare baza de date..."
python -m app.init_db

echo "[entrypoint] Pornire API..."
exec uvicorn app.main:app "$@"
