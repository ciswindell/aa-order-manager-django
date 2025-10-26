# Data Model: Order Details Page Enhancement

**Feature**: 002-order-details-page  
**Created**: October 26, 2025  
**Purpose**: Define entity relationships, data structures, and state management

---

## Entity Relationship Overview

```
┌─────────────────┐
│     Order       │
│  (1 entity)     │
│                 │
│ - id            │
│ - order_number  │
│ - order_date    │
│ - order_notes   │
│ - delivery_link │
│ - created_at    │
│ - created_by    │
│ - updated_at    │
│ - updated_by    │
└────────┬────────┘
         │
         │ 1:N (One Order has Many Reports)
         │
         ▼
┌─────────────────┐
│     Report      │
│  (N entities)   │
│                 │
│ - id            │
│ - order_id      │◄───── Foreign Key to Order
│ - report_type   │
│ - legal_desc    │
│ - start_date    │
│ - end_date      │
│ - report_notes  │
│ - created_at    │
│ - updated_at    │
└────────┬────────┘
         │
         │ M:N (Many Reports have Many Leases)
         │      via report_leases junction table
         ▼
┌─────────────────┐
│     Lease       │
│  (M entities)   │
│                 │
│ - id            │
│ - agency        │
│ - lease_number  │
│ - runsheet_link │
│ - runsheet_status│
│ - document_link │
│ - created_at    │
│ - updated_at    │
└─────────────────┘
```

**Key Relationships**:
- **Order → Report**: One-to-Many (one order contains multiple reports)
- **Report → Lease**: Many-to-Many (one report references multiple leases, one lease can be used by multiple reports)
- **Order → Lease**: Indirect through Report (an order's leases are the union of all its reports' leases)

---

## Backend Data Model (Existing)

### Order Model

**Django Model**: `orders.models.Order`

```python
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=100, unique=True)
    order_date = models.DateField()
    order_notes = models.TextField(blank=True, null=True)
    delivery_link = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders_updated')
    
    @property
    def report_count(self):
        return self.reports.count()
```

**Validation Rules**:
- `order_number`: Required, unique, max 100 characters
- `order_date`: Required, valid date
- `order_notes`: Optional, text
- `delivery_link`: Optional, valid URL format
- Cannot delete if reports exist (enforced by backend)

### Report Model

**Django Model**: `orders.models.Report`

```python
class Report(models.Model):
    REPORT_TYPES = [
        ('RUNSHEET', 'Runsheet'),
        ('BASE_ABSTRACT', 'Base Abstract'),
        ('SUPPLEMENTAL_ABSTRACT', 'Supplemental Abstract'),
        ('DOL_ABSTRACT', 'DOL Abstract'),
    ]
    
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    legal_description = models.TextField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    report_notes = models.TextField(blank=True, null=True)
    leases = models.ManyToManyField('Lease', related_name='reports', through='ReportLease')
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports_updated')
    
    @property
    def lease_count(self):
        return self.leases.count()
```

**Validation Rules**:
- `order`: Required, must reference existing Order
- `report_type`: Required, must be one of the defined choices
- `legal_description`: Required, text field
- `start_date`: Optional, valid date
- `end_date`: Optional, valid date, should be >= start_date (optional validation)
- `leases`: Required, at least one lease must be associated
- Cascade delete when parent order is deleted

### Lease Model

**Django Model**: `orders.models.Lease`

```python
class Lease(models.Model):
    AGENCY_CHOICES = [
        ('BLM', 'Bureau of Land Management'),
        ('NMSLO', 'New Mexico State Land Office'),
    ]
    
    RUNSHEET_STATUS = [
        ('Found', 'Found'),
        ('Not Found', 'Not Found'),
        ('Pending', 'Pending'),
    ]
    
    id = models.AutoField(primary_key=True)
    agency = models.CharField(max_length=10, choices=AGENCY_CHOICES)
    lease_number = models.CharField(max_length=100)
    runsheet_link = models.URLField(blank=True, null=True)
    runsheet_archive_link = models.URLField(blank=True, null=True)
    runsheet_status = models.CharField(max_length=20, choices=RUNSHEET_STATUS, default='Pending')
    document_archive_link = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='leases_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='leases_updated')
    
    class Meta:
        unique_together = [['agency', 'lease_number']]
```

**Validation Rules**:
- `agency`: Required, must be 'BLM' or 'NMSLO'
- `lease_number`: Required, unique per agency (compound unique constraint)
- `runsheet_status`: Defaults to 'Pending', updated by background tasks
- Links are managed by background Celery tasks (not user-editable)
- Cannot be deleted if associated with reports (referential integrity)

---

## Frontend Data Types (TypeScript)

### Order Types

```typescript
// Existing type from lib/api/types.ts
export interface Order {
  id: number;
  order_number: string;
  order_date: string; // ISO 8601 date string "YYYY-MM-DD"
  order_notes: string | null;
  delivery_link: string | null;
  report_count: number;
  created_at: string; // ISO 8601 datetime
  updated_at: string;
  created_by: number | null;
  created_by_username: string | null;
  updated_by: number | null;
  updated_by_username: string | null;
}

// Existing form data type
export interface OrderFormData {
  order_number: string;
  order_date: string;
  order_notes?: string;
  delivery_link?: string;
}

// NEW: Extended order details with nested reports
export interface OrderDetails extends Order {
  reports: Report[]; // Optional: Full report objects (if using single endpoint)
}
```

### Report Types

```typescript
// Existing type from lib/api/types.ts
export interface Report {
  id: number;
  order: {
    id: number;
    order_number: string;
  };
  report_type: ReportType;
  legal_description: string;
  start_date: string | null;
  end_date: string | null;
  report_notes: string | null;
  lease_ids: number[];
  leases: Lease[]; // NEW: Full lease objects for inline display
  lease_count: number;
  created_at: string;
  updated_at: string;
  created_by: {
    id: number;
    username: string;
  } | null;
  updated_by: {
    id: number;
    username: string;
  } | null;
}

// Existing form data type
export interface ReportFormData {
  order_id: number;
  report_type: string;
  legal_description: string;
  start_date?: string;
  end_date?: string;
  report_notes?: string;
  lease_ids?: number[];
}

// Existing report type enum
export type ReportType =
  | 'RUNSHEET'
  | 'BASE_ABSTRACT'
  | 'SUPPLEMENTAL_ABSTRACT'
  | 'DOL_ABSTRACT';

export const REPORT_TYPE_LABELS: Record<ReportType, string> = {
  RUNSHEET: 'Runsheet',
  BASE_ABSTRACT: 'Base Abstract',
  SUPPLEMENTAL_ABSTRACT: 'Supplemental Abstract',
  DOL_ABSTRACT: 'DOL Abstract',
};
```

### Lease Types

```typescript
// Existing type from lib/api/types.ts
export interface Lease {
  id: number;
  agency: AgencyType;
  lease_number: string;
  runsheet_link: string | null;
  runsheet_archive_link: string | null;
  runsheet_status: RunsheetStatus;
  document_archive_link: string | null;
  created_at: string;
  updated_at: string;
  created_by: {
    id: number;
    username: string;
  } | null;
  updated_by: {
    id: number;
    username: string;
  } | null;
}

// Existing form data type
export interface LeaseFormData {
  agency: AgencyType;
  lease_number: string;
}

// Existing type enums
export type AgencyType = 'BLM' | 'NMSLO';
export type RunsheetStatus = 'Found' | 'Not Found' | 'Pending';
```

### NEW: Component-Specific Types

```typescript
// For lease search select component
export interface LeaseOption {
  label: string;      // Display text: "NMNM 12345"
  value: number;      // Lease ID
  lease: Lease;       // Full lease object for details
}

// For inline display in reports table
export interface LeaseDisplayItem {
  id: number;
  lease_number: string;
  agency: AgencyType;
  runsheet_status: RunsheetStatus;
}

// For dialog state management
export type ReportDialogMode = 'create' | 'edit';

export interface ReportDialogState {
  open: boolean;
  mode: ReportDialogMode;
  report?: Report; // Present when mode is 'edit'
}
```

---

## Frontend State Management

### React Query Cache Keys

```typescript
// Existing cache keys
['orders', page, pageSize]                    // Orders list pagination
['reports', page, pageSize, orderId?]         // Reports list with optional order filter
['leases', page, pageSize, reportId?, agency?] // Leases list with optional filters

// NEW cache keys
['order', orderId]                            // Single order details
['order', orderId, 'reports']                 // Reports for specific order (if not using filter)
```

### Component State Patterns

#### Order Details Page State

```typescript
interface OrderDetailsPageState {
  // Data from React Query hooks
  order: Order | undefined;
  reports: Report[];
  isLoadingOrder: boolean;
  isLoadingReports: boolean;
  
  // UI state
  reportDialogState: ReportDialogState;
  deleteDialogOpen: boolean;
  selectedReport: Report | null;
  
  // Actions
  openCreateReportDialog: () => void;
  openEditReportDialog: (report: Report) => void;
  closeReportDialog: () => void;
  openDeleteDialog: (report: Report) => void;
  closeDeleteDialog: () => void;
}
```

#### Report Form Dialog State

```typescript
interface ReportFormDialogState {
  // Form data
  formData: ReportFormData;
  setFormData: (data: ReportFormData) => void;
  
  // Lease selection
  selectedLeaseIds: number[];
  isCreatingLease: boolean;
  
  // Actions
  toggleLeaseSelection: (leaseId: number) => void;
  openInlineLeaseCreate: () => void;
  closeInlineLeaseCreate: () => void;
  handleLeaseCreated: (lease: Lease) => void;
  
  // Submission
  isSubmitting: boolean;
  handleSubmit: () => void;
}
```

#### Lease Search Select State

```typescript
interface LeaseSearchSelectState {
  // Search
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  debouncedSearchTerm: string;
  
  // Filtering
  filteredLeases: Lease[];
  isFiltering: boolean;
  
  // Selection
  selected: number[];
  onChange: (selected: number[]) => void;
  
  // UI
  dropdownOpen: boolean;
  focusedIndex: number;
}
```

---

## Data Flow Diagrams

### Creating a Report Flow

```
User Action                    Component State                Backend API
─────────────────────────────────────────────────────────────────────────
1. Click "Add Report"
   ▼
   Open ReportFormDialog
   with empty formData
                              ▼
                              mode = 'create'
                              formData = initial
                              selectedLeaseIds = []

2. User fills form fields
   (type, legal desc, dates)
                              ▼
                              formData updated
                              via setFormData()

3. User searches for leases
   Types in search box
                              ▼
                              searchTerm updated
                              filteredLeases calculated
                              (client-side filter)

4. User clicks lease
   in dropdown
                              ▼
                              selectedLeaseIds updated
                              lease chip displayed

5. User clicks "Create New Lease"
                              ▼
                              isCreatingLease = true
                              Shows InlineLeaseCreateForm

6. User fills agency + number
   Clicks "Create"
                              ▼
                              InlineLeaseCreateForm
                              calls createLease()
                                                    ▼
                                                    POST /api/leases/
                                                    {agency, lease_number}
                                                    ▼
                                                    Returns new lease
                              ▼
                              handleLeaseCreated()
                              adds lease.id to
                              selectedLeaseIds
                              isCreatingLease = false

7. User clicks "Create Report"
                              ▼
                              handleSubmit()
                              calls createReport()
                                                    ▼
                                                    POST /api/reports/
                                                    {order_id, type, ...}
                                                    ▼
                                                    Returns new report
                              ▼
                              invalidateQueries(['reports'])
                              invalidateQueries(['order', orderId])
                              close dialog
                              show success toast

Order Details Page
   ▼
   Reports table auto-refreshes
   (React Query refetch)
   Shows new report in list
```

### Viewing Order Details Flow

```
User Action                    Component State                Backend API
─────────────────────────────────────────────────────────────────────────
1. Click order row on list page
   ▼
   router.push(`/orders/${id}`)

2. Order Details Page loads
   ▼
   useOrderDetails(id)
   useReports(1, 100, id)
                                                    ▼
                                                    GET /api/orders/{id}/
                                                    GET /api/reports/?order_id={id}
                                                    ▼
                                                    Returns order + reports
                              ▼
                              order = {...}
                              reports = [...]
                              isLoading = false

3. Page renders
   OrderDetailsHeader
     shows order info
   
   OrderReportsSection
     renders reports table
     each row shows:
       - report type
       - legal description
       - date range
       - lease numbers inline ◄── leases array from report
       
4. User clicks lease number
                              ▼
                              openLeaseDetailsPopover(lease)
                              Shows popover with:
                                - agency
                                - runsheet status
                                - links

5. User clicks "Edit" on report
                              ▼
                              reportDialogState = {
                                open: true,
                                mode: 'edit',
                                report: {...}
                              }
                              ReportFormDialog opens
                              with formData pre-filled
                              from selected report
```

---

## Data Validation Rules

### Client-Side Validation

**Order Form**:
```typescript
const validateOrderForm = (data: OrderFormData): ValidationErrors => {
  const errors: ValidationErrors = {};
  
  if (!data.order_number.trim()) {
    errors.order_number = 'Order number is required';
  }
  
  if (!data.order_date) {
    errors.order_date = 'Order date is required';
  }
  
  if (data.delivery_link && !isValidUrl(data.delivery_link)) {
    errors.delivery_link = 'Must be a valid URL';
  }
  
  return errors;
};
```

**Report Form**:
```typescript
const validateReportForm = (data: ReportFormData): ValidationErrors => {
  const errors: ValidationErrors = {};
  
  if (!data.report_type) {
    errors.report_type = 'Report type is required';
  }
  
  if (!data.legal_description.trim()) {
    errors.legal_description = 'Legal description is required';
  }
  
  if (!data.lease_ids || data.lease_ids.length === 0) {
    errors.lease_ids = 'At least one lease must be selected';
  }
  
  if (data.start_date && data.end_date && data.end_date < data.start_date) {
    errors.end_date = 'End date must be after start date';
  }
  
  return errors;
};
```

**Lease Form**:
```typescript
const validateLeaseForm = (data: LeaseFormData): ValidationErrors => {
  const errors: ValidationErrors = {};
  
  if (!data.agency) {
    errors.agency = 'Agency is required';
  }
  
  if (!data.lease_number.trim()) {
    errors.lease_number = 'Lease number is required';
  }
  
  return errors;
};
```

### Server-Side Validation (Enforced by Django)

- Order number uniqueness
- Foreign key integrity (order_id in reports, lease_ids in reports)
- Enum choices (report_type, agency, runsheet_status)
- URL format validation
- Cannot delete order with reports
- Cannot create report without leases
- Agency + lease_number compound uniqueness

---

## Performance Considerations

### Data Fetching Optimization

**Parallel Fetching**:
```typescript
// Fetch order and reports in parallel
const { data: order } = useOrderDetails(orderId);
const { reports } = useReports(1, 100, orderId);

// Both requests fire simultaneously, page renders when both complete
```

**Pagination Strategy**:
- Orders list: Paginated (20 per page)
- Reports on order details: No pagination (assume <100 per order)
- Leases in search: Client-side filter (assume <10,000 total leases)

**Caching Strategy**:
```typescript
// TanStack Query defaults
{
  staleTime: 5 * 60 * 1000,      // 5 minutes
  cacheTime: 10 * 60 * 1000,     // 10 minutes
  refetchOnWindowFocus: true,     // Refresh on tab focus
  refetchOnReconnect: true,       // Refresh after network reconnect
}
```

### Rendering Optimization

**Memoization**:
```typescript
// Memoize filtered leases to avoid recalculation
const filteredLeases = useMemo(
  () => allLeases.filter(lease => 
    lease.lease_number.toLowerCase().includes(searchTerm.toLowerCase())
  ),
  [allLeases, searchTerm]
);

// Memoize lease options for select component
const leaseOptions = useMemo(
  () => filteredLeases.map(lease => ({
    label: lease.lease_number,
    value: lease.id,
    lease,
  })),
  [filteredLeases]
);
```

**Virtualization** (if needed for large lists):
```typescript
// Only if leases >100 in search results
import { useVirtualizer } from '@tanstack/react-virtual';

const virtualizer = useVirtualizer({
  count: filteredLeases.length,
  getScrollElement: () => scrollRef.current,
  estimateSize: () => 40, // Height of each lease item
});
```

---

## Migration Notes

**No database migrations required** - this feature uses existing models without schema changes.

**Potential Backend Updates**:
1. Add `search` query parameter to `/api/leases/` endpoint (if not exists)
2. Verify `/api/orders/{id}/` endpoint exists for single order retrieval
3. Verify `/api/reports/?order_id={id}` filter works correctly

**Frontend Type Additions**:
- Extend `Report` interface to include full `leases` array (or fetch separately)
- Add component-specific types (`LeaseOption`, `ReportDialogState`, etc.)
- No breaking changes to existing types

---

## Summary

**Entities**: 3 (Order, Report, Lease) - all existing  
**Relationships**: 1:N (Order→Report), M:N (Report→Lease)  
**New Backend APIs**: 0 (may need query param additions)  
**New Frontend Types**: 4 (component-specific helpers)  
**State Management**: TanStack Query for server state, React useState for UI state  
**Validation**: Client-side for UX, server-side for integrity  
**Performance**: Parallel fetching, memoization, optional virtualization

**Data Model Status**: ✅ Complete - All entities and relationships documented

