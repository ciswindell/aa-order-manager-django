# Feature Specifications

This directory contains all feature specifications for the AA Order Manager Django/Next.js web application.

## Spec Structure

Each feature has its own directory following the naming convention `NNN-feature-name`:

```
specs/
├── 001-nextjs-frontend-migration/
├── 002-order-details-page/
├── 003-basecamp-integration/
├── 004-basecamp-project-api/
├── 005-basecamp-account-selection/
├── 006-integration-account-names/
├── 007-basecamp-order-workflows/
└── 008-separate-django-repo/  (pending merge)
```

## Speckit Workflow

We use the `.specify` framework (Speckit) for structured feature development. Each specification follows this workflow:

### Commands

1. **`/speckit.specify`** - Generate feature specification
   - Creates `spec.md` with user stories, requirements, success criteria
   - Creates `checklists/` for quality validation
   - Generates comprehensive feature documentation

2. **`/speckit.plan`** - Generate implementation plan
   - Creates `plan.md` with technical context and architecture
   - Creates `research.md` with technical decisions
   - Creates `data-model.md` for entities and relationships
   - Creates `contracts/` for API specifications
   - Creates `quickstart.md` for integration guide

3. **`/speckit.tasks`** - Generate task breakdown
   - Creates `tasks.md` with detailed, sequenced implementation tasks
   - Organizes tasks into phases with dependencies
   - Includes success criteria and checkpoints

4. **`/speckit.implement`** - Execute implementation
   - Executes tasks phase-by-phase
   - Validates against checklists and success criteria
   - Updates tasks.md with completion status

### Standard Files in Each Spec

- **`spec.md`** - Feature specification with user stories and requirements
- **`plan.md`** - Technical implementation plan
- **`tasks.md`** - Detailed task breakdown for implementation
- **`research.md`** - Technical research and decisions
- **`data-model.md`** - Data entities and relationships
- **`quickstart.md`** - Quick start guide and success criteria
- **`checklists/`** - Quality validation checklists
- **`contracts/`** - API specifications, scripts, procedures

## Feature Summaries

### 001 - Next.js Frontend Migration
Migrated from Django templates to Next.js 16 App Router with TypeScript, shadcn/ui, and TanStack Query.

### 002 - Order Details Page
Created comprehensive order management UI with reports, leases, and Basecamp workflow integration.

### 003 - Basecamp Integration
Implemented OAuth authentication and token management for Basecamp API.

### 004 - Basecamp Project API
Added project listing and caching functionality for Basecamp integration.

### 005 - Basecamp Account Selection
Implemented account selection UI with real-time authorization status and project counts.

### 006 - Integration Account Names
Enhanced integration management with account naming and improved UX.

### 007 - Basecamp Order Workflows
Automated creation of Basecamp to-do lists and tasks for orders with product-specific workflows.

### 008 - Separate Django Repository
Migrated Django/Next.js application to its own repository for independent development and deployment.

## Development Guidelines

### Creating a New Spec

1. Create a new branch: `git checkout -b NNN-feature-name`
2. Run `/speckit.specify` to generate the specification
3. Review and validate checklists in `checklists/`
4. Run `/speckit.plan` to generate implementation plan
5. Run `/speckit.tasks` to generate task breakdown
6. Run `/speckit.implement` to execute implementation
7. Create PR and merge when complete

### Spec Quality Standards

All specifications must pass quality checklists before implementation:
- Requirements are clear, testable, and complete
- User stories follow standard format
- Success criteria are measurable
- Edge cases are documented
- Dependencies and constraints are identified

## Constitution

All code must follow the project constitution (`.specify/memory/constitution.md`):
- **Backend**: Services organized by entity, Django REST Framework, Celery for background tasks
- **Frontend**: Next.js App Router, TypeScript, shadcn/ui components, TanStack Query
- **Security**: JWT in HTTP-only cookies, CORS with explicit origins, protected routes
- **Code Quality**: DRY, SOLID, PEP 8, no future methods, preserve comments

## Related Documentation

- **Project README**: [../README.md](../README.md)
- **Docker Setup**: [../DOCKER_DEV_README.md](../DOCKER_DEV_README.md)
- **Constitution**: [../.specify/memory/constitution.md](../.specify/memory/constitution.md)
- **Original Repository**: https://github.com/ciswindell/aa-order-manager (Tkinter app)

