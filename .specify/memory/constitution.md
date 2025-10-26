<!--
Sync Impact Report - 2025-10-26 Constitution Update
====================================================

VERSION CHANGE: 0.0.0 → 1.0.0 (Initial ratification)

RATIONALE: First formal constitution establishing Django + Next.js architectural principles 
with SOLID/DRY practices. MAJOR version because this sets foundational governance.

PRINCIPLES ESTABLISHED:
- I. Backend Architecture (Django, service layer, entity-centric)
- II. Frontend Architecture (Next.js App Router, TypeScript, shadcn/ui)
- III. SOLID Principles (mandatory for all code)
- IV. DRY Principle (no duplication, reusable abstractions)
- V. API-First Design (REST, HTTP-only cookies, clear contracts)

SECTIONS ADDED:
- Security & Authentication (HTTP-only cookies, JWT, CORS)
- Development Workflow (Docker-first, hot reload, testing)

TEMPLATE CONSISTENCY:
✅ plan-template.md - Constitution Check section references this file
✅ spec-template.md - Requirements align with API-first and security principles
✅ tasks-template.md - Task categorization supports backend/frontend separation
⚠️  No command-specific references found requiring updates

FOLLOW-UP TODOS:
- None - all placeholders filled

-->

# AA Order Manager Constitution

## Core Principles

### I. Backend Architecture (Django)

**Mandatory Practices:**
- Django backend MUST follow entity-centric service organization (not workflow-centric)
- Services MUST be organized by domain entity: `orders/services/lease/`, `orders/services/report/`, `orders/services/order/`
- MUST use Django REST Framework for all API endpoints
- MUST use Django models with proper relationships and migrations
- Background tasks MUST use Celery for async operations (Dropbox sync, discovery workflows)
- MUST maintain clear separation: Models → Services → Views/API → Serializers

**Rationale:** Entity-centric organization scales better as service complexity grows. The `orders` app manages tightly coupled entities (Order → Report → Lease) that share workflows. Splitting into separate apps would create artificial boundaries and complicate transaction management.

### II. Frontend Architecture (Next.js)

**Mandatory Practices:**
- MUST use Next.js 16+ with App Router (not Pages Router)
- MUST use TypeScript for all frontend code
- MUST use shadcn/ui component library via MCP tools (`mcp_shadcn-ui_*`)
- MUST prioritize shadcn blocks over individual components for common patterns
- MUST get component demos (`get_component_demo`) before implementation
- MUST use Tailwind CSS for styling with dark mode support via `next-themes`
- MUST use TanStack Query (React Query) for server state management
- MUST use React Context for client-side state (auth, theme)

**Rationale:** Modern React best practices with type safety. shadcn/ui provides accessible, customizable components. Blocks accelerate development for complex UI patterns. App Router enables better performance and developer experience.

### III. SOLID Principles (NON-NEGOTIABLE)

**Mandatory Practices:**
- **Single Responsibility**: Each class/module MUST have one reason to change
- **Open/Closed**: Entities MUST be open for extension, closed for modification
- **Liskov Substitution**: Subtypes MUST be substitutable for their base types
- **Interface Segregation**: No client MUST depend on methods it doesn't use
- **Dependency Inversion**: Depend on abstractions, not concretions

**Application:**
- Django: Use repositories for data access, services for business logic, serializers for API contracts
- Next.js: Use hooks for logic, components for presentation, separate API clients
- MUST justify any violation in code review with clear alternative analysis

**Rationale:** SOLID principles ensure maintainability, testability, and scalability. They prevent tight coupling and enable independent evolution of components.

### IV. DRY Principle (Don't Repeat Yourself)

**Mandatory Practices:**
- NO duplicate code - MUST extract to shared utilities, services, or components
- MUST use Django mixins, abstract models, and base classes for shared behavior
- MUST use React custom hooks for shared frontend logic
- MUST use TypeScript interfaces/types for shared data structures
- Configuration MUST be centralized (Django settings, .env files)
- MUST prefer composition over inheritance when extracting commonality

**Exceptions:**
- Test code MAY have some duplication for clarity
- Configuration files across environments (dev/prod) MAY duplicate structure

**Rationale:** DRY reduces maintenance burden, ensures consistency, and makes changes propagate correctly. Every piece of knowledge should have a single, authoritative representation.

### V. API-First Design

**Mandatory Practices:**
- Backend MUST expose REST API via Django REST Framework
- API endpoints MUST use proper HTTP methods (GET, POST, PUT/PATCH, DELETE)
- API responses MUST use consistent JSON structure
- Authentication MUST use JWT tokens via `djangorestframework-simplejwt`
- Tokens MUST be stored in HTTP-only cookies (not localStorage)
- Frontend MUST communicate with backend ONLY through API endpoints
- API contracts MUST be documented in `contracts/` directory for new features

**URL Structure:**
- API endpoints: `/api/[resource]/` (e.g., `/api/auth/login/`, `/api/orders/`)
- Django admin: `/admin/`
- Integration callbacks: `/integrations/[provider]/[action]/`

**Rationale:** Clear API contracts enable independent frontend/backend development. HTTP-only cookies prevent XSS attacks on tokens. RESTful design provides predictable, discoverable interfaces.

## Security & Authentication

**Mandatory Practices:**
- MUST use JWT tokens for authentication with 15-minute access tokens and 7-day refresh tokens
- MUST set tokens as HTTP-only cookies with `SameSite=Lax` and `Secure` flag in production
- MUST use CORS with `credentials: 'include'` and explicit allowed origins (no wildcards)
- MUST blacklist refresh tokens on logout
- Frontend middleware MUST protect authenticated routes by checking for `access_token` cookie
- MUST validate user permissions in backend (never trust frontend checks)
- Sensitive operations (Dropbox sync, directory creation) MUST run via Celery tasks
- MUST use Django's built-in CSRF protection for any form submissions

**Rationale:** HTTP-only cookies prevent XSS token theft. Short-lived access tokens limit damage from compromise. CORS restrictions prevent unauthorized origins from accessing the API. Backend validation ensures security regardless of frontend tampering.

## Development Workflow

**Mandatory Practices:**
- MUST use Docker Compose for development environment (PostgreSQL, Redis, Celery, frontend, backend)
- MUST use hot reload for both frontend (`npm run dev`) and backend (`runserver`)
- MUST follow PEP 8 for Python code (enforced by linters)
- MUST NOT create imports outside of top-level in Python
- MUST use `python3` command explicitly on Linux
- MUST prefer fewer lines of code when functionality is equivalent
- MUST NOT add methods for future use - only write code that is needed now
- MUST run linters before committing (`eslint` for frontend, Python linters for backend)

**Branch Strategy:**
- Main branch: `django/main`
- Feature branches: `[###-feature-name]` (e.g., `001-auth-flow`)

**Testing:**
- Tests are OPTIONAL unless explicitly requested in specifications
- When tests are required, follow TDD: Write tests → Verify failure → Implement → Verify pass
- Backend tests: `python3 web/manage.py test`
- Frontend builds: `npm run build` in frontend directory

**Rationale:** Docker ensures consistency across development environments. Hot reload accelerates feedback loops. Code quality standards prevent technical debt. Minimal code reduces maintenance burden.

## Technology Stack

**Backend:**
- Django 5.2+ with PostgreSQL database
- Django REST Framework for API
- djangorestframework-simplejwt for JWT authentication
- django-cors-headers for CORS
- Celery with Redis broker for background tasks
- Dropbox SDK for integration

**Frontend:**
- Next.js 16+ (App Router) with React 19+
- TypeScript 5+
- shadcn/ui component library (installed via MCP tools)
- Tailwind CSS 4+ for styling
- TanStack Query (React Query) for data fetching
- next-themes for dark mode
- Axios for HTTP requests

**Development:**
- Docker & Docker Compose for containerization
- Node 20 Alpine for frontend container
- Python 3.11+ for backend
- Redis for Celery broker and caching
- Flower for Celery monitoring

## Governance

**Amendment Procedure:**
1. Proposed changes MUST be documented with rationale
2. Changes MUST be reviewed against existing codebase for compatibility
3. Breaking changes MUST include migration plan
4. Constitution version MUST be incremented using semantic versioning:
   - MAJOR: Backward incompatible principle removals or redefinitions
   - MINOR: New principle or section added
   - PATCH: Clarifications, wording fixes, non-semantic refinements

**Compliance:**
- All code reviews MUST verify compliance with this constitution
- Deviations MUST be explicitly justified with alternative analysis
- Feature specifications MUST reference constitutional principles
- Implementation plans MUST include "Constitution Check" section

**Enforcement:**
- Pull requests failing constitution checks MUST be revised before merge
- Unjustified complexity MUST be simplified or removed
- Regular audits SHOULD identify constitutional violations in existing code

**Runtime Guidance:**
- Development practices: See README.md and DOCKER_DEV_README.md
- Speckit workflows: See `.specify/templates/commands/*.md`
- shadcn/ui usage: See `.cursor/rules/shad-cn.mdc`

**Version**: 1.0.0 | **Ratified**: 2025-10-26 | **Last Amended**: 2025-10-26
