# AA Order Manager

## Development Setup

### 🐳 Docker (Recommended)

The easiest way to get started is using Docker Compose. This provides:
- ✅ PostgreSQL database with persistent storage
- ✅ Redis for Celery background tasks
- ✅ Celery worker for async task processing
- ✅ Next.js frontend with hot-reload
- ✅ Django REST API backend
- ✅ Flower monitoring UI

**Quick Start:**

```bash
# 1. Create .env file (see DOCKER_DEV_README.md for template)
cp .env.example .env

# 2. Create frontend/.env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > frontend/.env.local

# 3. Start all services
docker compose up -d

# 4. Access the application
# Next.js Frontend: http://localhost:3000/ (login: admin/admin)
# Django admin: http://localhost:8000/admin/ (admin/admin)
# Flower monitoring: http://localhost:5555/
```

**📖 Full Docker documentation:** [DOCKER_DEV_README.md](./DOCKER_DEV_README.md)

---

## Basecamp Workflow Automation

Automatically create Basecamp to-do lists and tasks for orders with a single button click.

### Features

- **4 Product Types Supported:**
  - Federal Runsheets (BLM leases)
  - Federal Abstracts (BLM leases)
  - State Runsheets (NMSLO leases)
  - State Abstracts (NMSLO leases)

- **Intelligent Workflow Creation:**
  - Runsheets: One to-do per unique lease with grouped reports
  - Abstracts: Structured workflow with 5 groups (Setup, Workup, Imaging, Indexing, Assembly)
  - Lease-specific tasks automatically generated
  - HTML-formatted descriptions with clickable links

- **Multi-Product Orders:** Automatically detects and creates workflows for all applicable product types

### Configuration

Set Basecamp project IDs in your `.env` file:

```bash
# Required: Basecamp project IDs for each product type
BASECAMP_PROJECT_FEDERAL_RUNSHEETS=your_project_id
BASECAMP_PROJECT_FEDERAL_ABSTRACTS=your_project_id
BASECAMP_PROJECT_STATE_RUNSHEETS=your_project_id
BASECAMP_PROJECT_STATE_ABSTRACTS=your_project_id
```

### Usage

1. **Connect Basecamp:** Go to Dashboard → Integrations → Connect Basecamp
2. **Create/Edit Order:** Add reports with appropriate leases
3. **Push to Basecamp:** Click "Push to Basecamp" button on order details page
4. **View Workflows:** Check your Basecamp projects for new to-do lists

### Success Scenarios

- ✅ **Complete Success:** All workflows created successfully
- ⚠️ **Partial Success:** Some workflows created, others failed (shows warning)
- ❌ **Complete Failure:** All workflows failed (shows error details)
- ℹ️ **No Applicable Products:** Order has no matching reports

### Troubleshooting

**"Basecamp not connected"**  
→ Connect your Basecamp account in the Integrations page

**"Missing project ID configuration"**  
→ Set the required `BASECAMP_PROJECT_*` environment variables and restart services

**"No workflows to create for this order"**  
→ Order has no reports matching configured product types (Runsheet/Abstract)

---

### Local Development (Alternative)

If you prefer to run services locally without Docker:

## Quick start

1) Run Django (in web/):

```bash
python3 manage.py runserver
```

## Optional: real background tasks

To use Redis + Celery worker instead of eager mode, configure a broker and run a worker.
Eager mode can be enabled by environment variable:

```bash
export CELERY_TASK_ALWAYS_EAGER=1
```

This runs tasks inline (no Redis/worker needed). Unset to return to real background processing.


## Dropbox integration (workspace-first)

- The Dropbox service prefers workspace (shared folder) handling automatically by resolving the first path segment to a shared folder namespace. If no match exists, it falls back to the regular client.
- Shared folder names and namespace IDs are cached per authentication session.
- Dev-only listing endpoint `/integrations/dropbox/list/` was removed.
- DEBUG logs indicate whether workspace or regular mode was used for list and metadata calls.

### Configuration fields (per agency)
- `runsheet_archive_base_path` (required): The base path under the workspace. Must already exist; the app will not create it.
- `runsheet_subfolder_documents_name` (optional): Subfolder name to create under the runsheet archive.
- `runsheet_subfolder_misc_index_name` (optional): Subfolder name to create under the runsheet archive.
- `runsheet_subfolder_runsheets_name` (optional): Subfolder name to create under the runsheet archive.
- `auto_create_runsheet_archives` (bool): If true, when a runsheet archive is missing the system will create `<base>/<lease_number>` and configured subfolders.

### Directory creation behavior
- Trigger: Background runsheet search does not find the runsheet archive.
- Preconditions: `runsheet_archive_base_path` must exist. The app will not create the base path.
- Actions: Create `<base>/<lease_number>`; create configured subfolders; no share links are created.
- Lease updates: Upsert `CloudLocation` for the runsheet archive, assign `lease.runsheet_archive`, and set `lease.runsheet_report_found = False`.

## Integration Status & CTA Framework

Centralized service to evaluate per-user readiness for providers (Dropbox, Basecamp placeholder) and render a gentle, non-blocking action prompt.

- Service: `IntegrationStatusService.assess(user, provider)` returns an `IntegrationStatus` DTO.
- Context processor: enabled in settings as `integrations.context.integration_statuses` and injects `{"dropbox": dto, "basecamp": dto}` for authenticated users.
  - By default, only Dropbox is included. Basecamp will be added once OAuth is wired.
- Template tag: `{% load integration_cta %}{% integration_cta 'dropbox' user %}` renders a CTA when `blocking_problem` is true; otherwise nothing.
- Partial: `web/integrations/templates/integrations/_cta.html` used by the tag and optional global banner in `core/base.html`.
- Caching: In-process TTL (10m) to keep pages fast; force-refresh used for request-time UI to avoid stale prompts.

Migration notes:
- Views/templates should avoid bespoke integration readiness logic. Use the context processor and/or the `{% integration_cta %}` tag.
- Environment flags: set `DROPBOX_APP_KEY`/`DROPBOX_APP_SECRET` for OAuth; optional `INTEGRATIONS_STATUS_LIVE_PROBE` to enable a cheap live probe when tokens are stale.

