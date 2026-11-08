#!/bin/bash
# Create the virtualenv inside the python3.13 webservice image.
# toolforge webservice treats a leading dash as its own option, so this
# file holds the flags and deploy.sh only passes the script path.
set -euo pipefail

venv="${HOME}/www/python/venv"
src="${HOME}/www/python/src"

rm -rf "$venv"
python3 -m venv "$venv"
"$venv/bin/pip" install --upgrade pip wheel
"$venv/bin/pip" install -r "$src/requirements.txt"
