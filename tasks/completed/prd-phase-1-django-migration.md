## Phase 1 PRD: Django Migration — Setup and Structure

### Introduction / Overview

Migrate the AA Order Manager foundation from a Tkinter desktop app to a Django web project. Phase 1 establishes the Django project scaffolding, isolates legacy code, and prepares a working admin-enabled environment for further migration.

### Goals

- Create and use branch `django-migration`.
- Move legacy code into `legacy/` for reference (imports may break in this branch).
- Consolidate dependencies into a single `requirements.txt` (Django 5.2.5 LTS) and install.
- Initialize Django project in `web/` as `order_manager_project` and app `orders`.
- Configure settings for development (SQLite, static/media paths, timezone, installed apps).
- Run initial migrations, create a superuser, and verify Django admin loads.

### User Stories

- As a developer, I can spin up a Django project with an `orders` app so that future migrations have a stable base.
- As an admin, I can log into Django admin to verify authentication and admin scaffolding works.
- As a teammate, I can find all legacy code in `legacy/` without impacting the new web project.

### Functional Requirements

1. Branching
   - The repository must have a branch named `django-migration` and development must occur there.

2. Legacy isolation
   - Move `app.py` and `src/` into `legacy/` (`legacy/app.py`, `legacy/src/`).
   - Add `legacy/README.md` noting legacy is reference-only on this branch and clearly marked DEPRECATED.
   - Add deprecation banner comments at the top of `legacy/app.py` and `legacy/src/__init__.py` indicating the code is deprecated and read-only on this branch.

3. Dependencies
   - Use a single top-level `requirements.txt` including Django 5.2.5 (LTS) — specify `Django>=5.2,<6.0` — and existing libs (`dropbox`, `pandas`, `openpyxl`).
   - Install with `python3 -m pip install -r requirements.txt`.

4. Django project/app scaffolding
   - Create Django project at `web/order_manager_project/` using `django-admin startproject order_manager_project web`.
   - Create app `orders` under `web/` using `python3 web/manage.py startapp orders`.

5. Settings configuration (development)
   - Database: SQLite (default) for dev.
   - Timezone: `America/Denver`; `USE_TZ = True`; language `en-us`.
   - Static files: `STATIC_URL = "/static/"`; create `web/static/` directory for development assets.
   - Media files: `MEDIA_URL = "/media/"`; set `MEDIA_ROOT` to `web/media/`.
   - Templates: use default Django TEMPLATES; project-level templates can be added later.
   - Installed apps: include `'orders'` and core Django apps.
   - URLs: ensure admin is available at `/admin/` (no app URLs required in Phase 1).

6. Admin readiness
   - Run `python3 web/manage.py migrate` to apply core migrations.
   - Create a superuser via `python3 web/manage.py createsuperuser`.
   - Verify admin loads with `python3 web/manage.py runserver`.

### Non-Goals (Out of Scope)

- Migrating business logic, services, workflows, or integrations.
- Creating application views, forms, templates, or AJAX endpoints.
- Database design for orders or any data models beyond Django defaults.
- Production configuration (WSGI, nginx, CI/CD) beyond basic dev server sanity checks.

### Design Considerations

- Directory layout for Phase 1:
  - `legacy/` contains all current desktop app code (`app.py`, `src/`).
  - `web/` holds the Django project and the `orders` app.
  - Single shared `requirements.txt` at repo root.

### Technical Considerations

- Use Django 5.2.5 (LTS) — currently recommended and under active security support.
- Use SQLite for development; production DB decision deferred.
- Commands use `python3` (Linux).
- Moving legacy code will break legacy imports on this branch by design.
- Keep imports at top-level and follow PEP 8.

### Success Metrics

- `web/manage.py check` reports no errors.
- Admin site reachable at `/admin/` with successfully created superuser.
- `python3 web/manage.py runserver` starts without errors.
- Codebase reflects the new structure (`legacy/`, `web/`, single `requirements.txt`).

### Open Questions

- Do we want a basic `README` update in Phase 1 to document local dev steps, or defer to Phase 2?


