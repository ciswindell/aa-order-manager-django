## Relevant Files

- `legacy/README.md` - Root README moved here; marked DEPRECATED and reference-only on this branch.
- `legacy/app.py` - Deprecated legacy entrypoint with deprecation banner comment.
- `legacy/src/__init__.py` - Deprecated package marker with deprecation banner comment.
- `requirements.txt` - Unified dependencies including Django 5.2 LTS and existing libs.
- `web/manage.py` - Django management entrypoint.
- `web/order_manager_project/settings.py` - Dev settings: SQLite, timezone, static/media, installed apps.
- `web/order_manager_project/urls.py` - Base routing; ensures admin at `/admin/`.
- `web/order_manager_project/wsgi.py` - WSGI configuration.
- `web/orders/apps.py` - App configuration for `orders`.
- `web/orders/admin.py` - Placeholder for admin registrations; confirms app is installed.
- `web/orders/__init__.py` - Package marker.
- `web/static/` - Static assets directory for development.
- `web/media/` - Media uploads directory for development.
- `README.md` - Optional: update with local dev steps once Phase 1 completes.
- `.gitignore` - Updated for Django project (SQLite DB, media, collectstatic output).

### Notes

- Use `python3` for all commands on Linux.
- Run the development server with `python3 web/manage.py runserver`.
- If using a virtualenv, ensure it is activated before `pip install -r requirements.txt`.

## Tasks

- [x] 1.0 Create and switch to `django-migration` branch
  - [x] 1.1 Create and switch: `git checkout -b django-migration` (or `git switch -c django-migration`)
  - [x] 1.2 Push branch to origin: `git push -u origin django-migration`

- [x] 2.0 Isolate legacy code into `legacy/` with deprecation notices
  - [x] 2.1 Create directory: `mkdir -p legacy`
  - [x] 2.2 Move files: `git mv app.py legacy/` and `git mv src/ legacy/`
  - [x] 2.3 Add `legacy/README.md` describing DEPRECATED status and reference-only intent
  - [x] 2.4 Add deprecation banner to `legacy/app.py`
  - [x] 2.5 Add deprecation banner to `legacy/src/__init__.py`

- [x] 3.0 Consolidate dependencies in top-level `requirements.txt` (Django 5.2.5 LTS) and install
  - [x] 3.1 Write `requirements.txt` with `Django>=5.2,<6.0`, `dropbox`, `pandas`, `openpyxl`
  - [x] 3.2 Install: `python3 -m pip install -r requirements.txt`

- [ ] 4.0 Initialize Django project in `web/` and create `orders` app
  - [x] 4.1 Create project: `django-admin startproject order_manager_project web`
  - [x] 4.2 Create app: `python3 web/manage.py startapp orders`
  - [x] 4.3 If app created at repo root by mistake, move to `web/orders/`

- [ ] 5.0 Configure development settings (SQLite, `America/Denver`, static/media, installed apps, admin URL)
  - [x] 5.1 In `settings.py`, add `'orders'` to `INSTALLED_APPS`
  - [x] 5.2 Set `TIME_ZONE = 'America/Denver'`, `USE_TZ = True`, `LANGUAGE_CODE = 'en-us'`
  - [x] 5.3 Set `STATIC_URL = '/static/'`; create directory `web/static/`
  - [x] 5.4 Set `MEDIA_URL = '/media/'` and `MEDIA_ROOT = BASE_DIR / 'media'`; create directory `web/media/`
  - [x] 5.5 Ensure admin URL at `/admin/` in `urls.py` (default from `startproject`)

- [ ] 6.0 Run initial migrations, create superuser, verify Django admin loads
  - [x] 6.1 Migrate: `python3 web/manage.py migrate`
  - [x] 6.2 Create superuser: `python3 web/manage.py createsuperuser`
  - [x] 6.3 Run: `python3 web/manage.py runserver` and verify `/admin/` loads

- [x] 6.0 Run initial migrations, create superuser, verify Django admin loads


