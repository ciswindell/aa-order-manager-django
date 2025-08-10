## Phase 2 PRD: Models — Order, Lease, and Report

### Introduction / Overview

Define Django models to replace legacy dataclasses in `legacy/src/core/models.py`. Introduce a normalized `Lease` model and define `Report` (formerly `OrderItem`) to reference leases. Provide persistent storage with business and technical identifiers needed now; defer workflow-derived fields to later phases.

### Goals

- Create `Order`, `Lease`, and `Report` Django models.
- Enforce uniqueness for `Order.order_number`.
- Use `TextChoices` for `ReportType` (in `OrderItem`) and `AgencyType` (in `Lease`).
- Establish `Order` → `OrderItem` one-to-many with cascade delete.
- Include standard timestamps (`created_at`, `updated_at`).

### User Stories

- As a developer, I can persist orders and their items with validated enums and unique identifiers.
- As an admin, I can view and manage orders and items in Django admin.

### Functional Requirements

1. Model: Order
   - Fields
     1. `id`: BigAutoField (default primary key)
     2. `order_number`: CharField, unique, non-null
     3. `order_date`: DateField, non-null
     4. `order_notes`: TextField, optional
     5. `delivery_link`: URLField, optional
     6. `created_at`: DateTimeField auto_now_add=True
     7. `updated_at`: DateTimeField auto_now=True

2. Model: Lease
   - Fields
     1. `id`: BigAutoField (default primary key)
     2. `agency`: TextChoices (`AgencyType`: NMSLO, BLM), non-null
     3. `lease_number`: CharField, non-null
     4. `documents_links`: JSONField (list of URLs), default []
     5. `misc_index_link`: URLField, optional
     6. `created_at`: DateTimeField auto_now_add=True
     7. `updated_at`: DateTimeField auto_now=True
   - Constraints
     - Unique together on (`agency`, `lease_number`).

3. Model: Report
   - Fields
     1. `id`: BigAutoField (default primary key)
      2. `order`: ForeignKey to `Order` with on_delete=CASCADE, related_name="reports"
     3. `report_type`: TextChoices (`ReportType`: Runsheet, Base Abstract, Supplemental Abstract, DOL Abstract)
     4. `leases`: ManyToManyField to `Lease` (runsheet: exactly 1; abstracts: 1..N)
     5. `legal_description`: TextField, non-null (required for all items)
     6. `start_date`: DateField, null/blank allowed
     7. `end_date`: DateField, null/blank allowed
     8. `report_notes`: TextField, optional
     9. `created_at`: DateTimeField auto_now_add=True
     10. `updated_at`: DateTimeField auto_now=True

4. Enums (TextChoices)
   - `ReportType` (in `OrderItem`): Runsheet, Base Abstract, Supplemental Abstract, DOL Abstract
   - `AgencyType` (in `Lease`): NMSLO, BLM

5. Relationships & Constraints
   - `Order` 1→N `Report` with on_delete=CASCADE
   - `Report` N↔N `Lease`
   - Unique constraints: `Order.order_number` unique; `Lease(agency, lease_number)` unique
   - Validation (model `clean()` to enforce, defer strict DB constraints):
      - All reports must have `legal_description`.
      - Runsheet reports must reference exactly one `Lease`.
      - Abstract reports may reference one or more `Lease`s.

6. Migrations
   - Create and apply initial migrations for the `orders` app.

### Non-Goals (Out of Scope)

- Business logic and services migration.
- Views/templates/APIs.
- Data import/migration from legacy files.

### Design Considerations

- Keep default BigAutoField primary keys; add a unique `uuid` for external references.
- Use `JSONField` for list fields to remain SQLite-compatible in development.
- Keep enums human-readable via `TextChoices` values that match legacy strings.

### Technical Considerations

- Timezone-aware datetimes with project `America/Denver` timezone and `USE_TZ=True`.
- Indexes on frequently queried fields can be added (see Open Questions).

### Success Metrics

- `makemigrations` and `migrate` succeed with no errors.
- Admin can create an `Order` and associated `OrderItem`s.
- Uniqueness on `order_number` and `uuid` is enforced by the database.

### Open Questions

1. Lease docs fields: Confirm `misc_index_link` is singular (URL) and `documents_links` is plural (list of URLs).
2. Indexes: Any additional indexes needed (e.g., on `Lease.lease_number`)?
3. Admin: Register models with list_display and search fields now, or defer?


