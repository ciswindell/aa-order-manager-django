# Research: Next.js Frontend Migration

**Feature**: Next.js Frontend Migration  
**Branch**: `001-nextjs-frontend-migration`  
**Date**: 2025-10-26  
**Purpose**: Resolve technical unknowns and document best practices for Django + Next.js architecture

## Executive Summary

All technical decisions have been made based on existing project context, constitution requirements, and industry best practices. No critical unknowns remain. This document consolidates research findings on Django REST Framework patterns, Next.js App Router architecture, JWT authentication security, and shadcn/ui implementation.

## Research Areas

### 1. Django REST Framework API Design

**Decision**: Use Django REST Framework with ViewSets and Serializers

**Rationale**:
- Constitution mandates DRF for all API endpoints
- ViewSets provide CRUD operations with minimal boilerplate
- Serializers ensure data validation and type safety
- Existing Django models can be reused with minimal changes
- DRF integrates seamlessly with djangorestframework-simplejwt for JWT authentication

**Alternatives Considered**:
- **Plain Django views with JSON responses**: Rejected because requires manual implementation of pagination, filtering, permissions, and serialization. DRF provides these out-of-the-box.
- **GraphQL with Graphene-Django**: Rejected because adds complexity without clear benefit for this use case. REST API is sufficient for CRUD operations and integrations.
- **Django Ninja (FastAPI-style)**: Rejected because DRF is more mature, better documented, and aligns with constitution's explicit requirement.

**Best Practices**:
- Organize serializers by entity (auth.py, orders.py, reports.py, leases.py, integrations.py)
- Use ModelSerializer for entities to reduce duplication
- Implement custom serializers for complex responses (dashboard aggregations)
- Use SerializerMethodField for computed fields (integration status, lease counts)
- Validate input data in serializers, not views
- Use pagination classes for list endpoints (PageNumberPagination with page_size=20)

**References**:
- DRF Official Docs: https://www.django-rest-framework.org/
- DRF ViewSets: https://www.django-rest-framework.org/api-guide/viewsets/
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/

### 2. JWT Authentication with HTTP-Only Cookies

**Decision**: Use djangorestframework-simplejwt with HTTP-only cookies

**Rationale**:
- Constitution mandates HTTP-only cookies to prevent XSS attacks
- simplejwt provides token generation, refresh, and blacklisting
- HTTP-only cookies cannot be accessed by JavaScript (prevents token theft via XSS)
- SameSite=Lax prevents CSRF attacks
- Access token (15min) + Refresh token (7 days) balances security and UX

**Alternatives Considered**:
- **localStorage for tokens**: Rejected due to XSS vulnerability. Constitution explicitly prohibits this approach.
- **Session-based auth**: Rejected because doesn't scale well for API-first architecture and requires Django session middleware overhead.
- **OAuth2 only**: Rejected because adds unnecessary complexity for internal application. OAuth2 used only for external integrations (Dropbox).

**Best Practices**:
- Set access_token and refresh_token as HTTP-only cookies in custom login view
- Include credentials ('include') in frontend fetch requests
- Configure CORS with CORS_ALLOW_CREDENTIALS=True and explicit origins (no wildcards)
- Implement automatic token refresh in frontend (axios/fetch interceptor)
- Blacklist refresh tokens on logout
- Use secure flag in production (settings.DEBUG=False)
- Set appropriate max_age (15min for access, 7 days for refresh)

**Security Considerations**:
- No password complexity requirements per clarifications (user discretion)
- No rate limiting per clarifications (simplified MVP)
- Backend validation always required (never trust frontend)
- CORS configured with explicit origins (localhost:3000 dev, production domain)

**References**:
- simplejwt docs: https://django-rest-framework-simplejwt.readthedocs.io/
- OWASP JWT Best Practices: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- MDN HTTP Cookies: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies

### 3. Next.js 16 App Router Architecture

**Decision**: Use Next.js 16 with App Router, TypeScript, and src/ directory structure

**Rationale**:
- Constitution mandates Next.js 16+ with App Router (not Pages Router)
- App Router provides better performance, nested layouts, and server components
- TypeScript ensures type safety across frontend codebase
- src/ directory keeps app code separate from config files
- Flat route structure (no route groups initially) simplifies navigation

**Alternatives Considered**:
- **Next.js Pages Router**: Rejected because constitution explicitly requires App Router.
- **Create React App**: Rejected because no SSR/SSG capabilities and CRA is deprecated.
- **Vite + React**: Rejected because Next.js provides better production optimizations and routing.
- **Route groups for auth**: Deferred to keep structure simple. Protected routes handled by middleware.

**Best Practices**:
- Use middleware.ts for route protection (check access_token cookie)
- Implement loading.tsx and error.tsx for better UX
- Use React Server Components by default, Client Components only when needed ('use client')
- Organize by feature (components/auth/, components/dashboard/, etc.)
- Use layout.tsx for shared UI (nav, providers)
- Implement AuthProvider and ThemeProvider in root layout
- Use next-themes for dark mode with system preference support

**Performance Optimizations**:
- Use TanStack Query for caching and automatic refetching
- Implement optimistic updates for mutations
- Use React.memo for expensive components
- Lazy load components with next/dynamic for code splitting
- Use next/image for optimized images (if needed)

**References**:
- Next.js App Router Docs: https://nextjs.org/docs/app
- Next.js Middleware: https://nextjs.org/docs/app/building-your-application/routing/middleware
- TanStack Query: https://tanstack.com/query/latest

### 4. shadcn/ui Component Integration

**Decision**: Use shadcn/ui via MCP tools with incremental component installation

**Rationale**:
- Constitution mandates shadcn/ui installed via MCP tools
- Prioritize blocks over individual components for complex patterns
- Components are customizable (not npm package, copied into project)
- Built on Radix UI (accessible, unstyled primitives)
- Tailwind CSS integration with dark mode support
- Get component demos before implementation

**Alternatives Considered**:
- **Material-UI**: Rejected because heavy bundle size and opinionated styling.
- **Ant Design**: Rejected because less customizable and larger bundle.
- **Chakra UI**: Rejected because constitution explicitly requires shadcn/ui.
- **Build from scratch**: Rejected because reinventing accessibility is error-prone.

**Best Practices**:
- Install components incrementally (only when needed per page/feature)
- Use MCP tools: `mcp_shadcn-ui_list_components`, `mcp_shadcn-ui_get_component`, `mcp_shadcn-ui_get_component_demo`
- Prioritize blocks (`get_block`) for login pages, dashboards, tables
- Always call `get_component_demo` before using a component
- Customize components in components/ui/ as needed
- Use cn() utility for conditional class names
- Implement dark mode with class strategy (Tailwind)
- Configure next-themes provider in root layout

**Component Installation Plan**:
- **Phase 1 (Auth - P1)**: button, input, label, form, card, sonner (toast)
- **Phase 2 (Dashboard - P1)**: dropdown-menu (theme toggle)
- **Phase 3 (Integrations - P2)**: alert, badge
- **Phase 4 (Data Management - P3)**: table, dialog, additional form components

**References**:
- shadcn/ui Docs: https://ui.shadcn.com/docs
- Radix UI: https://www.radix-ui.com/
- next-themes: https://github.com/pacocoursey/next-themes

### 5. State Management Strategy

**Decision**: TanStack Query for server state, React Context for client state

**Rationale**:
- Constitution mandates TanStack Query for server state (API data)
- React Context sufficient for client state (auth, theme)
- No need for Redux/Zustand complexity
- TanStack Query provides caching, background refetching, optimistic updates
- Separates server and client state concerns (SOLID principle)

**Alternatives Considered**:
- **Redux Toolkit**: Rejected because overkill for this application. TanStack Query handles server state better.
- **Zustand**: Rejected because React Context is sufficient for simple client state.
- **Recoil**: Rejected because less mature and more complex than needed.
- **SWR**: Rejected because TanStack Query has better TypeScript support and more features.

**Best Practices**:
- Create custom hooks for each entity (useOrders, useReports, useLeases)
- Use QueryClient in layout.tsx
- Implement query keys consistently (`['orders', id]`, `['reports', { orderId }]`)
- Use useMutation for create/update/delete operations
- Implement onSuccess, onError callbacks for mutations
- Invalidate queries after successful mutations
- Use useAuth hook for auth context (user, login, logout)
- Use useTheme hook from next-themes for theme state

**References**:
- TanStack Query Docs: https://tanstack.com/query/latest/docs/framework/react/overview
- React Context: https://react.dev/reference/react/useContext

### 6. Database Schema Changes (Audit Logging)

**Decision**: Add audit fields to Order, Report, Lease models

**Rationale**:
- Clarification specifies basic audit logging (created_at, updated_at, created_by, updated_by)
- Django provides auto_now_add and auto_now for timestamps
- ForeignKey to User model for created_by/updated_by
- Tracks who made changes and when
- Enables future audit trail features if needed

**Implementation**:
- Add to Order model: created_at (DateTimeField auto_now_add), updated_at (DateTimeField auto_now), created_by (ForeignKey User), updated_by (ForeignKey User)
- Add to Report model: Same fields
- Add to Lease model: Same fields
- Create Django migration: `python manage.py makemigrations orders`
- Populate existing records with system user or first superuser
- Update API views to automatically set created_by/updated_by from request.user

**Migration Strategy**:
- Create migration with default values for existing records
- Set null=True, blank=True for audit fields to avoid breaking existing code
- Gradually enforce in forms/API over time

**References**:
- Django Models: https://docs.djangoproject.com/en/5.2/topics/db/models/
- Django Migrations: https://docs.djangoproject.com/en/5.2/topics/migrations/

### 7. Docker Configuration Updates

**Decision**: Add frontend service to docker-compose.yml with hot reload

**Rationale**:
- Consistent development environment across team
- Frontend needs access to backend API (http://web:8000 internally)
- Hot reload accelerates development
- Volume mount preserves node_modules

**Best Practices**:
- Use Node 20 Alpine base image for smaller size
- Mount ./frontend:/app for hot reload
- Set NEXT_PUBLIC_API_URL environment variable
- Expose port 3000 for local access
- Depend on web service (backend must be up first)
- Use .dockerignore to exclude node_modules, .next from build context

**docker-compose.yml Changes**:
```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules  # Anonymous volume for node_modules
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api
    depends_on:
      - web
```

**References**:
- Docker Compose: https://docs.docker.com/compose/
- Next.js Docker: https://nextjs.org/docs/deployment#docker-image

### 8. Toast Notification Behavior

**Decision**: Success toasts auto-dismiss after 5 seconds, error toasts require manual dismiss

**Rationale**:
- Clarification specifies this behavior for better UX
- Success messages are informational (don't need prolonged attention)
- Error messages may require user action (should stay visible)
- Follows common notification patterns (GitHub, Gmail, etc.)

**Implementation**:
- Use sonner library (shadcn/ui recommendation)
- Configure default duration: 5000ms for success
- Configure duration: Infinity for error toasts
- Make all toasts dismissible (X button)
- Position: bottom-right for desktop

**References**:
- Sonner: https://sonner.emilkowal.ski/
- shadcn/ui Toast: https://ui.shadcn.com/docs/components/toast

## Unresolved Questions

**None**: All technical decisions have been made. Implementation can proceed directly to Phase 1 (Design & Contracts).

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| HTTP-only cookie CORS issues | Low | Medium | CORS configured correctly, tested in existing implementation |
| Next.js SSR hydration mismatches with auth | Low | Medium | Use middleware for protection, check auth client-side only in effects |
| shadcn/ui component compatibility | Very Low | Low | Components already tested in existing implementation |
| Performance with 50 concurrent users | Very Low | Low | Standard Django/Next.js setup handles this easily, no special optimization needed |
| JWT token refresh race conditions | Low | Medium | Implement token refresh mutex in frontend interceptor |
| Dark mode flash on page load | Low | Low | Use next-themes with suppressHydrationWarning |

## Next Steps

1. **Phase 1**: Generate data-model.md (entity schemas with audit fields)
2. **Phase 1**: Generate API contracts (OpenAPI specs for all endpoints)
3. **Phase 1**: Generate quickstart.md (developer setup guide)
4. **Phase 1**: Update agent context file with new technologies
5. **Phase 2**: Generate tasks.md (implementation task breakdown by user story)

