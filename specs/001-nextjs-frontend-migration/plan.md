# Implementation Plan: Next.js Frontend Migration

**Branch**: `001-nextjs-frontend-migration` | **Date**: 2025-10-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-nextjs-frontend-migration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Migrate the AA Order Manager from Django server-rendered templates to a modern Next.js 16 frontend with Django REST API backend. The system manages Orders, Reports, and Leases with external integrations (Dropbox, Basecamp). Primary goals: implement JWT authentication with HTTP-only cookies, create responsive UI using shadcn/ui components, maintain feature parity with existing Django application, and support 10-50 concurrent users with performance targets (login <10s, dashboard <2s, operations <1s).

Technical approach: Django backend stays largely intact but adds Django REST Framework for API layer. New Next.js frontend consumes API with TypeScript, TanStack Query for server state, and React Context for client state (auth, theme). Docker Compose orchestrates all services (PostgreSQL, Redis, Celery, Django backend, Next.js frontend) for consistent development environment.

## Technical Context

**Language/Version**: Python 3.11+ (backend), Node 20 (frontend), TypeScript 5+ (frontend)  
**Primary Dependencies**: Django 5.2+, Django REST Framework, Next.js 16+, React 19+, shadcn/ui, TanStack Query v5  
**Storage**: PostgreSQL (existing), Redis (Celery broker), localStorage (dark mode preference only)  
**Testing**: Manual testing for MVP (automated E2E deferred), Django test framework for backend API validation  
**Target Platform**: Linux server (Docker containerized), Desktop web browsers (Chrome, Firefox, Safari)  
**Project Type**: Web application - Django backend + Next.js frontend  
**Performance Goals**: Login <10 seconds, dashboard load <2 seconds, CRUD operations reflect changes <1 second, maintain targets with 10-50 concurrent users  
**Constraints**: HTTP-only cookies for JWT tokens (XSS prevention), no rate limiting (simplified MVP), basic audit logging (created_at/updated_at/created_by/updated_by), no password complexity requirements  
**Scale/Scope**: 10-50 concurrent users (small team), 6 user stories (3 P1, 1 P2, 2 P3), 46 functional requirements, 13 success criteria, 6 main pages (Login, Dashboard, Integrations, Orders, Reports, Leases)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md`:

**Backend (Django):**
- [ ] Services organized by entity (lease/, report/, order/), not workflow
- [ ] Using Django REST Framework for all API endpoints
- [ ] Background tasks use Celery
- [ ] Following SOLID principles (repositories, services, serializers)

**Frontend (Next.js):**
- [ ] Using Next.js 16+ App Router (not Pages Router)
- [ ] TypeScript for all code
- [ ] shadcn/ui components installed via MCP tools
- [ ] TanStack Query for server state, React Context for client state

**Security:**
- [ ] JWT tokens in HTTP-only cookies (not localStorage)
- [ ] CORS configured with credentials and explicit origins
- [ ] Protected routes via middleware

**Code Quality:**
- [ ] DRY: No duplicate code, reusable utilities
- [ ] SOLID: Single responsibility, clear abstractions
- [ ] Python: PEP 8, no future methods, preserve comments
- [ ] TypeScript: Strict types, no any unless justified

**Complexity Justification Required If:**
- Adding new Django app (orders app handles coupled entities)
- Breaking DRY (must justify why duplication acceptable)
- Violating SOLID (must show alternative analysis)
- Client-side auth checks (backend must always validate)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
web/                                # Django backend (existing, augmented)
├── manage.py
├── order_manager_project/
│   ├── settings.py                 # Add DRF, JWT, CORS configuration
│   ├── urls.py                     # Include api URLs
│   └── celery.py                   # Existing Celery config
├── api/                            # NEW: REST API app
│   ├── __init__.py
│   ├── serializers/
│   │   ├── __init__.py
│   │   ├── auth.py                 # UserSerializer, TokenSerializer
│   │   ├── orders.py               # OrderSerializer
│   │   ├── reports.py              # ReportSerializer
│   │   ├── leases.py               # LeaseSerializer
│   │   └── integrations.py         # IntegrationStatusSerializer
│   ├── views/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Login, logout, token refresh, user profile
│   │   ├── dashboard.py            # Dashboard data aggregation
│   │   ├── orders.py               # OrderViewSet
│   │   ├── reports.py              # ReportViewSet
│   │   ├── leases.py               # LeaseViewSet
│   │   └── integrations.py         # Integration status, connect/disconnect
│   └── urls.py                     # API URL routing
├── orders/                         # Existing app (models stay)
│   ├── models.py                   # Order, Report, Lease models + audit fields
│   ├── services/                   # Entity-centric organization
│   │   ├── order/
│   │   ├── report/
│   │   └── lease/
│   └── repositories/               # Data access layer
│       ├── lease_repository.py
│       └── document_images_link_repository.py
├── integrations/                   # Existing app
│   ├── models.py                   # Integration models
│   ├── dropbox/                    # Dropbox service
│   └── status/                     # Status checking service
├── core/                           # Existing app
│   └── views.py                    # Keep Django admin accessible
└── requirements.txt                # Add: djangorestframework, djangorestframework-simplejwt, django-cors-headers

frontend/                           # NEW: Next.js application
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout (AuthProvider, ThemeProvider, Toaster)
│   │   ├── page.tsx                # Root redirect logic
│   │   ├── login/
│   │   │   └── page.tsx            # Login page (P1)
│   │   └── dashboard/
│   │       ├── page.tsx            # Dashboard page (P1)
│   │       ├── integrations/
│   │       │   └── page.tsx        # Integrations page (P2)
│   │       ├── orders/
│   │       │   └── page.tsx        # Orders page (P3)
│   │       ├── reports/
│   │       │   └── page.tsx        # Reports page (P3)
│   │       └── leases/
│   │           └── page.tsx        # Leases page (P3)
│   ├── components/
│   │   ├── ui/                     # shadcn/ui components (installed incrementally)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   └── ...                 # Others as needed per phase
│   │   ├── auth/
│   │   │   └── login-form.tsx      # Login form component
│   │   ├── theme-provider.tsx      # next-themes provider
│   │   └── theme-toggle.tsx        # Dark mode toggle
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts           # Fetch client with credentials
│   │   │   └── types.ts            # TypeScript interfaces for API
│   │   ├── auth/
│   │   │   ├── api.ts              # Auth API functions
│   │   │   └── storage.ts          # User storage (localStorage)
│   │   └── utils.ts                # Utility functions
│   └── hooks/
│       └── useAuth.tsx             # Auth context and hook
├── middleware.ts                   # Route protection middleware
├── components.json                 # shadcn/ui configuration
├── tailwind.config.ts              # Tailwind + dark mode config
├── tsconfig.json                   # TypeScript configuration
├── next.config.js                  # Next.js configuration
├── package.json                    # Frontend dependencies
├── .env.local                      # NEXT_PUBLIC_API_URL
└── Dockerfile                      # Node 20 Alpine container

docker-compose.yml                  # Orchestration (updated)
├── db (PostgreSQL)
├── redis (Celery broker)
├── web (Django backend)            # Port 8000, API at /api/
├── worker (Celery)
├── flower (Celery monitoring)
└── frontend (Next.js)              # NEW: Port 3000, hot reload enabled
```

**Structure Decision**: Web application architecture selected. Django backend (web/) remains in place with new api/ app for REST endpoints. Next.js frontend (frontend/) created as separate directory with src/ structure. This follows the constitution's mandate for frontend/backend separation. Docker Compose coordinates all services. Existing orders/ app structure retained but organized entity-centrically (orders/services/lease/, orders/services/report/, orders/services/order/) per constitution requirements.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations**: This implementation fully complies with the constitution. Backend uses Django REST Framework with entity-centric service organization. Frontend uses Next.js 16 App Router with TypeScript and shadcn/ui. JWT tokens stored in HTTP-only cookies. SOLID and DRY principles guide all implementation decisions. No additional complexity justification needed.

---

## Planning Summary

### Phase 0: Research ✅ COMPLETE
**Artifacts Generated**:
- `research.md` - Technical decisions, best practices, alternatives considered for all technology choices

**Key Decisions**:
- Django REST Framework with ViewSets and Serializers
- JWT authentication via djangorestframework-simplejwt with HTTP-only cookies
- Next.js 16 App Router with TypeScript and src/ directory
- shadcn/ui via MCP tools with incremental component installation
- TanStack Query for server state, React Context for client state
- Basic audit logging (created_at, updated_at, created_by, updated_by)
- No password complexity requirements, no rate limiting (per clarifications)
- Small team scale (10-50 concurrent users)
- Docker Compose for development orchestration

**Risk Assessment**: All risks identified and mitigated (see research.md)

### Phase 1: Design & Contracts ✅ COMPLETE
**Artifacts Generated**:
- `data-model.md` - Complete entity schemas, relationships, validation rules, migration plan
- `contracts/api-spec.md` - Comprehensive REST API specification with 30+ endpoints
- `quickstart.md` - Developer setup guide with Docker instructions
- `.cursor/rules/specify-rules.mdc` - Updated agent context (auto-generated)

**Data Model Highlights**:
- 4 core entities: User, Order, Report, Lease (with audit fields)
- 1 DTO: IntegrationStatus (computed, not persisted)
- Clear relationships: Order → Report → Lease hierarchy
- Validation rules defined for all fields
- Migration strategy for adding audit fields to existing models

**API Contract Highlights**:
- 30+ REST endpoints across 6 resource groups
- Authentication flow: login, refresh, logout, user profile
- Dashboard aggregation endpoint
- Full CRUD for Orders, Reports, Leases
- Integration status and connect/disconnect endpoints
- Pagination (page_size=20), filtering, sorting
- HTTP-only cookies for JWT tokens
- TypeScript types provided for frontend

**Quickstart Highlights**:
- Docker-first workflow (5 services: db, redis, web, worker, frontend)
- Step-by-step setup instructions
- Common issues & solutions
- Manual test plan covering all 6 user stories
- API testing examples (curl, Postman)
- Development workflow guidance

### Constitution Compliance

**✅ Backend (Django)**:
- Services organized by entity (orders/services/order/, orders/services/report/, orders/services/lease/)
- Django REST Framework for all API endpoints
- Celery for background tasks (existing, maintained)
- SOLID principles: Repositories for data access, Services for business logic, Serializers for API contracts

**✅ Frontend (Next.js)**:
- Next.js 16 App Router (not Pages Router)
- TypeScript for all code
- shadcn/ui via MCP tools with blocks prioritized
- TanStack Query for server state, React Context for client state

**✅ Security**:
- JWT tokens in HTTP-only cookies (not localStorage)
- CORS configured with credentials and explicit origins (localhost:3000 dev)
- Protected routes via Next.js middleware
- Backend validation (never trust frontend)

**✅ Code Quality**:
- DRY: Reusable serializers, custom hooks, shared utilities
- SOLID: Single responsibility (ViewSets, hooks, components)
- Python: PEP 8 compliant (auto-formatted)
- TypeScript: Strict mode, no `any` without justification

### Technology Stack Summary

**Backend**:
- Python 3.11+, Django 5.2+
- Django REST Framework, djangorestframework-simplejwt
- PostgreSQL (existing), Redis (existing)
- Celery (existing, maintained)
- django-cors-headers

**Frontend**:
- Node 20, Next.js 16+, React 19+, TypeScript 5+
- shadcn/ui (Radix UI + Tailwind CSS)
- TanStack Query v5, next-themes
- Sonner (toast notifications)

**Development**:
- Docker & Docker Compose
- Hot reload (both backend and frontend)
- Manual testing (automated E2E deferred)

### Performance Targets

- **Login**: < 10 seconds
- **Dashboard load**: < 2 seconds  
- **CRUD operations**: Changes reflected < 1 second
- **Concurrent users**: 10-50 without degradation
- **Pagination**: 20 items per page (configurable up to 100)
- **Toast notifications**: Success 5s auto-dismiss, errors manual dismiss

### Security Posture

- **Authentication**: JWT tokens, HTTP-only cookies, SameSite=Lax
- **Passwords**: No complexity requirements (user discretion per clarification)
- **Rate Limiting**: None (simplified MVP per clarification)
- **Audit Logging**: Basic (created_at, updated_at, created_by, updated_by)
- **CORS**: Credentials required, explicit origins only
- **Authorization**: Backend always validates (staff checks for admin features)

### Scope Summary

**In Scope** (6 User Stories):
1. **P1**: Secure Login & Authentication (JWT with HTTP-only cookies)
2. **P1**: View Dashboard with Integration Status (welcome, integration cards, dark mode)
3. **P2**: Manage External Integrations (Dropbox/Basecamp connect/disconnect)
4. **P3**: Manage Orders (CRUD with pagination, filtering)
5. **P3**: Manage Reports (CRUD with order filtering, lease counts)
6. **P3**: Manage Leases (CRUD with agency filtering, runsheet status, external links)

**Out of Scope** (per clarifications and assumptions):
- Server-side rendering optimization (client-side only)
- Mobile responsiveness (desktop-focused)
- Progressive Web App features
- Advanced state management (Redux, Zustand)
- End-to-end automated testing (manual testing sufficient)
- Internationalization (i18n)
- Analytics integration
- WebSocket real-time updates
- Custom shadcn/ui theme (use defaults)
- API versioning (defer to future)

### Next Steps

**Phase 2: Task Generation** (not in this command's scope):
Run `/speckit.tasks` to generate detailed implementation tasks broken down by user story priority with dependencies and parallel execution opportunities.

**Implementation Order** (post-task generation):
1. Setup & Foundation (Django DRF, JWT, CORS, Next.js scaffold)
2. **User Story 1 (P1)**: Authentication flow
3. **User Story 2 (P1)**: Dashboard with integration status
4. **User Story 3 (P2)**: Integration management
5. **User Stories 4-6 (P3)**: Orders, Reports, Leases (can be implemented in parallel)
6. Polish & Testing

**Immediate Actions**:
1. Review this plan and all generated artifacts
2. Run quickstart.md setup to verify Docker environment
3. Test existing implementation (already partially built per git status)
4. Run `/speckit.tasks` to generate implementation task list
5. Begin implementation following constitutional guidelines

---

## Validation Checklist

### Technical Context ✅
- [x] All NEEDS CLARIFICATION items resolved
- [x] Language/version specified (Python 3.11+, Node 20, TypeScript 5+)
- [x] Dependencies listed (Django DRF, Next.js, shadcn/ui, TanStack Query)
- [x] Storage defined (PostgreSQL, Redis, localStorage)
- [x] Testing strategy specified (manual for MVP)
- [x] Performance goals quantified (<10s, <2s, <1s)
- [x] Scale/scope clear (10-50 users, 6 pages, 46 requirements)

### Constitution Check ✅
- [x] Backend Django compliance verified
- [x] Frontend Next.js compliance verified
- [x] Security requirements met (HTTP-only cookies)
- [x] Code quality standards defined (SOLID, DRY)
- [x] No unjustified complexity

### Project Structure ✅
- [x] Documentation tree defined (plan.md, research.md, data-model.md, quickstart.md, contracts/)
- [x] Source code tree specified (web/ backend, frontend/ Next.js)
- [x] Structure decision documented and justified

### Phase 0: Research ✅
- [x] research.md created
- [x] All technical decisions documented with rationale
- [x] Alternatives considered and rejected with reasoning
- [x] Best practices identified for each technology
- [x] Risks assessed and mitigated
- [x] No unresolved questions remain

### Phase 1: Design & Contracts ✅
- [x] data-model.md created with entity schemas
- [x] contracts/api-spec.md created with REST API specification
- [x] quickstart.md created with developer setup guide
- [x] Agent context updated (.cursor/rules/specify-rules.mdc)
- [x] All entities documented with fields, relationships, validation
- [x] All API endpoints specified with request/response formats
- [x] Migration plan defined for audit fields
- [x] TypeScript types provided

### Ready for Phase 2 ✅
- [x] All prerequisites complete
- [x] Spec validated and clarified
- [x] Technical decisions finalized
- [x] Data model designed
- [x] API contracts defined
- [x] Quickstart guide available
- [x] Constitution compliance verified

**Status**: ✅ **READY FOR IMPLEMENTATION** - Proceed to `/speckit.tasks` or begin implementation following this plan.

---

**Plan Generated**: 2025-10-26  
**Branch**: `001-nextjs-frontend-migration`  
**Spec**: [spec.md](./spec.md)  
**Research**: [research.md](./research.md)  
**Data Model**: [data-model.md](./data-model.md)  
**API Contracts**: [contracts/api-spec.md](./contracts/api-spec.md)  
**Quickstart**: [quickstart.md](./quickstart.md)  
**Next Command**: `/speckit.tasks` (generate implementation tasks)
