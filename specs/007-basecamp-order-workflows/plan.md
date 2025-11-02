# Implementation Plan: Basecamp Order Workflows

**Branch**: `007-basecamp-order-workflows` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/007-basecamp-order-workflows/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Automate creation of Basecamp task workflows from order data using hardcoded templates. System supports 4 product types (Federal/State × Runsheets/Abstracts) across 2 distinct workflow patterns: Pattern A (lease-centric, flat structure for runsheets) and Pattern B (report-centric, grouped by department for abstracts). Technical approach uses Strategy Pattern with separate workflow strategies for each pattern type, delegating to appropriate strategy based on report type and agency filtering.

## Technical Context

**Language/Version**: Python 3.11+, TypeScript 5+  
**Primary Dependencies**: Django 5.2+, Django REST Framework, Next.js 16+, existing BasecampService  
**Storage**: PostgreSQL (existing models: Order, Report, Lease, BasecampAccount)  
**Testing**: pytest for backend (optional per constitution), not required by spec  
**Target Platform**: Web application (Docker containerized)  
**Project Type**: Web - Django backend + Next.js frontend  
**Performance Goals**: Workflow creation completes within 30 seconds for orders with up to 10 reports (SC-002)  
**Constraints**: <30s workflow creation, 95% success rate (SC-003), exponential backoff retry for API failures  
**Scale/Scope**: Up to 10 reports per order, 4 Basecamp project configurations, handles multi-product orders

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md`:

### Initial Check (Pre-Research) ✅ PASSED

**Backend (Django):**
- [x] Services organized by entity (orders/services/workflow/ NEW service layer for workflow execution)
- [x] Using Django REST Framework for all API endpoints (new workflow trigger endpoint)
- [x] Background tasks use Celery (NOT APPLICABLE - workflow creation is synchronous per spec)
- [x] Following SOLID principles (Strategy Pattern for workflow types, ProductConfig for DRY configuration)

**Frontend (Next.js):**
- [x] Using Next.js 16+ App Router (existing order details page modification)
- [x] TypeScript for all code
- [x] shadcn/ui components installed via MCP tools (Button component for "Push to Basecamp")
- [x] TanStack Query for server state, React Context for client state

**Security:**
- [x] JWT tokens in HTTP-only cookies (existing auth mechanism)
- [x] CORS configured with credentials and explicit origins (existing configuration)
- [x] Protected routes via middleware (order details page already protected)

**Code Quality:**
- [x] DRY: Strategy Pattern + ProductConfig prevents duplication across 4 product types
- [x] SOLID: WorkflowStrategy interface, concrete strategies for each pattern, single responsibility
- [x] Python: PEP 8, comprehensive logging with structured context
- [x] TypeScript: Strict types, proper error handling

**Complexity Justification Required If:**
- ✅ Adding new Django service layer: NEW `orders/services/workflow/` for workflow execution (justified - complex business logic for 2 patterns × 4 product types)
- ✅ Strategy Pattern: Prevents duplication, enables independent evolution of runsheet vs abstract workflows
- ✅ Configuration-driven: ProductConfig dataclass makes adding new products trivial without code changes

---

### Post-Design Check (After Phase 1) ✅ PASSED

**Design Artifacts Generated**:
- [x] research.md: 5 research questions resolved (Strategy Pattern, ProductConfig, workflow steps, success message, error handling)
- [x] data-model.md: Entities defined (ProductConfig, WorkflowResult, WorkflowStrategy implementations)
- [x] contracts/api-spec.md: API endpoint specification (POST /api/orders/{id}/workflows/)
- [x] quickstart.md: Implementation checklist (5 phases, 3-5 day estimate)

**Architecture Verification**:
- [x] **Entity-Centric**: Workflow service operates on Order entity, follows orders/services/ pattern
- [x] **SOLID Compliance**:
  - Single Responsibility: WorkflowExecutor (orchestration), Strategies (pattern-specific logic), ProductConfig (configuration)
  - Open/Closed: Can add new workflow patterns without modifying existing strategies
  - Liskov Substitution: All strategies implement WorkflowStrategy interface correctly
  - Interface Segregation: WorkflowStrategy has single `create_workflow()` method
  - Dependency Inversion: Executor depends on WorkflowStrategy abstraction, not concrete strategies
- [x] **DRY Compliance**: ProductConfig eliminates duplication across 4 product types, strategies share BasecampService primitives
- [x] **API-First**: REST endpoint with clear contract, JSON request/response, proper HTTP status codes
- [x] **Security**: JWT auth required, user authorization check, error messages don't expose internals
- [x] **No Future Methods**: All code serves immediate spec requirements (no speculative features)

**Technology Stack Alignment**:
- [x] Python 3.11+ with Django 5.2+ and DRF (backend)
- [x] TypeScript 5+ with Next.js 16+ App Router (frontend)
- [x] PostgreSQL for existing models (no new database changes)
- [x] Docker development environment
- [x] Existing BasecampService for API primitives (no reinvention)

**Final Verdict**: ✅ Design fully compliant with constitution, ready for implementation (/speckit.tasks)

## Project Structure

### Documentation (this feature)

```text
specs/007-basecamp-order-workflows/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api-spec.md      # Workflow trigger API endpoint
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Web application structure (Django backend + Next.js frontend)
web/
├── orders/
│   ├── models.py                    # Existing: Order, Report, Lease
│   ├── services/
│   │   ├── workflow/                # NEW: Workflow execution service
│   │   │   ├── __init__.py
│   │   │   ├── executor.py          # Main workflow executor (delegates to strategies)
│   │   │   ├── strategies/          # Workflow strategy implementations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py          # WorkflowStrategy abstract base class
│   │   │   │   ├── runsheet.py      # RunsheetWorkflowStrategy (Pattern A)
│   │   │   │   └── abstract.py      # AbstractWorkflowStrategy (Pattern B)
│   │   │   └── config.py            # ProductConfig dataclass, PRODUCT_CONFIGS dict
│   │   ├── lease/                   # Existing
│   │   ├── report/                  # Existing
│   │   └── order/                   # Existing
│   └── views/
│       └── workflows.py             # NEW: Workflow trigger API view
├── integrations/
│   └── basecamp/
│       └── basecamp_service.py      # Existing: API methods (list_projects, create_todolist, etc.)
└── order_manager_project/
    └── settings.py                  # Environment variables for Basecamp project IDs

web/api/
├── urls.py                          # NEW route: POST /api/orders/{id}/workflows/
└── serializers/
    └── workflows.py                 # NEW: WorkflowTriggerSerializer, WorkflowResultSerializer

frontend/
└── src/
    ├── app/
    │   └── dashboard/
    │       └── orders/
    │           └── [id]/
    │               └── page.tsx      # MODIFIED: Add "Push to Basecamp" button
    └── lib/
        └── api/
            ├── types.ts              # MODIFIED: Add WorkflowResult type
            └── workflows.ts          # NEW: API client for workflow trigger
```

**Structure Decision**: Web application structure selected. Backend implements Strategy Pattern in new `orders/services/workflow/` service layer following entity-centric organization (workflow operates on Order entity). Frontend adds button to existing order details page. Existing BasecampService provides API integration primitives.

## Complexity Tracking

> **Justifications for constitutional compliance**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New service layer (orders/services/workflow/) | Complex business logic for 2 workflow patterns across 4 product types requires dedicated orchestration layer | Putting logic in views would violate SRP and make testing difficult; existing services (lease/, report/, order/) operate on single entities, workflow crosses all three |
| Strategy Pattern for workflows | Each pattern (Runsheet vs Abstract) has fundamentally different structure: flat vs grouped, lease-per-task vs report-per-todolist, conditional step duplication | Single monolithic workflow function would have nested conditionals for 4 product types, violating OCP and making new products harder to add |
| ProductConfig dataclass | Encapsulates project_id, agency, report_types, strategy mapping for DRY | Hardcoding project IDs and logic in each strategy would duplicate configuration across 4 product types |
