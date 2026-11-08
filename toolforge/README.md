# Deployment

Everything in this directory is for running the WDAudioLex API on [Toolforge](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python)

## Layout Toolforge expects

The tool account name in Gerrit is `wdaudiolex-be` (`labs/tools/wdaudiolex-be`). The public site is then `https://wdaudiolex-api.toolforge.org`.

```text
$HOME/service.template          # copied from toolforge/service.template
$HOME/replica.my.cnf            # Toolforge creates this; do not edit it
$HOME/uwsgi.log
$HOME/www/python/src            # this git checkout
$HOME/www/python/src/.env       # secrets, not committed
$HOME/www/python/venv           # created inside the python3.13 image
```

uWSGI loads `app` from `$HOME/www/python/src/app.py`. That module already imports the Flask app.

## First-time setup

On your laptop, nothing in this directory talks to Toolforge. SSH in, become the tool, then clone.

```bash
ssh login.toolforge.org
become wdaudiolex-be
mkdir -p ~/www/python
git clone "https://gerrit.wikimedia.org/r/labs/tools/wdaudiolex-be" ~/www/python/src
```

### ToolsDB

The credential user is the `user` value in `~/replica.my.cnf`. It looks like `s12345`, not `wdaudiolex-be`.

```bash
mariadb --defaults-file=$HOME/replica.my.cnf -h tools.db.svc.wikimedia.cloud
```

```sql
CREATE DATABASE s57653__wdaudiolex CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Use your own credential user. The name must be `<credential user>__wdaudiolex` (two underscores).

### `.env`

```bash
cp ~/www/python/src/toolforge/env.example ~/www/python/src/.env
chmod 600 ~/www/python/src/.env
```

Build the database URI on the tool account. `quote_plus` is required because ToolsDB passwords contain characters that break a URI. The standard library is enough, so the bastion `python3` can run this before the virtualenv exists.

```bash
python3 - <<'PY'
import configparser
import os
from urllib.parse import quote_plus

cnf = configparser.ConfigParser()
cnf.read(os.path.expanduser("~/replica.my.cnf"))
user = cnf.get("client", "user")
password = quote_plus(cnf.get("client", "password"))
print(
    "SQLALCHEMY_DATABASE_URI="
    f"mysql+pymysql://{user}:{password}"
    f"@tools.db.svc.wikimedia.cloud/{user}__wdaudiolex?charset=utf8mb4"
)
PY
```

Paste that line into `.env`. Also set:

- `IS_DEV=false`. If this is missing, the process stays in development mode and falls back to SQLite on NFS.
- `APP_SECRET` to a long random string (`python3 -c 'import secrets; print(secrets.token_hex(32))'`).
- `DOMAIN=wdaudiolex-be.toolforge.org` so Swagger's server URL is the public host.
- `CONSUMER_KEY` and `CONSUMER_SECRET` from a **Wikidata** OAuth consumer. The callback URL registered on that consumer is the frontend's `/oauth-callback`, because the API only returns `redirect_string` and the browser returns to the frontend.
- `TOOL_CONTACT` to a page or address that identifies the operator. Wikimedia expects that in the User-Agent.

`PORT` is unused once uWSGI is serving the app. The proxy sends traffic to port 8000 inside the pod.

## Deploy

```bash
become wdaudiolex-be
export DATABASE=s57653__wdaudiolex
bash ~/www/python/src/toolforge/deploy.sh
```

The script asks before each step:

1. Copy `service.template` to `~/service.template`. Toolforge will not stop or start without that file.
2. Stop the webservice when one is already running.
3. Dump ToolsDB with a one-off `mariadb` job into `~/wdaudiolex-db-backups/<utc-date>.sql`. The bastion has no `mysqldump`.
4. Tag the current checkout with that date and `git pull --ff-only`.
5. Create `~/www/python/venv` inside the `python3.13` image, if it does not exist yet.
6. Reinstall `requirements.txt` into that virtualenv.
7. Run `create_db.py` (`db.create_all()` only adds missing tables).
8. Copy `service.template` again, then start the webservice.

Check:

```bash
tail -f ~/uwsgi.log
curl -sS https://wdaudiolex-be.toolforge.org/api/health
```

A healthy response is `{"status":"ok","service":"wdaudiolex-be",...}`.

## Files

- `deploy.sh` deploys one step at a time.
- `service.template` selects the `python3.13` image and checks `/api/health`.
- `env.example` is the production `.env` skeleton.

## Logs

Application logs go to `~/uwsgi.log`. To rotate that file, add `log-maxsize` in `~/www/python/uwsgi.ini` as described in [Help:Toolforge/Web/Python](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python). This setup does not add that file.
