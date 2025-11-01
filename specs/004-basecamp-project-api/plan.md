# Implementation Plan: Basecamp Project API Extension

**Branch**: `004-basecamp-project-api` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-basecamp-project-api/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Extend the existing `BasecampService` class with methods to interact with Basecamp 3 API for project, to-do list, task, and group management. This enables the foundation for future workflow automation (Phase 2: hardcoded workflow) and template-driven workflow creation (Phase 3: template system). The extension follows existing authentication patterns and adds methods for: listing/retrieving projects, creating to-do lists with duplicate detection, creating groups to organize tasks into sections, creating/updating tasks with assignees, due dates, and group assignments, and adding comments.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Django 5.2+, Django REST Framework, requests library, existing Basecamp OAuth integration  
**Storage**: No new database models required; extends existing `web/integrations/basecamp/basecamp_service.py`  
**Testing**: Manual testing in Django shell (tests not required per spec)  
**Target Platform**: Linux server (Docker containerized)  
**Project Type**: Web application (Django backend extension)  
**Performance Goals**: API methods respond within 3 seconds under normal network conditions; 95% success rate for retry operations  
**Constraints**: Must handle Basecamp API rate limits (HTTP 429) with exponential backoff; must validate duplicate to-do list names before creation  
**Scale/Scope**: Extends single service class with 10 new methods (projects, to-do lists, tasks, groups, comments); integrates with existing BasecampAccount model and OAuth authentication

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md`:

**Backend (Django):**
- [x] Services organized by entity (lease/, report/, order/), not workflow
  - *Compliant: Extending existing `basecamp/` integration service, not creating new entity*
- [x] Using Django REST Framework for all API endpoints
  - *Compliant: Service methods will be called by future API endpoints; no new endpoints in this phase*
- [x] Background tasks use Celery
  - *N/A: No background tasks in this feature*
- [x] Following SOLID principles (repositories, services, serializers)
  - *Compliant: Service layer pattern with clear separation of concerns*

**Frontend (Next.js):**
- [x] Using Next.js 16+ App Router (not Pages Router)
  - *N/A: Backend-only feature*
- [x] TypeScript for all code
  - *N/A: Backend-only feature*
- [x] shadcn/ui components installed via MCP tools
  - *N/A: Backend-only feature*
- [x] TanStack Query for server state, React Context for client state
  - *N/A: Backend-only feature*

**Security:**
- [x] JWT tokens in HTTP-only cookies (not localStorage)
  - *Compliant: Leverages existing authentication; no changes to auth flow*
- [x] CORS configured with credentials and explicit origins
  - *Compliant: No CORS changes; uses existing configuration*
- [x] Protected routes via middleware
  - *Compliant: Service methods assume authenticated context*

**Code Quality:**
- [x] DRY: No duplicate code, reusable utilities
  - *Compliant: Extends existing service class; reuses authentication pattern*
- [x] SOLID: Single responsibility, clear abstractions
  - *Compliant: BasecampService has single responsibility for Basecamp API interaction*
- [x] Python: PEP 8, no future methods, preserve comments
  - *Compliant: Will follow existing codebase style*
- [x] TypeScript: Strict types, no any unless justified
  - *N/A: Backend-only feature*

**Complexity Justification Required If:**
- Adding new Django app (orders app handles coupled entities)
  - *N/A: No new Django app; extending existing integrations app*
- Breaking DRY (must justify why duplication acceptable)
  - *N/A: No duplication planned*
- Violating SOLID (must show alternative analysis)
  - *N/A: No violations*
- Client-side auth checks (backend must always validate)
  - *N/A: Backend-only feature*

**Post-Design Re-Check**: ✅ All checks pass. No constitutional violations.

## Project Structure

### Documentation (this feature)

```text
specs/004-basecamp-project-api/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api-spec.md      # Basecamp 3 API endpoint specifications
├── checklists/
│   └── requirements.md  # Quality validation checklist
└── spec.md              # Feature specification
```

### Source Code (repository root)

```text
web/
├── integrations/
│   ├── basecamp/
│   │   ├── __init__.py
│   │   ├── auth.py                    # Existing OAuth authentication
│   │   ├── config.py                  # Existing configuration helpers
│   │   └── basecamp_service.py        # EXTENDED: Add project/task methods
│   ├── models.py                      # Existing BasecampAccount model
│   └── ...
└── ...

# No new directories or apps required
# Extends existing integrations/basecamp/ module
```

**Structure Decision**: This feature extends the existing `web/integrations/basecamp/` module by adding methods to `basecamp_service.py`. No new Django apps or models required. The service layer approach maintains separation of concerns while building on established authentication infrastructure.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations. All constitutional requirements are met.*
