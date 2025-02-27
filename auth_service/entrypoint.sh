#!/bin/sh
set -e

alembic upgrade head

python cli.py ${ADMIN_EMAIL} ${ADMIN_PASS} || true

uvicorn src.main:app --host 0.0.0.0 --port 8001
