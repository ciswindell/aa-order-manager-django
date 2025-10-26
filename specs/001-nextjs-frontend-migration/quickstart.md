# Quickstart Guide: Next.js Frontend Migration

**Feature**: Next.js Frontend Migration  
**Branch**: `001-nextjs-frontend-migration`  
**Date**: 2025-10-26  
**Purpose**: Get development environment running quickly

## Prerequisites

- **Docker & Docker Compose**: Version 20+ (or Docker Desktop)
- **Git**: For cloning repository
- **curl or Postman**: For testing API endpoints (optional)
- **Modern browser**: Chrome, Firefox, or Safari (for frontend testing)

**Optional** (if running without Docker):
- Python 3.11+
- Node.js 20+
- PostgreSQL 13+
- Redis 6+

## Quick Start (Docker - Recommended)

### 1. Clone & Checkout Feature Branch

```bash
git clone <repository-url>
cd aa-order-manager
git checkout 001-nextjs-frontend-migration
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with required values:
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://postgres:postgres@db:5432/order_manager

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Dropbox (optional for development)
DROPBOX_APP_KEY=your-app-key
DROPBOX_APP_SECRET=your-app-secret

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 3. Start All Services

```bash
docker compose up --build
```

**Services Started**:
- `db` (PostgreSQL) - Port 5432
- `redis` (Redis) - Port 6379
- `web` (Django backend) - Port 8000
- `worker` (Celery worker)
- `flower` (Celery monitoring) - Port 5555
- `frontend` (Next.js) - Port 3000

**Wait for**: "Application startup complete" messages from all services

### 4. Run Migrations & Create Superuser

In a new terminal:
```bash
# Run Django migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser
# Follow prompts: username: admin, password: admin (for dev)
```

### 5. Access Applications

| Service | URL | Credentials |
|---------|-----|-------------|
| **Next.js Frontend** | http://localhost:3000 | admin / admin |
| **Django API** | http://localhost:8000/api/ | (via frontend) |
| **Django Admin** | http://localhost:8000/admin/ | admin / admin |
| **Flower (Celery)** | http://localhost:5555/ | (no auth) |

### 6. Test Login Flow

1. Open http://localhost:3000
2. Should redirect to `/login`
3. Enter credentials: `admin` / `admin`
4. Should redirect to `/dashboard`
5. Toggle dark mode (verify persistence)
6. Navigate to different pages
7. Click logout

**Success**: If you can login and see the dashboard, setup is complete! 🎉

---

## Development Workflow

### Making Frontend Changes

Frontend code hot-reloads automatically:
1. Edit files in `frontend/src/`
2. Save changes
3. Browser refreshes automatically
4. Check http://localhost:3000

**Common frontend directories**:
- `frontend/src/app/` - Pages and layouts
- `frontend/src/components/` - React components
- `frontend/src/lib/` - Utilities and API clients
- `frontend/src/hooks/` - Custom React hooks

### Making Backend Changes

Backend hot-reloads automatically (Django runserver):
1. Edit files in `web/`
2. Save changes
3. Django restarts automatically
4. Check http://localhost:8000/api/

**Common backend directories**:
- `web/api/` - REST API endpoints
- `web/orders/` - Orders app (models, services)
- `web/integrations/` - Integration management

### Adding shadcn/ui Components

**IMPORTANT**: Always use MCP tools (in Cursor) to install shadcn components:

```typescript
// In Cursor, use these MCP tools:
// 1. List available components
mcp_shadcn-ui_list_components()

// 2. Get component demo (ALWAYS do this first)
mcp_shadcn-ui_get_component_demo('button')

// 3. Get component code
mcp_shadcn-ui_get_component('button')

// For complex patterns, use blocks:
mcp_shadcn-ui_list_blocks()
mcp_shadcn-ui_get_block('dashboard-01')
```

**Manual installation** (if MCP unavailable):
```bash
cd frontend
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
# etc.
```

### Running Database Migrations

After changing Django models:
```bash
# Create migration
docker compose exec web python manage.py makemigrations

# Apply migration
docker compose exec web python manage.py migrate
```

### Installing Frontend Dependencies

```bash
# Enter frontend container
docker compose exec frontend sh

# Install package
npm install <package-name>

# Or from host (if node_modules mounted)
cd frontend
npm install <package-name>
```

### Installing Backend Dependencies

```bash
# Edit web/requirements.txt, then rebuild:
docker compose down
docker compose up --build web
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f frontend
docker compose logs -f web
docker compose logs -f worker

# Last N lines
docker compose logs --tail=50 frontend
```

### Restarting Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart frontend
docker compose restart web
```

### Stopping Services

```bash
# Stop all (preserves data)
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v
```

---

## API Testing

### Using curl

**Login**:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}' \
  -c cookies.txt \
  -v
```

**Get User Profile** (with cookies):
```bash
curl http://localhost:8000/api/auth/user/ \
  -b cookies.txt
```

**List Orders**:
```bash
curl http://localhost:8000/api/orders/ \
  -b cookies.txt
```

**Create Order**:
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "order_number": "TEST-001",
    "order_date": "2025-01-26"
  }'
```

### Using Postman

1. Import API collection (if available)
2. Set base URL: `http://localhost:8000/api`
3. Enable cookie jar (Settings → General → Cookies)
4. Login: POST `/auth/login/` with credentials
5. Cookies set automatically for subsequent requests

---

## Common Issues & Solutions

### Frontend not loading

**Symptom**: http://localhost:3000 shows "This site can't be reached"

**Solutions**:
1. Check frontend service running: `docker compose ps frontend`
2. Check logs: `docker compose logs frontend --tail=50`
3. Restart: `docker compose restart frontend`
4. Rebuild: `docker compose up --build frontend`

**Common causes**:
- Port 3000 already in use (stop other processes)
- npm install failed (check package.json)
- TypeScript errors (check logs)

### Backend API returning 500 errors

**Symptom**: API calls fail with 500 Internal Server Error

**Solutions**:
1. Check backend logs: `docker compose logs web --tail=100`
2. Check database connection: `docker compose exec web python manage.py dbshell`
3. Run migrations: `docker compose exec web python manage.py migrate`
4. Check settings: Verify `DEBUG=True` in .env

### CORS errors in browser console

**Symptom**: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solutions**:
1. Verify `CORS_ALLOWED_ORIGINS=http://localhost:3000` in `.env`
2. Restart backend: `docker compose restart web`
3. Check credentials included: `fetch(..., { credentials: 'include' })`
4. Verify corsheaders in INSTALLED_APPS and MIDDLEWARE

### Login fails with 401

**Symptom**: Login returns "No active account found with the given credentials"

**Solutions**:
1. Verify superuser created: `docker compose exec web python manage.py createsuperuser`
2. Check username/password correct
3. Verify user is active: Django admin → Users → Check is_active=True
4. Check backend logs for authentication errors

### Dark mode not persisting

**Symptom**: Theme resets to light on page reload

**Solutions**:
1. Check localStorage in browser DevTools (Application → Local Storage)
2. Verify ThemeProvider in layout.tsx
3. Check suppressHydrationWarning on <html> tag
4. Clear browser cache and cookies

### Hot reload not working

**Symptom**: Changes not reflected after saving files

**Solutions**:
1. Check volume mounts in docker-compose.yml
2. Restart service: `docker compose restart frontend` or `docker compose restart web`
3. Check file permissions (Linux: chmod/chown if needed)
4. Try manual refresh: Cmd/Ctrl + Shift + R

### Database connection errors

**Symptom**: "could not connect to server" or "relation does not exist"

**Solutions**:
1. Check db service: `docker compose ps db`
2. Run migrations: `docker compose exec web python manage.py migrate`
3. Check DATABASE_URL in .env
4. Reset database: `docker compose down -v && docker compose up -d db` then migrations

### Celery worker not processing tasks

**Symptom**: Background tasks stuck in pending

**Solutions**:
1. Check worker logs: `docker compose logs worker --tail=100`
2. Check redis: `docker compose ps redis`
3. Restart worker: `docker compose restart worker`
4. Check Flower: http://localhost:5555/ for task status

---

## Testing the Feature

### Manual Test Plan

#### 1. Authentication (P1)
- [ ] Navigate to http://localhost:3000
- [ ] Verify redirect to /login
- [ ] Login with admin/admin
- [ ] Verify redirect to /dashboard
- [ ] Refresh page - verify still logged in
- [ ] Close browser, reopen - verify need to login again (session expired)
- [ ] Logout - verify redirect to /login

#### 2. Dashboard (P1)
- [ ] Login and view dashboard
- [ ] Verify welcome message with username
- [ ] Verify integration status cards (Dropbox, Basecamp)
- [ ] If staff: verify admin links visible
- [ ] Toggle dark mode - verify applies immediately
- [ ] Refresh page - verify dark mode persists

#### 3. Integrations (P2)
- [ ] Navigate to /dashboard/integrations
- [ ] Verify Dropbox card with status
- [ ] If staff: click Connect Dropbox (OAuth flow - may not work without real credentials)
- [ ] Verify Basecamp shows "Coming Soon"
- [ ] Verify toast notifications on actions

#### 4. Orders (P3)
- [ ] Navigate to /dashboard/orders
- [ ] Verify orders table (may be empty)
- [ ] Click "Create Order"
- [ ] Fill form: order_number, order_date
- [ ] Submit - verify success toast
- [ ] Verify new order in table
- [ ] Click edit - verify form pre-fills
- [ ] Update order - verify success
- [ ] Click delete - verify confirmation
- [ ] Confirm delete - verify removed from table

#### 5. Reports (P3)
- [ ] Navigate to /dashboard/reports
- [ ] Create report linked to order
- [ ] Filter by order
- [ ] Verify lease count displays
- [ ] Edit report
- [ ] Verify changes persist

#### 6. Leases (P3)
- [ ] Navigate to /dashboard/leases
- [ ] Create lease linked to report
- [ ] Filter by agency
- [ ] Verify runsheet status badge
- [ ] Verify external links (if any)
- [ ] Edit lease
- [ ] Verify changes persist

#### 7. Error Handling
- [ ] Try invalid login - verify error toast stays visible
- [ ] Create order with missing fields - verify validation errors
- [ ] Try to delete order with reports - verify error message
- [ ] Disconnect internet - verify network error handling
- [ ] Reconnect - verify auto-retry works

#### 8. Performance (10-50 concurrent users target)
- [ ] Login - should complete < 10 seconds
- [ ] Dashboard load - should complete < 2 seconds
- [ ] CRUD operations - changes reflect < 1 second
- [ ] Pagination - navigate through large lists smoothly

### Automated Testing (Deferred)

Automated E2E tests deferred per clarifications. Manual testing sufficient for MVP.

**Future**: Add Playwright or Cypress tests for critical paths.

---

## Next Steps After Setup

1. **Implement User Stories**: Start with P1 (Login, Dashboard)
2. **Install shadcn Components**: Use MCP tools, install incrementally
3. **Create API Endpoints**: Implement serializers and viewsets
4. **Build Frontend Pages**: Create components and hooks
5. **Test Each Feature**: Follow manual test plan
6. **Add Audit Fields**: Create migrations for created_by/updated_by
7. **Deploy to Staging**: Update docker-compose for production

---

## Useful Commands Reference

```bash
# Docker Compose
docker compose up --build          # Build and start all services
docker compose down                # Stop all services
docker compose down -v             # Stop and remove volumes
docker compose restart <service>   # Restart specific service
docker compose logs -f <service>   # Follow logs
docker compose exec <service> sh   # Enter service shell

# Django (in web container)
python manage.py migrate           # Run migrations
python manage.py makemigrations    # Create migrations
python manage.py createsuperuser   # Create admin user
python manage.py shell             # Django shell
python manage.py test              # Run tests

# Frontend (in frontend container)
npm install                        # Install dependencies
npm run dev                        # Start dev server (auto-run)
npm run build                      # Build for production
npm run lint                       # Run ESLint

# Database
docker compose exec db psql -U postgres -d order_manager  # PostgreSQL shell

# Redis
docker compose exec redis redis-cli  # Redis CLI
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       BROWSER (localhost:3000)               │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Next.js Frontend (Port 3000)                       │    │
│  │ - App Router pages                                 │    │
│  │ - shadcn/ui components                            │    │
│  │ - TanStack Query (server state)                   │    │
│  │ - React Context (client state: auth, theme)       │    │
│  │ - Middleware (route protection)                   │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           │ HTTP (credentials: include)      │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Django Backend (Port 8000)                         │    │
│  │ /api/                                              │    │
│  │ - JWT Authentication (HTTP-only cookies)           │    │
│  │ - Django REST Framework                           │    │
│  │ - CORS configured                                 │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│          ┌────────────────┴──────────────┐                 │
│          │                               │                 │
│          ▼                               ▼                 │
│  ┌──────────────┐              ┌──────────────┐           │
│  │ PostgreSQL   │              │  Redis       │           │
│  │ (Port 5432)  │              │ (Port 6379)  │           │
│  │ - Orders     │              │ - Celery     │           │
│  │ - Reports    │              │   broker     │           │
│  │ - Leases     │              └──────────────┘           │
│  │ - Users      │                     │                   │
│  └──────────────┘                     │                   │
│                                       ▼                   │
│                              ┌──────────────┐             │
│                              │ Celery Worker│             │
│                              │ - Background │             │
│                              │   tasks      │             │
│                              │ - Dropbox    │             │
│                              │   discovery  │             │
│                              └──────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

---

## Support & Resources

- **Constitution**: `.specify/memory/constitution.md` - Project principles and standards
- **API Docs**: `specs/001-nextjs-frontend-migration/contracts/api-spec.md` - Complete API reference
- **Data Model**: `specs/001-nextjs-frontend-migration/data-model.md` - Entity schemas
- **Research**: `specs/001-nextjs-frontend-migration/research.md` - Technical decisions
- **Main README**: `README.md` - Project overview

**External Documentation**:
- Next.js: https://nextjs.org/docs
- shadcn/ui: https://ui.shadcn.com/docs
- Django REST Framework: https://www.django-rest-framework.org/
- TanStack Query: https://tanstack.com/query/latest

**Need Help?**
1. Check logs first: `docker compose logs <service> --tail=100`
2. Review this quickstart guide
3. Check Common Issues section above
4. Review existing PRD/tasks documents
5. Consult team or project documentation

---

**Last Updated**: 2025-10-26  
**Maintainer**: Development Team  
**Status**: Active Development

