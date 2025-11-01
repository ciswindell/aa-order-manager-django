# Implementation Plan: Basecamp OAuth Account Selection

**Branch**: `005-basecamp-account-selection` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/005-basecamp-account-selection/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Allow users to choose which Basecamp account to connect when they have access to multiple accounts during OAuth authorization. Currently, the system automatically selects the first account, which prevents users from controlling which account is connected and requires manual database editing to correct. This feature adds a session-based account selection screen that appears after OAuth authorization when multiple accounts are detected, while maintaining auto-selection for single-account users.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5+ (frontend)  
**Primary Dependencies**: Django 5.2+, Django REST Framework, Next.js 16+, React 19+, TanStack Query  
**Storage**: PostgreSQL (account connections), Django session framework (pending selections)  
**Testing**: Manual testing with American Abstract LLC account  
**Target Platform**: Web application (Linux server + browser)  
**Project Type**: Web (Django backend + Next.js frontend)  
**Performance Goals**: Account selection page loads within 2 seconds, supports up to 20 accounts without degradation  
**Constraints**: 15-minute session timeout for pending selections, lazy cleanup pattern for expired sessions  
**Scale/Scope**: Single-user OAuth flow, 1-20 accounts per user, existing `BasecampAccount` model with OneToOne user relationship

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Initial Check (Before Phase 0)**: ✅ PASS  
**Final Check (After Phase 1)**: ✅ PASS

Verify compliance with `.specify/memory/constitution.md`:

**Backend (Django):**
- [x] Services organized by entity (existing `integrations` app handles OAuth, not creating new app)
- [x] Using Django REST Framework for all API endpoints (will add account selection endpoint)
- [x] Background tasks use Celery (N/A - OAuth is synchronous request/response)
- [x] Following SOLID principles (account selection endpoint delegates to OAuth service logic)

**Frontend (Next.js):**
- [x] Using Next.js 16+ App Router (account selection page will use App Router)
- [x] TypeScript for all code (new selection page will be TypeScript)
- [x] shadcn/ui components installed via MCP tools (will use shadcn RadioGroup for account selection)
- [x] TanStack Query for server state, React Context for client state (N/A - selection is one-time flow, not persistent state)

**Security:**
- [x] JWT tokens in HTTP-only cookies (existing implementation, not modified)
- [x] CORS configured with credentials and explicit origins (existing configuration remains)
- [x] Protected routes via middleware (selection page accessible during OAuth, no auth required)

**Code Quality:**
- [x] DRY: No duplicate code, reusable utilities (account selection logic extracted to service method)
- [x] SOLID: Single responsibility, clear abstractions (view handles HTTP, service handles business logic, session handles storage)
- [x] Python: PEP 8, no future methods, preserve comments (will follow existing code style)
- [x] TypeScript: Strict types, no any unless justified (will use proper types for account data)

**Complexity Justification Required If:**
- ❌ Adding new Django app (NOT adding new app - extending existing `integrations` app)
- ❌ Breaking DRY (no code duplication planned)
- ❌ Violating SOLID (clean separation of concerns)
- ❌ Client-side auth checks (backend validates session before completing connection)

**Constitution Compliance**: ✅ PASS - No violations. Feature extends existing `integrations` app following established patterns.

## Project Structure

### Documentation (this feature)

```text
specs/005-basecamp-account-selection/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api-spec.md      # Account selection API endpoint specification
├── checklists/          # Quality validation
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
web/                                    # Django backend
├── api/
│   ├── views/
│   │   └── integrations.py            # MODIFY: Update OAuth callback, add selection endpoint
│   └── urls.py                        # MODIFY: Add account selection route
├── integrations/
│   ├── models.py                      # EXISTING: BasecampAccount model (no changes)
│   └── basecamp/
│       └── basecamp_oauth.py          # EXISTING: OAuth logic (may extract helpers)
└── manage.py

frontend/                               # Next.js frontend
├── src/
│   └── app/
│       └── basecamp/
│           └── select-account/
│               └── page.tsx           # NEW: Account selection page
└── package.json
```

**Structure Decision**: Extending existing web application structure. Backend changes in `web/api/views/integrations.py` for OAuth callback modification and new account selection endpoint. Frontend adds single new page under `frontend/src/app/basecamp/select-account/`. No new Django apps or major structural changes needed - feature extends existing Basecamp integration.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitutional violations. All gates passed.
