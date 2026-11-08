#!/bin/bash
# Create missing tables, using the virtualenv built by bootstrap-venv.sh.
set -euo pipefail

cd "${HOME}/www/python/src"
exec "${HOME}/www/python/venv/bin/python" create_db.py
