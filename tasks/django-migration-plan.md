# Django Migration Plan

## Overview

This document outlines the strategy for migrating the AA Order Manager from a Tkinter-based desktop application to a Django web application. Legacy code remains available for reference in `master`; the `django-migration` branch may break legacy imports/behavior while refactoring.

## Migration Strategy

### Branch Strategy
- **Stable Branch**: `master` (Tkinter app - production/stable)
- **Migration Branch**: `django-migration` (Django refactor; legacy may break here)
- **Approach**: Migrate in-place on the feature branch; legacy retained only as reference

### Directory Structure After Migration

```
aa-order-manager/
├── legacy/                    # All current Tkinter code (reference only on this branch)
│   ├── app.py
│   └── src/
│       ├── core/
│       │   ├── models.py
│       │   ├── services/
│       │   ├── validation/
│       │   └── workflows/
│       ├── gui/
│       └── integrations/
│
├── web/                       # Django project (active)
│   ├── manage.py
│   ├── order_manager_project/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── orders/                # Django app (avoid naming collision with `src/core`)
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py
│       ├── urls.py
│       ├── views.py
│       ├── templates/
│       ├── services/          # Migrated service layer
│       ├── workflows/         # Migrated workflows
│       └── utils/             # Migrated utils
│
├── requirements.txt           # Single shared requirements (includes Django)
├── README.md
└── .gitignore
```

## Phase 1: Setup and Structure

### Step 1: Create Migration Branch
```bash
git checkout -b django-migration
```

### Step 2: Move Legacy Code (reference only)
```bash
# Create legacy directory
mkdir -p legacy

# Move current code to legacy (will break legacy imports on this branch)
git mv app.py legacy/
git mv src/ legacy/

# Create legacy README
touch legacy/README.md
```

### Step 3: Setup Django Dependencies (single requirements)
```bash
# Update single requirements to include Django (tkcalendar not needed for web)
printf "Django>=4.2.0\ndropbox\npandas\nopenpyxl\n" > requirements.txt
pip install -r requirements.txt
```

### Step 4: Install Dependencies
```bash
# Install Django and other dependencies
pip install -r requirements.txt
```

### Step 5: Initialize Django Project
```bash
# Create Django project in web/
django-admin startproject order_manager_project web

# Create Django app (avoid name 'core' to prevent confusion)
python web/manage.py startapp orders
```

### Step 6: Configure Django Settings
```bash
# Edit the generated settings.py file
# Configure database, static files, media handling, and file upload settings
```

### Step 7: Setup User Management and Admin
```bash
# Run initial Django migrations (core Django tables)
python web/manage.py migrate

# Create superuser for admin access
python web/manage.py createsuperuser

# Test Django setup
python web/manage.py runserver
```

### Step 8: Setup Admin Interface
- Create basic admin.py file
- Prepare for model registration as models are created

## Phase 2: Core Logic Migration

### Step 1: Adapt Models to Django
```python
# web/orders/models.py - Convert dataclasses to Django models
# Reference legacy/src/core/models.py for the original dataclass structure
# Convert OrderData and OrderItemData to Django models
# Convert enums (ReportType, AgencyType) to Django TextChoices
# Add Django-specific fields like created_at, updated_at
# Add FK from OrderItem to Order
```

### Step 2: Create Database Migrations
```bash
# Create migrations for the new models
python web/manage.py makemigrations orders

# Apply migrations
python web/manage.py migrate

# Test models in Django shell
python web/manage.py shell
# >>> from orders.models import Order, OrderItem
# >>> Order.objects.all()
# >>> exit()
```

### Step 3: Migrate Integrations
```bash
# Copy cloud integrations (adjust imports to new package paths as needed)
mkdir -p web/integrations
cp -r legacy/src/integrations/* web/integrations/
```

#### Cloud services placement
```
web/
├── integrations/              # Cloud-agnostic and provider-specific code
│   ├── cloud/                 # protocols, models, factory
│   └── dropbox/               # dropbox_service.py, auth.py, workspace_handler.py, errors.py
```

### Step 4: Migrate Core Services
```bash
# Copy core services into the Django app (update imports from src.* to orders.*)
mkdir -p web/orders/services web/orders/workflows web/orders/utils
cp -r legacy/src/core/services/* web/orders/services/
cp -r legacy/src/core/workflows/* web/orders/workflows/
cp -r legacy/src/core/utils/* web/orders/utils/
```


### Notes: Model changes introduced during Phase 2 (applies now)

- Models
  - Introduced `orders.models.Lease` with unique `(agency, lease_number)`.
  - Introduced `orders.models.Report` (renamed from conceptual OrderItem) with `report_type`, required `legal_description`, optional `start_date`/`end_date`, and M2M `leases`.
  - Kept `orders.models.Order` with unique `order_number`.
  - Replaced `Lease.documents_links` JSONField with `orders.models.DocumentImagesLink` (FK to `Lease`, `url` URLField). `Lease.misc_index_link` remains a single URL.
- Relationships
  - `Order` 1→N `Report` (`Order.reports`).
  - `Report` N↔N `Lease` (`Report.leases`).
- Validation
  - All `Report` rows require `legal_description`.
  - Runsheet reports must reference exactly 1 lease; Abstract reports (Base/Supplemental/DOL) must reference ≥1 lease.
- Admin
  - `Lease` admin uses an inline for `DocumentImagesLink` (clean multi-URL input).
- Naming
  - We do not use UUIDs for these models; rely on `order_number` and natural keys.

Dev/migration tips observed
- If the admin changelist errors with a removed column (e.g., `documents_links`), it may be due to a stale sort parameter or old server process.
  - Hard refresh the changelist (e.g., `/admin/orders/lease/?o=`) or clear cookies/incognito.
  - Restart the dev server without `--noreload`.
  - In development only, removing the SQLite DB and re-running migrations can clear inconsistencies.

Downstream impact (consider in future phases)
- Services/workflows
  - Parsing and processing must create/link `Lease` rows and attach them to `Report` rows; remove any assumptions of a single `agency` on an order item.
  - Where legacy services wrote document links to a list, now create `DocumentImagesLink` rows instead.
- Forms/views/APIs
  - Report creation forms should accept: `order`, `report_type`, `legal_description`, optional dates, and selected leases (M2M selector or lease-lookup by number+agency).
  - Lease forms now manage document image links via inline rows, preserving URL validation.
- Queries/filters
  - Report lookups should filter via `report_type` and `leases__lease_number`/`leases__agency` as needed.
- Data import
  - When importing legacy data with embedded link arrays, transform them into `DocumentImagesLink` rows.



## Phase 3: Django Views and Forms

### Step 1: Create Django Forms
- Create forms for order creation and management
- Include file upload form for Excel files
- Add form validation and error handling

### Step 2: Create Django Views
- Create views for order listing and creation
- Implement file upload handling
- Add AJAX endpoints for order processing
- Include progress tracking functionality
- Update imports in migrated services/workflows from `src.core.*` to `orders_app.*` and `web.integrations.*`

### Step 3: URL Configuration
- Set up main URL configuration in `web/order_manager_project/urls.py` (include `orders.urls`)
- Create app-specific URL patterns in `web/orders/urls.py`
- Configure media file serving

## Phase 4: Templates and UI

### Step 1: Base Template
- Create base HTML template with Bootstrap styling
- Include navigation and common layout elements
- Add message display functionality

### Step 2: Order Create Template
- Create order creation form template
- Include file upload and agency selection
- Add progress tracking display
- Implement AJAX form submission

## Phase 5: Testing and Deployment

### Step 1: Test Core Functionality
```bash
# Test Django admin interface
python web/manage.py runserver
# Visit http://127.0.0.1:8000/admin/

# Test basic views
# Visit http://127.0.0.1:8000/
```

### Step 2: Test Order Processing
```bash
# Test file upload and processing
# Use Django admin to create test orders
# Test the complete workflow
```

### Step 3: Production Preparation
```bash
# Collect static files
python web/manage.py collectstatic

# Test with production settings
python web/manage.py check --deploy
```

### Step 4: Production Deployment
- Configure production database (PostgreSQL recommended)
- Set up static file serving
- Configure environment variables
- Set up reverse proxy (nginx)
- Configure WSGI server (gunicorn)

## Migration Checklist

### Phase 1: Setup ✅
- [ ] Create django-migration branch
- [ ] Move legacy code to legacy/ folder
- [ ] Setup Django dependencies
- [ ] Install dependencies
- [ ] Initialize Django project
- [ ] Configure Django settings
- [ ] Setup user management and admin
- [ ] Setup admin interface

### Phase 2: Core Logic ✅
- [ ] Adapt models to Django
- [ ] Create database migrations
- [ ] Migrate integrations
- [ ] Migrate core services
- [ ] Migrate validation

### Phase 3: Django Views and Forms ✅
- [ ] Create Django forms
- [ ] Create Django views
- [ ] Setup URL routing
- [ ] Implement file upload handling
- [ ] Add AJAX processing

### Phase 4: Templates and UI ✅
- [ ] Create base template
- [ ] Create order forms
- [ ] Implement progress tracking
- [ ] Add Bootstrap styling

### Phase 5: Testing and Deployment ✅
- [ ] Test core functionality
- [ ] Test order processing
- [ ] Create production configuration
- [ ] Deploy to production

## Benefits After Migration

1. **Web Accessibility**: Access from any device with a browser
2. **Better UX**: Modern web interface vs. Tkinter
3. **Scalability**: Can handle multiple users
4. **Database Integration**: Built-in ORM for data persistence
5. **Admin Interface**: Django admin for order management
6. **API Capabilities**: Easy to add REST API endpoints
7. **Mobile Friendly**: Responsive design works on mobile devices

## Rollback Plan

If issues arise during migration:
1. Keep working on `master` branch with Tkinter app
2. Fix issues on `django-migration` branch
3. Only merge when Django version is fully functional
4. Legacy code remains available in `legacy/` folder

## Timeline Estimate

- **Phase 1-2**: 2-3 days (setup and core migration)
- **Phase 3-4**: 3-5 days (views, forms, and templates)
- **Phase 5-6**: 2-3 days (configuration and testing)
- **Total**: 1-2 weeks for complete migration

## Notes

- Legacy code in this branch is reference-only; functionality may be broken during refactor
- Test each component thoroughly before moving to next phase
- Use Django's built-in admin for initial data management
- Consider adding REST API endpoints for future integrations
- Plan for production deployment with proper security measures
