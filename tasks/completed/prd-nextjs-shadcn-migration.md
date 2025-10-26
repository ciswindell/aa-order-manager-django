# PRD: Next.js + shadcn/ui Frontend Migration

## Introduction/Overview

Migrate the AA Order Manager from Django template-based frontend with Bootstrap to a modern React frontend using Next.js 14 (App Router) and shadcn/ui components. The Django backend will be converted to a REST API using Django REST Framework, with JWT authentication for secure communication between frontend and backend.

**Problem it solves:** Enables modern React-based UI with shadcn/ui components, better separation of concerns, improved developer experience, and sets foundation for future scalability.

**Goal:** Create a production-ready Next.js frontend with shadcn/ui that communicates with Django REST API backend, maintaining all existing functionality while improving UI/UX.

## Goals

1. Create Next.js 14 application (App Router) with TypeScript
2. Implement shadcn/ui component library with default theme and dark mode
3. Convert Django backend to REST API using Django REST Framework
4. Implement JWT authentication (access + refresh tokens)
5. Migrate all existing pages: Dashboard, Login, Integration Management
6. Support Order, Report, and Lease management interfaces
7. Update Docker Compose with separate frontend and backend containers
8. Maintain feature parity with existing Django template application
9. Implement client-side dark mode with localStorage persistence
10. Use modern data fetching patterns (React Query/TanStack Query)

## User Stories

1. As a user, I want to log in with my credentials and receive a secure JWT token for API access.
2. As a user, I want a modern, responsive interface built with shadcn/ui components.
3. As a user, I want dark mode that persists across sessions using localStorage.
4. As a developer, I want a clear separation between frontend and backend for easier maintenance.
5. As a developer, I want TypeScript for type safety across the entire frontend.
6. As a staff user, I want to manage integrations (Dropbox) through the new interface.
7. As a user, I want to view and manage orders, reports, and leases through the React interface.
8. As a developer, I want automatic API request retries and caching via React Query.

## Functional Requirements

### Next.js Frontend Setup

1. The system must create a Next.js 14 application using App Router architecture.
2. The system must use TypeScript for all frontend code.
3. The system must use Tailwind CSS for styling (shadcn/ui dependency).
4. The system must initialize shadcn/ui with default configuration.
5. The frontend must run on port 3000 in development.
6. The frontend must be containerized in Docker with hot-reload support.

### shadcn/ui Components

7. The system must initialize shadcn/ui configuration during setup.
8. The system must install shadcn/ui components incrementally as needed per page:
   - **Phase 1 (Auth):** button, input, label, form
   - **Phase 2 (Layout):** navigation-menu, dropdown-menu, switch (dark mode)
   - **Phase 3 (Dashboard/Integrations):** card, alert, badge, toast
   - **Phase 4 (Data Management):** table, additional form components as needed
9. Components must only be added when actively used in implementation.
10. The system must use default shadcn/ui theme colors.
11. All components must support dark mode via Tailwind's dark mode class strategy.

### Dark Mode

12. The system must implement dark mode toggle using shadcn/ui switch component.
13. Dark mode preference must persist in localStorage (client-side only).
14. The system must load dark mode preference immediately to prevent flash.
15. Dark mode must apply to all shadcn/ui components automatically.

### Authentication System

16. The system must implement JWT authentication with access and refresh tokens.
15. Django backend must use djangorestframework-simplejwt for token generation.
16. Access tokens must expire after 15 minutes.
17. Refresh tokens must expire after 7 days.
18. The frontend must automatically refresh access tokens when expired.
19. The frontend must redirect to login page when refresh token expires.
20. The system must store tokens securely (httpOnly cookies preferred, or localStorage with XSS protection).
21. Login form must validate credentials and receive JWT tokens.
22. Logout must clear tokens and redirect to login page.

### Django REST API

31. The system must install Django REST Framework (DRF).
24. The system must create API endpoints for:
    - Authentication (login, logout, token refresh)
    - User profile (current user details)
    - Dashboard data
    - Integration status (Dropbox, Basecamp)
    - Integration actions (connect, disconnect)
    - Orders (CRUD operations)
    - Reports (CRUD operations)
    - Leases (CRUD operations)
25. All API endpoints must require authentication (except login).
26. API responses must use consistent JSON structure.
27. API must handle CORS to allow Next.js frontend access.
28. API must use proper HTTP status codes (200, 201, 400, 401, 403, 404, 500).
29. API must include pagination for list endpoints.
30. API must validate all input data with DRF serializers.

### Data Fetching & State Management

39. The frontend must use TanStack Query (React Query) for server state management.
32. The system must implement query caching with appropriate stale times.
33. The system must implement automatic refetching on window focus.
34. The system must implement optimistic updates for mutations.
35. The system must display loading states during API calls.
36. The system must display error states with user-friendly messages.
37. The system must implement retry logic for failed requests.

### Page Migrations

46. **Login Page** must include:
    - Email/username and password inputs
    - Submit button
    - Error message display
    - Redirect to dashboard after successful login

47. **Dashboard Page** must include:
    - Welcome message with username
    - Admin action buttons (if staff)
    - Integration status cards
    - Integration CTAs when action required

48. **Integration Management Page** must include:
    - Dropbox integration card with connection status
    - Connect/disconnect buttons
    - Status badges (connected, authenticated)
    - Basecamp placeholder card

49. **Orders Page** must include:
    - Order list table with sorting/filtering
    - Create new order button
    - Order details view
    - Edit/delete actions

50. **Reports Page** must include:
    - Report list associated with orders
    - Report type indicators
    - Create/edit report forms
    - Link to associated leases

51. **Leases Page** must include:
    - Lease list with agency and number
    - Runsheet links and status
    - Document archive links
    - Edit lease details

### Navigation & Layout

52. The system must implement a consistent layout with:
    - Top navigation bar with shadcn navigation-menu
    - User dropdown menu (profile, logout)
    - Dark mode toggle in navigation
    - Responsive design for desktop (mobile out of scope per PRD)

53. Navigation must show/hide items based on user permissions (is_staff).
54. Navigation must highlight active page.

### Error Handling & Notifications

55. The system must use shadcn/ui toast component for notifications.
56. Success messages must display as green toasts.
57. Error messages must display as red toasts.
58. Warning messages must display as yellow toasts.
59. The system must handle network errors gracefully.
60. The system must handle 401 errors by triggering token refresh or logout.
61. The system must handle 403 errors with permission denied message.

### Docker Configuration

62. The system must create a Dockerfile for Next.js application.
63. The docker-compose.yml must add a `frontend` service:
    - Build from Next.js Dockerfile
    - Mount source code for hot reload
    - Expose port 3000
    - Environment variables for API URL
64. The `web` service must be renamed to `backend` for clarity.
65. Backend must expose API on port 8000.
66. Backend must configure CORS to allow requests from frontend:3000.
67. All services must start with single `docker compose up` command.

## Non-Goals (Out of Scope)

1. Server-side rendering (SSR) optimization - use client-side only for now
2. Mobile responsiveness - desktop-focused as per original PRD
3. Progressive Web App (PWA) features
4. Advanced state management (Redux, Zustand) - React Query sufficient
5. End-to-end testing - defer to future work
6. Internationalization (i18n)
7. Analytics integration
8. WebSocket real-time updates
9. Advanced caching strategies (Service Workers)
10. Migration of legacy Django admin interface - keep existing
11. Custom shadcn/ui theme - use defaults
12. Image optimization and lazy loading
13. Code splitting optimization beyond Next.js defaults

## Design Considerations

### Architecture

- **Frontend:** Next.js 14 (App Router) + React 18 + TypeScript
- **UI Library:** shadcn/ui + Tailwind CSS
- **Backend:** Django 5.2 + Django REST Framework
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Data Fetching:** TanStack Query v5
- **HTTP Client:** Axios with interceptors for token handling

### Directory Structure

```
/
├── web/                          # Django backend
│   ├── manage.py
│   ├── order_manager_project/
│   │   └── settings.py
│   ├── api/                      # New: REST API app
│   │   ├── views/
│   │   ├── serializers/
│   │   └── urls.py
│   ├── orders/                   # Existing apps
│   ├── integrations/
│   └── core/
├── frontend/                     # New: Next.js app
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   └── login/
│   │   │   ├── (dashboard)/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── orders/
│   │   │   │   ├── reports/
│   │   │   │   ├── leases/
│   │   │   │   └── integrations/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── ui/              # shadcn components
│   │   │   ├── layout/          # Nav, Layout
│   │   │   └── features/        # Domain components
│   │   ├── lib/
│   │   │   ├── api/             # API client & endpoints
│   │   │   ├── auth/            # Auth utilities
│   │   │   └── utils.ts
│   │   └── hooks/               # Custom React hooks
│   ├── public/
│   ├── components.json          # shadcn config
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .env
```

### API Endpoint Design

```
POST   /api/auth/login/              # Login (username, password) → tokens
POST   /api/auth/refresh/            # Refresh token → new access token
POST   /api/auth/logout/             # Logout
GET    /api/auth/user/               # Current user details

GET    /api/dashboard/               # Dashboard data

GET    /api/integrations/status/    # All integration statuses
POST   /api/integrations/dropbox/connect/
POST   /api/integrations/dropbox/disconnect/

GET    /api/orders/                  # List orders (paginated)
POST   /api/orders/                  # Create order
GET    /api/orders/:id/              # Get order details
PATCH  /api/orders/:id/              # Update order
DELETE /api/orders/:id/              # Delete order

GET    /api/reports/                 # List reports (with filters)
POST   /api/reports/                 # Create report
GET    /api/reports/:id/             # Get report details
PATCH  /api/reports/:id/             # Update report
DELETE /api/reports/:id/             # Delete report

GET    /api/leases/                  # List leases (paginated)
POST   /api/leases/                  # Create lease
GET    /api/leases/:id/              # Get lease details
PATCH  /api/leases/:id/              # Update lease
DELETE /api/leases/:id/              # Delete lease
```

### Type Safety

- All API responses must have corresponding TypeScript interfaces
- Use Zod for runtime validation of API responses
- Generate types from Django models where possible

### Token Management Strategy

1. Store access token in memory (React state/context)
2. Store refresh token in httpOnly cookie (set by Django)
3. Axios interceptor automatically adds access token to requests
4. Axios interceptor detects 401, attempts refresh, retries original request
5. If refresh fails, redirect to login and clear tokens

## Technical Considerations

### Django Backend Changes

- Install: `djangorestframework`, `djangorestframework-simplejwt`, `django-cors-headers`
- Create new `api` Django app for REST endpoints
- Convert existing models to DRF serializers
- Implement viewsets for CRUD operations
- Configure CORS to allow frontend origin
- Configure JWT settings (token lifetimes)
- Update settings for REST framework defaults

### Next.js Frontend Setup

- Create with: `npx create-next-app@latest frontend --typescript --tailwind --app`
- Install: `@tanstack/react-query`, `axios`, `date-fns`, `zod`
- Initialize shadcn/ui: `npx shadcn-ui@latest init`
- **Install components incrementally** - only add components when needed for current implementation phase
- Configure environment variables for API URL

### Docker Considerations

- Frontend container: Node 20 Alpine
- Backend container: Python 3.11 (existing)
- Frontend hot reload: mount `./frontend` volume
- Backend hot reload: mount `./web` volume (existing)
- Network: all containers on same Docker network
- Environment variables passed via docker-compose

### Migration Strategy

1. Keep existing Django templates functional during migration
2. Build API endpoints incrementally
3. Build Next.js pages incrementally
4. Test each page thoroughly before moving to next
5. Once complete, remove Django template code
6. Remove Bootstrap CSS and old static files

## Success Metrics

1. **Feature Parity:** All existing functionality works in Next.js frontend
2. **Performance:** Pages load in < 2 seconds
3. **Type Safety:** 100% TypeScript coverage in frontend
4. **API Coverage:** All required endpoints implemented and documented
5. **Authentication:** Secure JWT flow with token refresh working
6. **Dark Mode:** Theme persists across sessions without flash
7. **Developer Experience:** `docker compose up` starts entire stack
8. **Error Handling:** All errors display user-friendly messages via toasts

## Open Questions

1. Should we implement API versioning (e.g., `/api/v1/`)? **Recommendation:** Yes, plan for future versions
2. Should we keep Django admin interface or build React admin pages? **Recommendation:** Keep Django admin for now
3. How should file uploads work (Celery task results, etc.)? **Recommendation:** Defer to implementation, likely multipart/form-data
4. Should we add API rate limiting? **Recommendation:** Yes, use DRF throttling
5. Should we implement WebSocket for real-time Celery task updates? **Recommendation:** Out of scope, defer to future

## Implementation Notes

### Phase 1: Backend API (Foundation)
- Set up DRF
- Implement authentication endpoints
- Create user and dashboard endpoints
- Configure CORS

### Phase 2: Frontend Scaffold
- Create Next.js app
- Set up shadcn/ui
- Implement authentication flow
- Create layout and navigation

### Phase 3: Core Pages
- Dashboard
- Integration management

### Phase 4: Data Management
- Orders CRUD
- Reports CRUD  
- Leases CRUD

### Phase 5: Polish & Testing
- Error handling
- Loading states
- Toast notifications
- Dark mode refinement
- Docker optimization

