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

cd "$SRC" || exit 1

info "This script deploys the WDAudioLex API as a Toolforge Python webservice.
You will be prompted before each step. A failed command prints a warning
and the script continues, unless you answer n. Read each command's output
before you accept the next one.

Runtime is ${PYTHON_TYPE} (the current prebuilt image). Isa used python3.11,
which Toolforge no longer offers. There is no Celery worker and no npm build."

timestamp=$(date -I -u)

# Toolforge refuses stop and start until it knows the image. The file it
# reads is $HOME/service.template, which does not exist on the first deploy.
run "cp $SRC/toolforge/service.template $HOME/service.template"

webservice_status=$(toolforge webservice status 2>&1 || true)
if [[ $webservice_status == *[Nn]ot\ running* ]] || [[ $webservice_status == *no\ webservice* ]]
then
    info "No webservice is running yet, so there is nothing to stop."
else
    run "toolforge webservice stop"
fi

# The login bastion does not ship mysqldump or mariadb-dump.
# The client lives in the Toolforge mariadb image:
# https://wikitech.wikimedia.org/wiki/Help:Toolforge/ToolsDB#Backups
mkdir -p "$BACKUP_DIR"
chmod 750 "$BACKUP_DIR"
dump_cmd="umask o-r; mkdir -p \$TOOL_DATA_DIR/wdaudiolex-db-backups; mariadb-dump --defaults-file=\$TOOL_DATA_DIR/replica.my.cnf --host=tools-readonly.db.svc.wikimedia.cloud --single-transaction ${DATABASE} > \$TOOL_DATA_DIR/wdaudiolex-db-backups/${timestamp}.sql"
run "toolforge jobs delete db-dump >/dev/null 2>&1 || true"
run "toolforge jobs run db-dump --image mariadb --wait --command '${dump_cmd}'"

# Tag current repo state, then update. --ff-only refuses a surprise merge.
run "git tag --force $timestamp"
run "git pull --ff-only"

# toolforge webservice parses every leading dash as its own option, even
# after --. `bash -lc` becomes --last=c, and `pip install -r` becomes
# --replicas. The flags stay inside these scripts; only the path is passed.
info "Installing Python packages inside the ${PYTHON_TYPE} image."
run "toolforge webservice $PYTHON_TYPE shell -- bash $SRC/toolforge/bootstrap-venv.sh"

# Create any missing tables. create_all does not alter existing columns.
run "toolforge webservice $PYTHON_TYPE shell -- bash $SRC/toolforge/create-db.sh"

# Pull may have changed the template. Install that copy before start.
run "cp $SRC/toolforge/service.template $HOME/service.template"

# Start webservice
run "toolforge webservice start"

info "Logs: \$HOME/uwsgi.log
Health: https://wdaudiolex-api.toolforge.org/api/health"
