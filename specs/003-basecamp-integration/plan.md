# Implementation Plan: Basecamp API Integration

**Branch**: `003-basecamp-integration` | **Date**: 2025-10-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-basecamp-integration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement Basecamp 3 OAuth 2.0 authentication to establish integration foundation. Users authenticate via OAuth, select one Basecamp account (enforced single-account limitation), and view connection status. System follows existing Dropbox integration pattern with encrypted token storage, refresh token flow, and graceful degradation on refresh failures. Minimal read-only identity scope requested per least privilege principle. All authentication events logged with metadata for audit trail.

## Technical Context

**Language/Version**: Python 3.11+ (Django backend)  
**Primary Dependencies**: Django 5.2+, Django REST Framework, Basecamp 3 API (OAuth 2.0), existing Dropbox integration pattern  
**Storage**: PostgreSQL (BasecampAccount model), encrypted token storage via existing mechanism  
**Testing**: Django test framework (`python3 web/manage.py test`)  
**Target Platform**: Linux server (Docker containerized)  
**Project Type**: Web application (backend Django API integration)  
**Performance Goals**: OAuth flow <2 min (SC-001), status display <1 sec (SC-002), 95% automatic token refresh (SC-003)  
**Constraints**: Single Basecamp account per user (FR-004), minimal OAuth scope (FR-002), HTTP-only cookies for tokens  
**Scale/Scope**: Authentication foundation for all application users, mirrors existing Dropbox integration scope

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md`:

**Backend (Django):**
- [x] Services organized by entity - Using existing `web/integrations/` structure, mirroring Dropbox pattern
- [x] Using Django REST Framework for all API endpoints - OAuth endpoints via DRF
- [x] Background tasks use Celery - Token refresh can leverage existing Celery infrastructure if needed
- [x] Following SOLID principles - Reusing cloud integration protocols, auth services, status strategies

**Frontend (Next.js):**
- [x] Using Next.js 16+ App Router - Integrations page already exists in App Router
- [x] TypeScript for all code - Existing integrations UI is TypeScript
- [x] shadcn/ui components installed via MCP tools - Existing pattern for integration status display
- [x] TanStack Query for server state - Existing pattern for fetching integration status

**Security:**
- [x] JWT tokens in HTTP-only cookies (not localStorage) - Application auth already configured
- [x] CORS configured with credentials and explicit origins - Existing Django CORS config
- [x] Protected routes via middleware - Integrations page already protected

**Code Quality:**
- [x] DRY: No duplicate code - Reusing Dropbox integration pattern (models, auth, status strategies)
- [x] SOLID: Single responsibility - Separate auth service, status strategy, models
- [x] Python: PEP 8, no future methods, preserve comments - Will follow existing codebase standards
- [x] TypeScript: Strict types - Existing integrations UI follows TypeScript best practices

**Complexity Justification Required If:**
- ✅ NOT adding new Django app - Extending existing `web/integrations/` app
- ✅ NOT breaking DRY - Mirroring proven Dropbox integration architecture
- ✅ NOT violating SOLID - Following established separation: Models → Auth → Status → Views
- ✅ NOT adding client-side auth checks - Backend validates all OAuth and token operations

**Result**: ✅ **PASSED** - All constitutional requirements satisfied. No complexity violations.

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
web/integrations/                           # Django integrations app (extends existing)
├── models.py                               # Add BasecampAccount model
├── views.py                                # Add OAuth endpoints (connect, callback, disconnect)
├── urls.py                                 # Add Basecamp URL patterns
├── serializers/
│   └── integrations.py                     # Add Basecamp serializers
├── basecamp/                               # New: Basecamp-specific modules
│   ├── __init__.py
│   ├── auth.py                             # BasecampOAuthAuth service
│   ├── basecamp_service.py                 # BasecampService (mirrors dropbox_service.py)
│   └── config.py                           # Basecamp configuration helpers
├── status/
│   └── strategies/
│       └── basecamp.py                     # Already exists as placeholder - enhance
├── utils/
│   └── token_store.py                      # Extend for Basecamp tokens
└── migrations/
    └── XXXX_basecamp_account.py            # New migration for BasecampAccount model

web/integrations/cloud/
├── factory.py                              # Extend factory to support Basecamp
└── config.py                               # Add Basecamp provider configuration

frontend/src/
├── app/dashboard/integrations/
│   └── page.tsx                            # Existing - displays Basecamp status
├── components/integrations/
│   └── [integration-card].tsx              # Existing - reuse for Basecamp display
└── lib/api/
    └── integrations.ts                     # Existing - status API calls work for Basecamp

web/order_manager_project/
└── settings.py                             # Add BASECAMP_APP_KEY, BASECAMP_APP_SECRET env vars
```

**Structure Decision**: Extends existing `web/integrations/` Django app following proven Dropbox pattern. No new apps needed. Basecamp implementation mirrors Dropbox architecture: separate module (`basecamp/`), auth service, status strategy, models in shared file. Cloud factory extended to support Basecamp provider. Frontend reuses existing integrations UI with status strategy pattern providing Basecamp-specific logic.

## Complexity Tracking

N/A - No constitutional violations. All checks passed.
