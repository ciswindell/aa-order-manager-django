# Data Model: Next.js Frontend Migration

**Feature**: Next.js Frontend Migration  
**Branch**: `001-nextjs-frontend-migration`  
**Date**: 2025-10-26  
**Purpose**: Define entity schemas, relationships, and validation rules

## Overview

This feature primarily adds audit logging fields to existing entities and creates API serializer representations. The core data model (Order → Report → Lease hierarchy) remains unchanged from existing Django implementation.

## Entity Schemas

### User

**Purpose**: Authentication and authorization, audit trail tracking

**Source**: Django contrib.auth.models.User (existing)

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| username | String(150) | Unique, Required | Login username |
| email | String(254) | Optional | Email address |
| password | String(128) | Required, Hashed | Password (no complexity requirements) |
| is_staff | Boolean | Default: False | Staff permission flag |
| is_superuser | Boolean | Default: False | Superuser permission flag |
| is_active | Boolean | Default: True | Account active status |
| date_joined | DateTime | Auto | Account creation timestamp |

**Relationships**:
- One-to-Many with Order (created_by, updated_by)
- One-to-Many with Report (created_by, updated_by)
- One-to-Many with Lease (created_by, updated_by)

**Business Rules**:
- Username must be unique
- Password has no complexity requirements (per clarification)
- Staff users see admin links in UI
- Only active users can authenticate

**API Representation** (UserSerializer):
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_staff": true
}
```

**Notes**: Password never included in API responses. Use Django's built-in User model, no custom user model needed.

---

### Order

**Purpose**: Top-level container grouping related reports for a work assignment

**Source**: orders.models.Order (existing, add audit fields)

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| order_number | String(255) | Required | Order identifier (not enforced unique) |
| order_date | Date | Required | Date order was placed |
| delivery_link | String(2048) | Optional | URL to delivery location |
| created_at | DateTime | Auto (add) | Record creation timestamp |
| updated_at | DateTime | Auto (update) | Last modification timestamp |
| created_by | ForeignKey(User) | Optional | User who created record |
| updated_by | ForeignKey(User) | Optional | User who last updated record |

**Relationships**:
- One-to-Many with Report (order → reports)
- Many-to-One with User (created_by, updated_by)

**Business Rules**:
- Cannot delete order if it has associated reports (enforce in API)
- Order number not enforced unique (business decision allows duplicates)
- Delivery link must be valid URL format if provided

**Validation**:
- order_number: max_length=255, required
- order_date: valid date, not future date
- delivery_link: valid URL format if present, max_length=2048

**API Representation** (OrderSerializer):
```json
{
  "id": 1,
  "order_number": "ORD-2025-001",
  "order_date": "2025-01-15",
  "delivery_link": "https://example.com/delivery/ord-001",
  "report_count": 3,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-16T14:22:00Z",
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "updated_by": {
    "id": 1,
    "username": "admin"
  }
}
```

**Indexes**: created_at, order_date (for sorting), order_number (for filtering)

---

### Report

**Purpose**: Contains legal description and represents work product associated with an order

**Source**: orders.models.Report (existing, add audit fields)

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| order | ForeignKey(Order) | Required | Parent order |
| report_type | String(100) | Required | Type (Runsheet, Base Abstract, etc.) |
| legal_description | Text | Required | Legal property description |
| report_date | Date | Optional | Report completion date |
| created_at | DateTime | Auto (add) | Record creation timestamp |
| updated_at | DateTime | Auto (update) | Last modification timestamp |
| created_by | ForeignKey(User) | Optional | User who created record |
| updated_by | ForeignKey(User) | Optional | User who last updated record |

**Relationships**:
- Many-to-One with Order (report → order)
- One-to-Many with Lease (report → leases)
- Many-to-One with User (created_by, updated_by)

**Business Rules**:
- Report must be associated with an Order
- Report type must be from predefined list (enforced in UI, choices in serializer)
- Legal description is required, no minimum length
- Cannot delete report if it has associated leases

**Validation**:
- report_type: max_length=100, required, choices validation
- legal_description: required, text field (unlimited length)
- report_date: valid date, cannot be future date
- order: must reference existing Order

**Report Type Choices**:
- "Runsheet"
- "Base Abstract"
- "Current Owner"
- "Full Abstract"
- "Title Opinion"
- "Other"

**API Representation** (ReportSerializer):
```json
{
  "id": 1,
  "order": {
    "id": 1,
    "order_number": "ORD-2025-001"
  },
  "report_type": "Runsheet",
  "legal_description": "Section 12, Township 5N, Range 3W",
  "report_date": "2025-01-20",
  "lease_count": 5,
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-20T09:15:00Z",
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "updated_by": {
    "id": 2,
    "username": "researcher"
  }
}
```

**Indexes**: order (foreign key), created_at, report_type (for filtering)

---

### Lease

**Purpose**: Individual lease record with agency, number, and links to external resources

**Source**: orders.models.Lease (existing, add audit fields)

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| report | ForeignKey(Report) | Required | Parent report |
| agency_name | String(255) | Required | Government agency name |
| lease_number | String(255) | Required | Lease identifier |
| runsheet_link | String(2048) | Optional | URL to runsheet report |
| runsheet_archive | ForeignKey(CloudLocation) | Optional | Link to Dropbox runsheet archive |
| runsheet_report_found | Boolean | Default: False | Discovery status flag |
| created_at | DateTime | Auto (add) | Record creation timestamp |
| updated_at | DateTime | Auto (update) | Last modification timestamp |
| created_by | ForeignKey(User) | Optional | User who created record |
| updated_by | ForeignKey(User) | Optional | User who last updated record |

**Relationships**:
- Many-to-One with Report (lease → report)
- Many-to-One with CloudLocation (lease → runsheet_archive)
- Many-to-One with User (created_by, updated_by)

**Business Rules**:
- Lease must be associated with a Report
- Agency name and lease number required
- Runsheet links populated by background Celery tasks (Dropbox discovery)
- runsheet_report_found flag indicates discovery workflow completion

**Validation**:
- agency_name: max_length=255, required
- lease_number: max_length=255, required
- runsheet_link: valid URL format if present, max_length=2048
- report: must reference existing Report

**Discovery Status Values** (derived from runsheet_report_found + runsheet_link presence):
- "Found": runsheet_report_found=True, runsheet_link present
- "Not Found": runsheet_report_found=True, runsheet_link=None
- "Pending": runsheet_report_found=False (discovery workflow not complete)

**API Representation** (LeaseSerializer):
```json
{
  "id": 1,
  "report": {
    "id": 1,
    "order_number": "ORD-2025-001"
  },
  "agency_name": "BLM",
  "lease_number": "NM-12345",
  "runsheet_link": "https://dropbox.com/sh/abc123/runsheet.pdf",
  "runsheet_archive_link": "https://dropbox.com/sh/abc123",
  "runsheet_status": "Found",
  "document_archive_link": "https://dropbox.com/sh/xyz789/documents",
  "created_at": "2025-01-15T12:00:00Z",
  "updated_at": "2025-01-22T16:45:00Z",
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "updated_by": {
    "id": 1,
    "username": "admin"
  }
}
```

**Indexes**: report (foreign key), agency_name (for filtering), created_at

---

### IntegrationStatus (DTO)

**Purpose**: Data transfer object representing current state of external integration

**Source**: Computed by integrations.status.service.IntegrationStatusService (not persisted)

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| provider | String | Integration name ("dropbox", "basecamp") |
| is_connected | Boolean | Whether integration is connected |
| is_authenticated | Boolean | Whether OAuth tokens are valid |
| last_sync | DateTime | Last successful sync timestamp (optional) |
| blocking_problem | Boolean | Whether issue requires immediate attention |
| action_required | String | User action needed (optional) |
| cta_url | String | URL for action (optional) |

**Business Rules**:
- Dropbox: is_connected if OAuth tokens exist and valid
- Basecamp: placeholder (coming soon)
- blocking_problem=True if authentication expired or connection failed
- Cached for 10 minutes to avoid repeated API calls

**API Representation** (IntegrationStatusSerializer):
```json
{
  "provider": "dropbox",
  "is_connected": true,
  "is_authenticated": true,
  "last_sync": "2025-01-26T08:30:00Z",
  "blocking_problem": false,
  "action_required": null,
  "cta_url": null
}
```

---

## Entity Relationship Diagram

```
┌──────────────┐
│     User     │
│              │
│ - id (PK)    │
│ - username   │
│ - email      │
│ - is_staff   │
└──────────────┘
       │
       │ created_by, updated_by (all entities below)
       │
       ▼
┌──────────────┐
│    Order     │
│              │
│ - id (PK)    │
│ - order_num  │
│ - order_date │
│ - created_at │
│ - updated_at │
└──────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐
│   Report     │
│              │
│ - id (PK)    │
│ - order_id   │───┐
│ - type       │   │
│ - legal_desc │   │
│ - created_at │   │
│ - updated_at │   │
└──────────────┘   │
       │           │
       │ 1:N       │
       ▼           │
┌──────────────┐   │
│    Lease     │   │
│              │   │
│ - id (PK)    │   │
│ - report_id  │───┘
│ - agency     │
│ - lease_num  │
│ - runsheet_* │
│ - created_at │
│ - updated_at │
└──────────────┘

External (not persisted):
┌───────────────────┐
│ IntegrationStatus │ (DTO - computed)
│                   │
│ - provider        │
│ - is_connected    │
│ - last_sync       │
└───────────────────┘
```

## Migration Plan

### Database Migrations

**Order Model**:
```python
# Migration: 0004_order_audit_fields.py
class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0003_rename_runsheet_directory_to_runsheet_archive'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='order',
            name='created_by',
            field=models.ForeignKey(null=True, blank=True, on_delete=models.SET_NULL, related_name='orders_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='updated_by',
            field=models.ForeignKey(null=True, blank=True, on_delete=models.SET_NULL, related_name='orders_updated', to=settings.AUTH_USER_MODEL),
        ),
    ]
```

**Report Model**: Similar migration adding created_at, updated_at, created_by, updated_by

**Lease Model**: Similar migration adding created_at, updated_at, created_by, updated_by

**Backfill Strategy**: Set null=True, blank=True for all audit fields. Existing records will have NULL values. New records will populate these fields automatically from request.user in API views.

## API Serializer Guidelines

### General Rules

- Use ModelSerializer for all Django models
- Include audit fields in read responses only (not required in create/update)
- Nest related entities with minimal fields (id, display name)
- Use SerializerMethodField for computed values (counts, status)
- Validate foreign keys exist before saving
- Set created_by/updated_by from request.user in view.perform_create/perform_update

### Example Serializer Pattern

```python
from rest_framework import serializers
from orders.models import Order

class OrderSerializer(serializers.ModelSerializer):
    report_count = serializers.SerializerMethodField()
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_date', 'delivery_link',
            'report_count', 'created_at', 'updated_at', 
            'created_by', 'updated_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    def get_report_count(self, obj):
        return obj.reports.count()
```

## Data Integrity Rules

1. **Cascading Deletes**:
   - Deleting Order → Prevent if reports exist (API validation)
   - Deleting Report → Prevent if leases exist (API validation)
   - Deleting User → SET_NULL for audit fields (preserve records)

2. **Required Fields**:
   - Order: order_number, order_date
   - Report: order, report_type, legal_description
   - Lease: report, agency_name, lease_number

3. **Unique Constraints**:
   - User.username (Django default)
   - No other unique constraints (per existing schema)

4. **Indexes**:
   - Foreign keys auto-indexed by Django
   - Add indexes for: created_at, order_date, report_type, agency_name (filtering/sorting)

## State Transitions

### Lease Runsheet Discovery State Machine

```
[Created] 
   │
   ├─► runsheet_report_found = False (default)
   │   Status: "Pending"
   │
   ▼
[Celery Discovery Task Runs]
   │
   ├─► Found runsheet
   │   ├─► Set runsheet_report_found = True
   │   ├─► Set runsheet_link = URL
   │   └─► Status: "Found"
   │
   └─► No runsheet found
       ├─► Set runsheet_report_found = True
       ├─► runsheet_link = None
       └─► Status: "Not Found"
```

**Notes**: Discovery runs asynchronously via Celery. Frontend polls or uses optimistic updates. No manual state transitions by users.

## Validation Summary

| Entity | Required Fields | Optional Fields | Computed Fields |
|--------|----------------|-----------------|-----------------|
| User | username, password | email | is_staff, is_superuser |
| Order | order_number, order_date | delivery_link | report_count |
| Report | order, report_type, legal_description | report_date | lease_count |
| Lease | report, agency_name, lease_number | runsheet_link, runsheet_archive | runsheet_status, document_archive_link |
| IntegrationStatus | provider, is_connected | last_sync | blocking_problem, action_required |

## Performance Considerations

- Use `select_related` for foreign keys (order, report, created_by, updated_by)
- Use `prefetch_related` for reverse relations (reports, leases)
- Paginate list endpoints (page_size=20)
- Cache integration status (10min TTL)
- Index frequently filtered fields (agency_name, report_type, order_date)
- Avoid N+1 queries by eager loading relationships in ViewSets

## Next Steps

- Generate API contracts (OpenAPI specs) in contracts/ directory
- Generate quickstart.md for developer setup
- Update agent context with entity schemas
- Proceed to Phase 2 (tasks.md generation)

