#! /usr/bin/env bash
# Deploy the WDAudioLex API on Toolforge.
# Same prompt-before-each-step flow as Isa (labs/tools/Isa), without
# Isa's Celery worker and npm build. This service is JSON only.
#
# Run on the tool account, from any directory:
#   bash ~/www/python/src/toolforge/deploy.sh
# DATABASE must be the ToolsDB name, for example s12345__wdaudiolex.

PYTHON_TYPE=python3.13
SRC="${HOME}/www/python/src"
VENV="${HOME}/www/python/venv"
BACKUP_DIR="${HOME}/wdaudiolex-db-backups"

run() {
    preview "$*"
    read -r -p "Run this command? [Y/n] "
    if [[ ${REPLY:-} =~ ^[Nn]$ ]]
    then
        exit 1
    fi

    if ! eval "$*"
    then
        warn "The previous command didn't exit properly. Check the output above and make sure that things are fine before proceeding."
    fi
}

info() {
    echo -e "\e[1;44m$*\e[0m"
}

warn() {
    echo -e "\e[1;43mWARNING: $*\e[0m"
}

error() {
    echo -e "\e[1;41mERROR: $*\e[0m"
}

preview() {
    echo -e "\e[1;36m$*\e[0m"
}

pip() {
    toolforge webservice "$PYTHON_TYPE" shell -- "$VENV/bin/pip" "$@"
}

if [[ -z ${DATABASE:-} ]]
then
    error "The environment variable DATABASE must be set to the ToolsDB name (for example s12345__wdaudiolex)."
    exit 1
fi

if [[ ! -f "$SRC/.env" ]]
then
    error "Missing $SRC/.env. Copy toolforge/env.example and fill it in before deploying."
    exit 1
fi

if ! grep -E -q '^SQLALCHEMY_DATABASE_URI=mysql\+pymysql://' "$SRC/.env"
then
    error "$SRC/.env must set SQLALCHEMY_DATABASE_URI to a mysql+pymysql ToolsDB URI."
    exit 1
fi

if ! grep -E -q '^IS_DEV=false[[:space:]]*$' "$SRC/.env"
then
    error "$SRC/.env must set IS_DEV=false. The default in code is development mode."
    exit 1
fi

if grep -E -q '^APP_SECRET=changeme' "$SRC/.env" || grep -E -q '^APP_SECRET=[[:space:]]*$' "$SRC/.env"
then
    error "$SRC/.env needs a long random APP_SECRET."
    exit 1
fi

if ! command -v mariadb-dump >/dev/null 2>&1 && ! command -v mysqldump >/dev/null 2>&1
then
    error "Neither mariadb-dump nor mysqldump is on PATH."
    exit 1
fi

if command -v mariadb-dump >/dev/null 2>&1
then
    DUMP=mariadb-dump
else
    DUMP=mysqldump
fi

cd "$SRC" || exit 1

info "This script deploys the WDAudioLex API as a Toolforge Python webservice.
You will be prompted before each step. A failed command prints a warning
and the script continues, unless you answer n. Read each command's output
before you accept the next one.

Runtime is ${PYTHON_TYPE} (the current prebuilt image). Isa used python3.11,
which Toolforge no longer offers. There is no Celery worker and no npm build."

timestamp=$(date -I -u)

# Stop webservice
run "toolforge webservice stop"

# Backup database. The dump is mode 640 so other users on the bastion cannot read it.
mask=$(umask)
umask o-r
mkdir -p "$BACKUP_DIR"
run "$DUMP --defaults-file=$HOME/replica.my.cnf -h tools.db.svc.wikimedia.cloud $DATABASE > $BACKUP_DIR/$timestamp.sql"
umask "$mask"

# Tag current repo state, then update. --ff-only refuses a surprise merge.
run "git tag --force $timestamp"
run "git pull --ff-only"

# The virtualenv must be created inside the webservice image. A venv built
# on the bastion will not load in the python3.13 pod.
if [[ ! -x "$VENV/bin/pip" ]]
then
    info "No virtualenv at $VENV yet. Creating one inside the ${PYTHON_TYPE} image."
    run "toolforge webservice $PYTHON_TYPE shell -- bash -lc 'python3 -m venv ~/www/python/venv && ~/www/python/venv/bin/pip install --upgrade pip wheel'"
fi

# Clear Python packages
if [[ $(pip freeze) ]]
then
    # Keep this quoted so the package list is not expanded into the prompt.
    run 'pip uninstall -y $(pip freeze)'
fi

# Install Python packages
run "pip install -r $SRC/requirements.txt"

# Create any missing tables. create_all does not alter existing columns.
run "toolforge webservice $PYTHON_TYPE shell -- bash -lc 'cd ~/www/python/src && ~/www/python/venv/bin/python create_db.py'"

# Toolforge reads $HOME/service.template, not the copy in the git checkout.
run "cp $SRC/toolforge/service.template $HOME/service.template"

# Start webservice
run "toolforge webservice start"

info "Logs: \$HOME/uwsgi.log
Health: https://wdaudiolex-be.toolforge.org/api/health"
