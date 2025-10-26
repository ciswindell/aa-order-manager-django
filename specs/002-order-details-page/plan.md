# Implementation Plan: Order Details Page Enhancement

**Branch**: `002-order-details-page` | **Date**: October 26, 2025 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/002-order-details-page/spec.md`

## Summary

Create a dedicated Order Details page at `/dashboard/orders/[id]` that consolidates order information and associated reports in a single view. Users can create orders and immediately land on the details page where they can add reports, search/select leases, and create new leases inline without navigating between multiple pages. This eliminates the current fragmented workflow requiring navigation between separate Orders, Reports, and Leases pages.

**Technical Approach**: Extend existing Next.js frontend with new dynamic route for order details. Create reusable React components for report management and enhanced lease selection. Backend API endpoints already exist for orders, reports, and leases - will leverage existing Django REST Framework endpoints with potential query parameter additions for filtering.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5+ (frontend)  
**Primary Dependencies**: Django 5.2+ with DRF, Next.js 16+ with App Router, shadcn/ui components via MCP  
**Storage**: PostgreSQL database (existing models for Order, Report, Lease)  
**Testing**: pytest for backend (optional unless specified), Next.js build validation for frontend  
**Target Platform**: Web application (Linux server for backend, modern browsers for frontend)  
**Project Type**: Web application with separate backend and frontend  
**Performance Goals**: Order details page load <2s, lease search filtering <300ms, support 10,000 concurrent users  
**Constraints**: Maintain existing data model relationships, preserve HTTP-only cookie authentication, ensure all operations work within existing order/report/lease entity constraints  
**Scale/Scope**: Estimated 8 new frontend components, 1 new route, minimal backend changes (query param additions), ~1500-2000 LOC across frontend

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md`:

**Backend (Django):**
- [x] Services organized by entity (lease/, report/, order/), not workflow
  - *Existing: `orders/services/lease/`, `orders/services/report/`, `orders/services/order/`*
- [x] Using Django REST Framework for all API endpoints
  - *Existing: `/api/orders/`, `/api/reports/`, `/api/leases/` already implemented*
- [x] Background tasks use Celery
  - *Not needed for this feature - no async operations required*
- [x] Following SOLID principles (repositories, services, serializers)
  - *Existing architecture maintained, no new backend services needed*

**Frontend (Next.js):**
- [x] Using Next.js 16+ App Router (not Pages Router)
  - *Confirmed: `frontend/src/app/` structure with App Router*
- [x] TypeScript for all code
  - *Confirmed: All existing frontend code in TypeScript*
- [x] shadcn/ui components installed via MCP tools
  - *Will use: Dialog, Table, Input, Select, Button, Card (existing + potential new components via MCP)*
- [x] TanStack Query for server state, React Context for client state
  - *Confirmed: Existing hooks use `@tanstack/react-query` (useOrders, useReports, useLeases)*

**Security:**
- [x] JWT tokens in HTTP-only cookies (not localStorage)
  - *Confirmed: Existing auth implementation uses HTTP-only cookies*
- [x] CORS configured with credentials and explicit origins
  - *Existing: Backend configured for frontend origin*
- [x] Protected routes via middleware
  - *Existing: `frontend/src/middleware.ts` protects `/dashboard/*` routes*

**Code Quality:**
- [x] DRY: No duplicate code, reusable utilities
  - *Will create: Reusable LeaseSearchSelect, InlineLeaseCreateForm, ReportFormDialog components*
- [x] SOLID: Single responsibility, clear abstractions
  - *Design: Each component has single purpose (display, search, create, edit)*
- [x] Python: PEP 8, no future methods, preserve comments
  - *No new backend code expected - using existing endpoints*
- [x] TypeScript: Strict types, no any unless justified
  - *Will use: Existing type definitions from `lib/api/types.ts`, extend as needed*

**Complexity Justification Required If:**
- ❌ Adding new Django app - *Not adding, using existing `orders` app*
- ❌ Breaking DRY - *Creating reusable components to avoid duplication*
- ❌ Violating SOLID - *Following single responsibility per component*
- ❌ Client-side auth checks - *Using existing middleware, backend validates all operations*

**Constitution Check Result**: ✅ **PASSED** - No violations, no justifications needed

## Project Structure

### Documentation (this feature)

```text
specs/002-order-details-page/
├── plan.md              # This file
├── research.md          # Technical decisions and patterns
├── data-model.md        # Entity relationships and frontend data structures
├── quickstart.md        # Implementation guide for developers
├── contracts/           # API contract specifications
│   └── api-spec.md      # REST endpoint contracts
└── checklists/
    └── requirements.md  # Specification quality validation
```

### Source Code (repository root)

```text
backend/                          # Django backend (minimal changes)
└── web/
    └── api/
        └── views/               # May add query parameters to existing views
            ├── orders.py        # GET /api/orders/:id/ (already exists)
            ├── reports.py       # GET /api/reports/?order_id=X (verify exists)
            └── leases.py        # GET /api/leases/?search=X (may need to add)

frontend/                        # Next.js frontend (primary changes)
├── src/
│   ├── app/
│   │   └── dashboard/
│   │       └── orders/
│   │           ├── page.tsx              # Existing orders list
│   │           └── [id]/
│   │               └── page.tsx          # NEW: Order details page
│   ├── components/
│   │   ├── orders/                       # NEW: Order-specific components
│   │   │   ├── OrderDetailsHeader.tsx   # Display order info + edit/delete
│   │   │   └── OrderReportsSection.tsx  # Reports table + add button
│   │   ├── reports/                      # NEW: Report-specific components
│   │   │   └── ReportFormDialog.tsx     # Create/edit report modal
│   │   ├── leases/                       # NEW: Lease-specific components
│   │   │   ├── LeaseSearchSelect.tsx    # Enhanced searchable multi-select
│   │   │   └── InlineLeaseCreateForm.tsx # Inline lease creation
│   │   └── ui/                           # shadcn/ui components (existing + new)
│   ├── hooks/
│   │   ├── useOrders.ts                  # Existing, may add useOrderDetails
│   │   ├── useReports.ts                 # Existing, already supports order_id filter
│   │   └── useLeases.ts                  # Existing, may add search param support
│   └── lib/
│       └── api/
│           ├── orders.ts                 # May add getOrder(id) function
│           ├── reports.ts                # Existing, verify getReports(orderId)
│           ├── leases.ts                 # May add searchLeases(term) function
│           └── types.ts                  # Extend with order details types
└── package.json                          # No new dependencies expected
```

**Structure Decision**: This is a web application using the existing backend/frontend split. The backend uses Django with entity-centric service organization (`orders` app contains Order, Report, and Lease services). The frontend uses Next.js App Router with TypeScript. Primary changes are in the frontend creating new components and a dynamic route. Backend changes are minimal - potentially adding query parameters to existing API endpoints.

## Complexity Tracking

> **No complexity justifications needed** - Feature adheres to all constitutional principles.

This feature:
- Uses existing Django app structure (no new apps)
- Follows DRY by creating reusable components
- Maintains SOLID principles with single-responsibility components
- Leverages existing authentication and API infrastructure
- No constitutional violations requiring justification
