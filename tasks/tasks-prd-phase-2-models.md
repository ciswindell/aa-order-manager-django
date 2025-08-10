## Relevant Files

- `web/orders/models.py` - Define `Order`, `Lease`, and `Report` with enums.
- `web/orders/admin.py` - Register models for admin management and filters.
- `web/orders/migrations/` - Auto-generated migrations for models and constraints.
- `web/orders/apps.py` - App configuration (existing).
- `web/order_manager_project/settings.py` - Ensure app is installed (done in Phase 1).

### Notes

- Use `python3` for all commands on Linux.
- Create migrations with: `python3 web/manage.py makemigrations orders`.
- Apply with: `python3 web/manage.py migrate`.
 

## Tasks

- [ ] 1.0 Define enums using `TextChoices`
  - [x] 1.1 `ReportType` for `Report` (Runsheet, Base Abstract, Supplemental Abstract, DOL Abstract)
  - [x] 1.2 `AgencyType` for `Lease` (NMSLO, BLM)
- [ ] 2.0 Implement `Order` model
  - [x] 2.1 Fields: `uuid` (unique), `order_number` (unique), `order_date`, `order_notes`, `delivery_link`, timestamps
- [ ] 3.0 Implement `Lease` model
  - [x] 3.1 Fields: `agency` (enum), `lease_number`, `documents_links` (JSON), `misc_index_link` (URL), timestamps
  - [x] 3.2 Constraint: unique together (`agency`, `lease_number`)
- [ ] 4.0 Implement `Report` model
  - [x] 4.1 Fields: `order` FK (CASCADE), `report_type` (enum), `leases` M2M to `Lease`, `legal_description` (required), `start_date` (nullable), `end_date` (nullable), `report_notes` (optional), timestamps
  - [x] 4.2 Validation in `clean()`: require `legal_description`; if Runsheet then exactly one lease; if Abstract then at least one lease
- [ ] 5.0 Create and apply migrations
  - [x] 5.1 `python3 web/manage.py makemigrations orders`
  - [x] 5.2 `python3 web/manage.py migrate`
- [ ] 6.0 Register models in Django admin
  - [x] 6.1 Register `Order` with list_display (`order_number`, `order_date`) and search (`order_number`)
  - [x] 6.2 Register `Lease` with list_display (`agency`, `lease_number`) and search (`lease_number`)
  - [x] 6.3 Register `Report` with list_display (`order`, `report_type`, `legal_description`) and filters (`report_type`)
- [ ] 7.0 Optional indexes (if needed later)
  - [ ] 7.1 Add DB index on `Lease.lease_number`

