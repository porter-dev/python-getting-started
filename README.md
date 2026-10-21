# Django on Porter

A minimal Django project, configured for production, that deploys to Porter with gunicorn, WhiteNoise, and an optional Postgres database.

## What's inside

| Component | Version | Notes |
| --- | --- | --- |
| Python | 3.14 | `python:3.14-slim` base image |
| Django | 6.1.2 | Created with `django-admin startproject`, settings read from env vars |
| gunicorn | 26.2.0 | Binds `0.0.0.0:$PORT`, defaulting to `8000` (see `gunicorn.conf.py`) |
| WhiteNoise | 6.12.0 | Serves static files collected at image build time |
| dj-database-url, psycopg | 3.1.2, 3.3.6 | Reads `DATABASE_URL`, falls back to SQLite |

| Endpoint | Method | Description |
| --- | --- | --- |
| `/` | GET | A page confirming Django is running on Porter |
| `/healthz` | GET | Returns `ok` with no database access, used by the health check |
| `/admin/` | GET | The Django admin, once migrations have run and a superuser exists |

## Run locally

```sh
python3.14 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_DEBUG=true
python manage.py migrate
python manage.py runserver
```

With Docker:

```sh
docker build -t python-getting-started . && docker run -p 8000:8000 -e DJANGO_SECRET_KEY=dev-only-secret python-getting-started
```

Run the tests with `DJANGO_DEBUG=true python manage.py test`.

## Deploy on Porter

### From the dashboard

1. Fork this repo.
2. In https://dashboard.porter.run, create a new app from your GitHub repo. Porter reads `porter.yaml`, builds the Dockerfile, and opens a PR adding a GitHub Actions workflow.
3. Before the first deploy, add `DJANGO_SECRET_KEY` as a secret environment variable on the app. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(50))"`. Without it the app and the predeploy job exit with a clear error.
4. Merge the PR. Every push to `main` redeploys.

See https://docs.porter.run/applications/deploy/deploy-from-github-repo for details.

### From the CLI

Install the CLI (https://docs.porter.run/cli/installation), then:

```sh
porter auth login
porter apply -f porter.yaml
```

Set `DJANGO_SECRET_KEY` as a secret on the app in the dashboard afterwards if you did not provide it beforehand.

### Adding Postgres

The default SQLite database lives inside the container and is not shared between pods, so it is only good for trying the app out. For real data, create a Postgres datastore in Porter (https://docs.porter.run/addons/datastores) and attach its env group to the app, either in the dashboard or by adding it to `porter.yaml`:

```yaml
envGroups:
  - <your-datastore-name>
```

The datastore env group provides `DATABASE_URL`, which Django picks up automatically. If your env group exposes the connection string under a different name, add a `DATABASE_URL` variable that references it. Once Postgres is attached, the predeploy `python manage.py migrate` applies migrations to the shared database before each release goes live.

## Configuration

`porter.yaml` defines:

* `build`: builds the `Dockerfile` at the repo root.
* `predeploy`: runs `python manage.py migrate --noinput` in a separate job before each deploy. With the SQLite fallback it succeeds but only migrates that job's own copy, so it starts to matter once a Postgres env group is attached.
* `services.web`: runs `gunicorn config.wsgi` on port `8000` with 0.25 CPU and 512 MB of memory, and checks `/healthz`.

| Name | Required | Description |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Yes, unless `DJANGO_DEBUG` is on | Django's secret key. Store it as a secret. |
| `DJANGO_DEBUG` | No | Set to `true` for local development. Defaults to off. |
| `DJANGO_ALLOWED_HOSTS` | No | Comma separated hostnames, for example `myapp.example.com`. Defaults to `*`, which is fine for a starter but should be narrowed to your domains in production. `/healthz` works regardless of this setting. |
| `CSRF_TRUSTED_ORIGINS` | No | Comma separated origins with scheme, for example `https://myapp.example.com`. Needed for form posts (including the admin login) from your custom domain. |
| `DATABASE_URL` | No | Database connection string. Defaults to SQLite at `db.sqlite3`. |
| `PORT` | No | Port gunicorn listens on. Defaults to `8000`, matching `porter.yaml`. |
| `WEB_CONCURRENCY` | No | Number of gunicorn workers. Defaults to 1. |
| `DJANGO_LOG_LEVEL` | No | Root log level. Defaults to `INFO`. |

Django trusts the `X-Forwarded-Proto` header from Porter's load balancer, so `request.is_secure()` is correct behind TLS.

Full reference: https://docs.porter.run/applications/configuration-as-code/reference

## Learn more

* https://docs.porter.run/getting-started/quickstart
* https://docs.porter.run/applications/configuration-as-code/overview
* https://docs.porter.run/applications/configure/environment-groups
* https://docs.porter.run/addons/datastores
* https://docs.porter.run/preview-environments/overview
* https://github.com/porter-dev/starters
