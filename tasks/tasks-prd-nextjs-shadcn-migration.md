# Task List: Next.js + shadcn/ui Frontend Migration

## Relevant Files

### Backend (Django)
- `web/requirements.txt` - Add DRF, simplejwt, cors-headers
- `web/order_manager_project/settings.py` - Configure DRF, JWT, CORS settings
- `web/api/__init__.py` - New Django app for REST API
- `web/api/serializers/*.py` - DRF serializers for models
- `web/api/views/*.py` - API viewsets and endpoints
- `web/api/urls.py` - API URL routing
- `web/orders/models.py` - Existing models (reference for serializers)
- `web/integrations/models.py` - Existing models (reference for serializers)

### Frontend (Next.js)
- `frontend/package.json` - Next.js dependencies
- `frontend/src/app/layout.tsx` - Root layout with providers
- `frontend/src/app/(auth)/login/page.tsx` - Login page
- `frontend/src/app/(dashboard)/layout.tsx` - Authenticated layout with nav
- `frontend/src/app/(dashboard)/dashboard/page.tsx` - Dashboard page
- `frontend/src/app/(dashboard)/integrations/page.tsx` - Integration management
- `frontend/src/app/(dashboard)/orders/page.tsx` - Orders list
- `frontend/src/app/(dashboard)/reports/page.tsx` - Reports list
- `frontend/src/app/(dashboard)/leases/page.tsx` - Leases list
- `frontend/src/components/ui/*` - shadcn/ui components (installed incrementally)
- `frontend/src/components/layout/nav.tsx` - Navigation component
- `frontend/src/lib/api/client.ts` - Axios client with interceptors
- `frontend/src/lib/auth/auth-context.tsx` - Auth context provider
- `frontend/src/hooks/use-auth.ts` - Auth hook
- `frontend/components.json` - shadcn/ui configuration
- `frontend/tailwind.config.ts` - Tailwind configuration
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/.env.local` - Frontend environment variables
- `frontend/Dockerfile` - Next.js Docker container

### Docker
- `docker-compose.yml` - Updated with frontend service, backend renamed
- `Dockerfile` - Frontend container definition

### Notes

- Follow incremental component installation - only add shadcn components when needed
- Use MCP shadcn tool to install components: `mcp_shadcn_view_items_in_registries` and `mcp_shadcn_get_add_command_for_items`
- Test API endpoints with curl/Postman before building frontend
- Keep Django templates functional until full migration complete
- Run backend tests after API changes: `python3 web/manage.py test`
- TypeScript compilation: `npm run build` in frontend directory

## Tasks

- [ ] 1.0 Setup Django REST API Backend
  - [ ] 1.1 Install Django REST Framework packages: `djangorestframework`, `djangorestframework-simplejwt`, `django-cors-headers`
  - [ ] 1.2 Add packages to `web/requirements.txt`
  - [ ] 1.3 Add `rest_framework`, `rest_framework_simplejwt`, `corsheaders` to `INSTALLED_APPS` in settings.py
  - [ ] 1.4 Create new Django app: `python3 web/manage.py startapp api` in web directory
  - [ ] 1.5 Add `api` app to `INSTALLED_APPS`
  - [ ] 1.6 Configure REST_FRAMEWORK settings in settings.py (pagination, authentication classes)
  - [ ] 1.7 Configure CORS settings to allow localhost:3000 origin
  - [ ] 1.8 Add `corsheaders.middleware.CorsMiddleware` to MIDDLEWARE (before CommonMiddleware)
  - [ ] 1.9 Create `web/api/serializers/` directory and `__init__.py`
  - [ ] 1.10 Create `web/api/views/` directory and `__init__.py`
  - [ ] 1.11 Create `web/api/urls.py` file
  - [ ] 1.12 Include API urls in main `order_manager_project/urls.py` at path `api/`

- [ ] 2.0 Implement JWT Authentication
  - [ ] 2.1 Configure SIMPLE_JWT settings in settings.py (access token 15min, refresh token 7 days)
  - [ ] 2.2 Create `web/api/serializers/auth.py` with UserSerializer
  - [ ] 2.3 Create `web/api/views/auth.py` with login view (TokenObtainPairView extension)
  - [ ] 2.4 Create custom TokenObtainPairSerializer to include user data in response
  - [ ] 2.5 Add logout view (blacklist refresh token)
  - [ ] 2.6 Add user profile view (GET /api/auth/user/)
  - [ ] 2.7 Configure JWT auth URLs in `api/urls.py`: login, refresh, logout, user
  - [ ] 2.8 Test login endpoint returns access and refresh tokens
  - [ ] 2.9 Test refresh endpoint with valid refresh token
  - [ ] 2.10 Test protected endpoint requires valid access token

- [ ] 3.0 Create Next.js Frontend Application
  - [ ] 3.1 Create frontend directory: `npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir`
  - [ ] 3.2 Move into frontend directory and verify it runs: `cd frontend && npm run dev`
  - [ ] 3.3 Install dependencies: `npm install @tanstack/react-query axios zod date-fns`
  - [ ] 3.4 Initialize shadcn/ui: `npx shadcn-ui@latest init` (choose defaults, confirm TypeScript, Tailwind)
  - [ ] 3.5 Create `frontend/.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`
  - [ ] 3.6 Create `src/` directory and move `app/` into it
  - [ ] 3.7 Update `tsconfig.json` paths to reflect src directory
  - [ ] 3.8 Create directory structure: `lib/`, `components/`, `hooks/`
  - [ ] 3.9 Create `lib/api/`, `lib/auth/`, `lib/utils.ts`
  - [ ] 3.10 Test build: `npm run build` to ensure no errors

- [ ] 4.0 Setup Authentication Flow in Frontend
  - [ ] 4.1 Install shadcn components for auth: `npx shadcn-ui@latest add button input label form`
  - [ ] 4.2 Create `lib/api/client.ts` - Axios instance with baseURL from env
  - [ ] 4.3 Create TypeScript interfaces in `lib/api/types.ts` for User, LoginRequest, LoginResponse, etc.
  - [ ] 4.4 Create `lib/auth/auth-context.tsx` - AuthProvider with user state and login/logout functions
  - [ ] 4.5 Create `lib/auth/token-storage.ts` - functions to store/retrieve/clear tokens from localStorage
  - [ ] 4.6 Add Axios request interceptor to attach access token to requests
  - [ ] 4.7 Add Axios response interceptor to handle 401 errors and refresh token
  - [ ] 4.8 Create `hooks/use-auth.ts` - custom hook to access auth context
  - [ ] 4.9 Create login API function in `lib/api/auth.ts`
  - [ ] 4.10 Wrap root layout with AuthProvider and QueryClientProvider
  - [ ] 4.11 Create `(auth)` route group directory for unauthenticated pages
  - [ ] 4.12 Create `app/(auth)/login/page.tsx` with login form using shadcn form components
  - [ ] 4.13 Implement form validation with Zod schema
  - [ ] 4.14 Implement login submit handler that calls API and stores tokens
  - [ ] 4.15 Add redirect to dashboard after successful login
  - [ ] 4.16 Test login flow: enter credentials, submit, verify redirect and token storage

- [ ] 5.0 Build Layout and Navigation Components
  - [ ] 5.1 Install shadcn navigation components: `npx shadcn-ui@latest add navigation-menu dropdown-menu avatar`
  - [ ] 5.2 Install dark mode components: `npx shadcn-ui@latest add switch`
  - [ ] 5.3 Create `(dashboard)` route group directory for authenticated pages
  - [ ] 5.4 Create `app/(dashboard)/layout.tsx` with authentication check
  - [ ] 5.5 Add redirect to login if user not authenticated in dashboard layout
  - [ ] 5.6 Create `components/layout/nav.tsx` with shadcn navigation-menu
  - [ ] 5.7 Add navigation links: Dashboard, Orders, Reports, Leases, Integrations
  - [ ] 5.8 Add conditional rendering for staff-only links (Admin)
  - [ ] 5.9 Create user dropdown menu with username and logout button
  - [ ] 5.10 Create `components/theme/theme-provider.tsx` for dark mode using next-themes
  - [ ] 5.11 Create `components/theme/theme-toggle.tsx` with shadcn switch component
  - [ ] 5.12 Add theme toggle to navigation bar
  - [ ] 5.13 Implement logout functionality that clears tokens and redirects to login
  - [ ] 5.14 Add active link highlighting using usePathname
  - [ ] 5.15 Include navigation in dashboard layout
  - [ ] 5.16 Test navigation: click links, verify routing, test logout, test dark mode toggle

- [ ] 6.0 Implement Dashboard Page
  - [ ] 6.1 Install shadcn components: `npx shadcn-ui@latest add card badge alert`
  - [ ] 6.2 Create `app/(dashboard)/dashboard/page.tsx`
  - [ ] 6.3 Create API endpoint GET `/api/dashboard/` in Django (returns welcome data, integration statuses)
  - [ ] 6.4 Create serializer for dashboard data in `web/api/serializers/dashboard.py`
  - [ ] 6.5 Create view for dashboard in `web/api/views/dashboard.py`
  - [ ] 6.6 Create dashboard API function in `frontend/src/lib/api/dashboard.ts`
  - [ ] 6.7 Create React Query hook `useDashboard` in `hooks/use-dashboard.ts`
  - [ ] 6.8 Implement dashboard page layout with welcome message
  - [ ] 6.9 Display admin action buttons (Django Admin, Manage Integrations) if user is staff
  - [ ] 6.10 Create integration status card component using shadcn card
  - [ ] 6.11 Display integration statuses with badges (connected, disconnected)
  - [ ] 6.12 Show integration CTAs when action required using shadcn alert
  - [ ] 6.13 Add loading state skeleton while fetching data
  - [ ] 6.14 Add error state display if API fails
  - [ ] 6.15 Test dashboard: verify data loads, check staff vs non-staff view, test loading/error states

- [ ] 7.0 Implement Integration Management Pages
  - [ ] 7.1 Install toast component: `npx shadcn-ui@latest add toast`
  - [ ] 7.2 Create `app/(dashboard)/integrations/page.tsx`
  - [ ] 7.3 Create API endpoint GET `/api/integrations/status/` in Django
  - [ ] 7.4 Create API endpoint POST `/api/integrations/dropbox/connect/` (initiates OAuth)
  - [ ] 7.5 Create API endpoint POST `/api/integrations/dropbox/disconnect/`
  - [ ] 7.6 Create serializers in `web/api/serializers/integrations.py`
  - [ ] 7.7 Create views in `web/api/views/integrations.py`
  - [ ] 7.8 Create API functions in `frontend/src/lib/api/integrations.ts`
  - [ ] 7.9 Create React Query hooks for integration status and actions
  - [ ] 7.10 Create Dropbox integration card showing connection status
  - [ ] 7.11 Add connect/disconnect buttons with shadcn button component
  - [ ] 7.12 Display status badges (Connected, Authenticated, Not Connected)
  - [ ] 7.13 Implement connect mutation with React Query
  - [ ] 7.14 Implement disconnect mutation with React Query
  - [ ] 7.15 Show toast notifications on success/error
  - [ ] 7.16 Add Basecamp placeholder card
  - [ ] 7.17 Test integration actions: connect, disconnect, verify toast messages

- [ ] 8.0 Implement Orders Management
  - [ ] 8.1 Install table component: `npx shadcn-ui@latest add table`
  - [ ] 8.2 Install dialog component for forms: `npx shadcn-ui@latest add dialog`
  - [ ] 8.3 Create `app/(dashboard)/orders/page.tsx`
  - [ ] 8.4 Create Order serializer in `web/api/serializers/orders.py`
  - [ ] 8.5 Create OrderViewSet in `web/api/views/orders.py` with CRUD operations
  - [ ] 8.6 Register OrderViewSet in API router
  - [ ] 8.7 Create API functions in `frontend/src/lib/api/orders.ts` (list, create, get, update, delete)
  - [ ] 8.8 Create TypeScript interfaces for Order in `lib/api/types.ts`
  - [ ] 8.9 Create React Query hooks in `hooks/use-orders.ts`
  - [ ] 8.10 Create orders table component with shadcn table
  - [ ] 8.11 Display columns: order number, order date, delivery link, actions
  - [ ] 8.12 Add "Create Order" button that opens dialog
  - [ ] 8.13 Create order form in dialog with shadcn form components
  - [ ] 8.14 Implement create order mutation
  - [ ] 8.15 Implement delete order with confirmation
  - [ ] 8.16 Add pagination controls
  - [ ] 8.17 Test CRUD operations: create, view list, delete

- [ ] 9.0 Implement Reports Management
  - [ ] 9.1 Create `app/(dashboard)/reports/page.tsx`
  - [ ] 9.2 Create Report serializer in `web/api/serializers/reports.py`
  - [ ] 9.3 Create ReportViewSet in `web/api/views/reports.py`
  - [ ] 9.4 Create API functions in `frontend/src/lib/api/reports.ts`
  - [ ] 9.5 Create TypeScript interfaces for Report in `lib/api/types.ts`
  - [ ] 9.6 Create React Query hooks in `hooks/use-reports.ts`
  - [ ] 9.7 Create reports table component
  - [ ] 9.8 Display columns: order number, report type, legal description, leases, dates, actions
  - [ ] 9.9 Add report type badges (Runsheet, Base Abstract, etc.)
  - [ ] 9.10 Create report form dialog
  - [ ] 9.11 Implement create/edit report mutations
  - [ ] 9.12 Add filter by order dropdown
  - [ ] 9.13 Display associated leases with links
  - [ ] 9.14 Test CRUD operations and filters

- [ ] 10.0 Implement Leases Management
  - [ ] 10.1 Create `app/(dashboard)/leases/page.tsx`
  - [ ] 10.2 Create Lease serializer in `web/api/serializers/leases.py`
  - [ ] 10.3 Create LeaseViewSet in `web/api/views/leases.py`
  - [ ] 10.4 Create API functions in `frontend/src/lib/api/leases.ts`
  - [ ] 10.5 Create TypeScript interfaces for Lease in `lib/api/types.ts`
  - [ ] 10.6 Create React Query hooks in `hooks/use-leases.ts`
  - [ ] 10.7 Create leases table component
  - [ ] 10.8 Display columns: agency, lease number, runsheet status, links, actions
  - [ ] 10.9 Add external link icons for runsheet and document links
  - [ ] 10.10 Display runsheet_report_found status with badge
  - [ ] 10.11 Create lease form dialog for editing
  - [ ] 10.12 Implement update lease mutation
  - [ ] 10.13 Add filter by agency dropdown
  - [ ] 10.14 Test CRUD operations and filters

- [ ] 11.0 Update Docker Configuration
  - [ ] 11.1 Create `frontend/Dockerfile` with Node 20 Alpine base image
  - [ ] 11.2 Configure Dockerfile with npm install and dev server
  - [ ] 11.3 Add `.dockerignore` to frontend directory
  - [ ] 11.4 Rename `web` service to `backend` in docker-compose.yml
  - [ ] 11.5 Add `frontend` service to docker-compose.yml
  - [ ] 11.6 Configure frontend service: build from Dockerfile, port 3000, volume mount
  - [ ] 11.7 Add NEXT_PUBLIC_API_URL environment variable to frontend service
  - [ ] 11.8 Update backend CORS_ALLOWED_ORIGINS to include frontend URL
  - [ ] 11.9 Ensure all services (db, redis, backend, worker, flower, frontend) are configured
  - [ ] 11.10 Test: `docker compose down && docker compose up --build`
  - [ ] 11.11 Verify frontend accessible at localhost:3000
  - [ ] 11.12 Verify backend API accessible from frontend container

- [ ] 12.0 Testing and Cleanup
  - [ ] 12.1 Test full authentication flow: login, access protected pages, logout
  - [ ] 12.2 Test token refresh when access token expires
  - [ ] 12.3 Test all CRUD operations for Orders, Reports, Leases
  - [ ] 12.4 Test integration connect/disconnect flows
  - [ ] 12.5 Test dark mode toggle persists across page navigation
  - [ ] 12.6 Test staff vs non-staff user permissions
  - [ ] 12.7 Test error handling: network errors, 401, 403, 404
  - [ ] 12.8 Test loading states display correctly
  - [ ] 12.9 Test toast notifications for all success/error cases
  - [ ] 12.10 Remove old Django template files: delete `web/core/templates/`, `web/integrations/templates/`
  - [ ] 12.11 Remove Bootstrap static files: delete `web/static/css/`, `web/static/js/`
  - [ ] 12.12 Remove Bootstrap from base.html (if kept for admin)
  - [ ] 12.13 Update README with new setup instructions for Next.js frontend
  - [ ] 12.14 Run Django tests: `docker compose exec backend python manage.py test`
  - [ ] 12.15 Run TypeScript check: `cd frontend && npm run build`

