# Implementation Plan: Integration Account Names Display

**Branch**: `006-integration-account-names` | **Date**: November 2, 2025 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/006-integration-account-names/spec.md`

## Summary

Display Basecamp account names and Dropbox account information (name + email) on the integrations page to help users identify which specific accounts they're connected to. This is primarily a display enhancement with data capture improvements for Dropbox OAuth flow.

**Technical Approach**:
- **P1 (Basecamp)**: Backend adds `account_name` to integration status response; frontend displays it. Data already exists in database.
- **P2 (Dropbox)**: Add database migration for `display_name` and `email` fields; fetch from Dropbox API during OAuth; update frontend to display both name and email.
- **P3 (Timestamps)**: Add `connected_at` to integration status response from existing `created_at` field; frontend displays formatted date.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5+ (frontend)  
**Primary Dependencies**: Django REST Framework, Next.js 16+ App Router, shadcn/ui  
**Storage**: PostgreSQL (existing `DropboxAccount` and `BasecampAccount` models)  
**Testing**: Manual testing (no automated tests required per project conventions)  
**Target Platform**: Web application (Linux server backend, browser frontend)  
**Project Type**: Web (Django backend + Next.js frontend)  
**Performance Goals**: Page load <2 seconds with account info displayed  
**Constraints**: No additional API calls after page load; Dropbox API call during OAuth only  
**Scale/Scope**: Single-user display enhancement, affects 2 integration cards, adds 2 DB fields

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md`:

**Backend (Django):**
- [x] Services organized by entity - Using existing `integrations/` app structure
- [x] Using Django REST Framework for all API endpoints - Existing `/api/integrations/status/` endpoint
- [x] Background tasks use Celery - N/A for this feature (synchronous display only)
- [x] Following SOLID principles - StatusService pattern already in place

**Frontend (Next.js):**
- [x] Using Next.js 16+ App Router - Modifying existing `app/dashboard/integrations/page.tsx`
- [x] TypeScript for all code - All frontend code in TypeScript
- [x] shadcn/ui components installed via MCP tools - Using existing Badge, Card components
- [x] TanStack Query for server state - N/A (using existing `getIntegrationStatus` API client)

**Security:**
- [x] JWT tokens in HTTP-only cookies - Unchanged (authentication already configured)
- [x] CORS configured with credentials - Unchanged (existing configuration)
- [x] Protected routes via middleware - `/dashboard/integrations` already protected
- [x] PII handling - Log masking for account names and emails (new requirement from clarifications)

**Code Quality:**
- [x] DRY: No duplicate code - Reusing existing integration status patterns
- [x] SOLID: Single responsibility - Separate concerns: data fetch (OAuth), storage (models), display (status service)
- [x] Python: PEP 8, no future methods - Following existing code standards
- [x] TypeScript: Strict types - Extending existing `IntegrationStatus` interface

**Complexity Justification**: None required - straightforward display enhancement using existing patterns

## Project Structure

### Documentation (this feature)

```text
specs/006-integration-account-names/
├── spec.md              # Feature specification (/speckit.specify output)
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Technical research and decisions
├── data-model.md        # Database schema changes
├── quickstart.md        # Implementation guide
├── contracts/
│   └── api-spec.md      # API endpoint specifications
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
web/                                          # Django backend
├── integrations/
│   ├── models.py                            # MODIFY: Add display_name, email to DropboxAccount
│   ├── migrations/
│   │   └── 000X_add_dropbox_account_info.py # NEW: Database migration
│   ├── status/
│   │   ├── strategies/
│   │   │   ├── basecamp.py                  # MODIFY: Include account_name in status
│   │   │   └── dropbox.py                   # MODIFY: Include display_name, email in status
│   │   └── dto.py                            # MODIFY: Add account_name, account_email, connected_at to IntegrationStatus
│   └── utils/
│       └── token_store.py                    # MODIFY: Store display_name, email for Dropbox
└── api/
    ├── views/integrations.py                 # MODIFY: Fetch Dropbox account info during OAuth callback
    └── serializers.py                        # MODIFY: Add fields to IntegrationStatusSerializer

frontend/                                      # Next.js frontend
└── src/
    ├── app/dashboard/integrations/page.tsx  # MODIFY: Display account names and dates
    └── lib/api/types.ts                      # MODIFY: Extend IntegrationStatus interface
```

**Structure Decision**: Web application structure (Option 2) - Modifications to existing Django backend (`web/`) and Next.js frontend (`frontend/`) directories. No new apps or major structural changes needed.

## Complexity Tracking

No constitutional violations requiring justification. Feature follows established patterns for integration status display.
