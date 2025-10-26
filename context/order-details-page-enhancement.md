# Order Details Page Enhancement - Feature Specification

## Document Information
- **Document Type**: Feature Specification
- **Created**: October 26, 2025
- **Status**: Draft - Ready for Engineering Review

---

## Executive Summary

This specification describes the enhancement of the Order Management workflow to introduce a dedicated Order Details page that serves as a central hub for managing an order and its associated reports. This eliminates the need for users to navigate between multiple pages when creating and managing orders, reports, and leases.

---

## Current State Analysis

### Existing Workflow
1. **Orders Page** (`/dashboard/orders`):
   - Displays a paginated table of all orders
   - Users can create/edit/delete orders via modal dialogs
   - Shows order count for each order but no direct access to view/manage those reports
   - Clicking "Edit" on an order opens a modal with only basic order fields

2. **Reports Page** (`/dashboard/reports`):
   - Separate standalone page for managing reports
   - Users must navigate away from orders to create/manage reports
   - Requires selecting an order from a dropdown
   - Lease selection uses a multi-select dropdown showing all leases (10,000 limit)
   - No inline creation of leases during report creation

3. **Leases Page** (`/dashboard/leases`):
   - Completely separate page for lease management
   - No integration with report creation workflow

### Current Pain Points
1. **Fragmented Workflow**: Users must navigate between 3 different pages to complete a single order with reports
2. **Context Loss**: When creating reports, users lose the context of which order they're working with
3. **No Order Details View**: No dedicated page to see all information about a specific order
4. **Inflexible Lease Selection**: Cannot create new leases during report creation, forcing users to leave the workflow
5. **Poor Discoverability**: Reports for an order are not easily accessible from the orders list

---

## Proposed Solution

### New Order Details Page

#### Route
- **URL Pattern**: `/dashboard/orders/[id]`
- **Dynamic Route Parameter**: `id` (order ID)

#### Page Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ Order Details Header                                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Back Button | Order #12345                              │ │
│ │ Order Date: 10/15/2025                                   │ │
│ │ Created: 10/15/2025 by user123                          │ │
│ │ Notes: [Display order notes if present]                 │ │
│ │ Delivery Link: [Link if present]                        │ │
│ │                                                          │ │
│ │ [Edit Order Details] [Delete Order]                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ Reports Section                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Reports (3)                          [+ Add Report]     │ │
│ │                                                          │ │
│ │ ┌────────────────────────────────────────────────────┐  │ │
│ │ │ Report Table                                        │  │ │
│ │ │ - Report Type | Legal Desc | Date Range | Leases   │  │ │
│ │ │ - [Edit] [Delete] actions per row                  │  │ │
│ │ └────────────────────────────────────────────────────┘  │ │
│ │                                                          │ │
│ │ [Empty state when no reports]                           │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Feature Requirements

### 1. Navigation Changes

#### 1.1 Orders List Page Modification
**Location**: `/dashboard/orders/page.tsx`

**Changes Required**:
- Make order rows clickable - clicking anywhere on a row navigates to the order details page
- Alternatively: Add a "View Details" button/icon to the Actions column
- Consider adding visual affordance (hover state, cursor pointer) to indicate clickability

**Rationale**: Provides intuitive access to order details without cluttering the UI

---

### 2. Order Details Page - Header Section

#### 2.1 Basic Order Information Display

**Required Fields** (Read-only display):
- Order Number (prominent heading)
- Order Date
- Created Date & Username
- Updated Date & Username (if applicable)
- Order Notes (if present)
- Delivery Link (if present, as clickable link with external icon)

**Action Buttons**:
- **Back/Return Button**: Navigate back to orders list
- **Edit Order Details**: Opens modal/dialog to edit basic order fields (reuse existing edit dialog)
- **Delete Order**: Opens confirmation dialog (with cascade warning if reports exist)

#### 2.2 Edit Order Details Modal
**Reuse Existing Component**: The current edit order dialog from orders page
**Fields**:
- Order Number
- Order Date
- Order Notes (optional)
- Delivery Link (optional)

**Behavior**:
- On save: Update order info and refresh page data
- On cancel: Close modal without changes

---

### 3. Reports Section

#### 3.1 Reports List Display

**Layout**: Data table showing all reports for the current order

**Table Columns**:
1. **Report Type**: Display formatted label (e.g., "Runsheet", "Base Abstract")
2. **Legal Description**: Truncated with ellipsis, full text on hover
3. **Date Range**: Display start and end dates (e.g., "10/01/2025 to 10/15/2025" or "-" if not set)
4. **Leases**: Count of associated leases (e.g., "5 leases") - clickable to show lease list
5. **Actions**: Inline edit and delete buttons

**Empty State**:
- Display when order has no reports
- Message: "No reports added yet"
- Prominent "Add Report" button

**Report Count Badge**:
- Display total count in section header (e.g., "Reports (3)")

#### 3.2 Add Report Flow

**Trigger**: Click "+ Add Report" button

**UI Component**: Modal dialog (or slide-over panel)

**Form Fields**:
1. **Report Type** (Required)
   - Dropdown selection
   - Options: Runsheet, Base Abstract, Supplemental Abstract, DOL Abstract

2. **Legal Description** (Required)
   - Multi-line text area
   - Placeholder: "Enter legal description..."

3. **Start Date** (Optional)
   - Date picker

4. **End Date** (Optional)
   - Date picker

5. **Report Notes** (Optional)
   - Multi-line text area

6. **Leases** (Required) - **Enhanced Component**
   - Searchable multi-select component with type-ahead
   - Display format: "LEASE_NUMBER" (e.g., "NMNM 12345")
   - Search functionality: Filter by agency or lease number
   - **"+ Create New Lease" button** below the selection list

**Enhanced Lease Selection Component Specifications**:

```typescript
// Component behavior
- Shows list of existing leases filtered by search term
- Highlights already selected leases
- Click to select/deselect
- Selected leases shown as chips/badges above the list
- If no matching leases found, show "No leases found" message
- "Create New Lease" button always visible at bottom
```

#### 3.3 Inline Lease Creation

**Trigger**: Click "+ Create New Lease" button within the report creation/edit dialog

**UI Component**: Nested modal or inline form expansion within the same dialog

**Form Fields**:
1. **Agency** (Required)
   - Dropdown selection
   - Options: BLM, NMSLO

2. **Lease Number** (Required)
   - Text input
   - Placeholder: "e.g., NM-12345"

**Behavior**:
- **On Save**:
  - Create lease via API
  - Automatically add the newly created lease to the report's lease selection
  - Close the nested lease creation form
  - Return focus to the report form (do not close the report dialog)
  - Show success toast notification
  
- **On Cancel**:
  - Close nested form without creating lease
  - Return to report form

- **Error Handling**:
  - If lease with same agency + lease number already exists, show error
  - Display validation errors inline
  - Do not close the form on error

**Technical Note**: This requires creating a reusable lease creation component that can be embedded in different contexts

#### 3.4 Edit Report Flow

**Trigger**: Click edit icon/button on a report row

**UI Component**: Modal dialog (same as add report)

**Behavior**:
- Pre-populate all fields with existing report data
- Lease selection shows currently associated leases
- Allow adding/removing leases with same enhanced selection component
- Support inline lease creation (same as add flow)
- On save: Update report and refresh reports list
- On cancel: Close dialog without changes

#### 3.5 Delete Report Flow

**Trigger**: Click delete icon/button on a report row

**UI Component**: Confirmation dialog

**Behavior**:
- Show confirmation message: "Are you sure you want to delete this report?"
- Note: "The X associated lease(s) will remain in the system" (if leases exist)
- On confirm: Delete report and refresh list
- On cancel: Close dialog without changes

#### 3.6 View Associated Leases

**Trigger**: Click on lease count in a report row

**UI Component**: Modal dialog or expandable inline section

**Display**:
- Table or list showing lease details for the report
- Columns: Agency, Lease Number, Runsheet Status, Links
- Each lease links to the main leases page with filter applied
- Close button to return to order details

---

## User Workflow Examples

### Scenario 1: Create New Order with Reports
1. User navigates to `/dashboard/orders`
2. Clicks "+ Create Order" button
3. Enters order details (order number, date, notes) in modal
4. Clicks "Save"
5. **System automatically redirects to Order Details page** (`/dashboard/orders/[new-id]`)
6. User sees order header with entered information
7. Reports section shows empty state: "No reports added yet"
8. User clicks "+ Add Report" button
9. Modal opens with report form
10. User enters report type, legal description, dates
11. User clicks "+ Create New Lease" button within the modal
12. Nested lease form appears
13. User enters agency and lease number, clicks "Create"
14. Lease is created and automatically added to report's lease selection
15. User can add more leases or create additional ones
16. User clicks "Create Report"
17. Report is created, modal closes, reports table updates with new report
18. User can add more reports or navigate back to orders list

### Scenario 2: Edit Existing Order and Add Report
1. User navigates to `/dashboard/orders`
2. Clicks on an order row or "View Details" button
3. Order Details page loads showing existing information
4. User clicks "Edit Order Details"
5. Updates order information in modal, saves
6. Header refreshes with updated information
7. User scrolls to Reports section
8. Clicks "+ Add Report" to add a new report
9. (Follows same flow as Scenario 1 steps 9-17)

### Scenario 3: Edit Report with Existing Leases
1. User on Order Details page
2. Reports section shows 2 existing reports
3. User clicks edit icon on second report
4. Modal opens with report pre-populated
5. User modifies legal description
6. User types in lease search field to find additional leases
7. User selects 2 more leases from search results
8. User removes 1 previously associated lease by clicking its chip/badge
9. User clicks "Update Report"
10. Report updates, modal closes, table refreshes showing updated lease count

---

## Technical Implementation Requirements

### 3.1 Frontend Components

#### New Components to Create:
1. **`/app/dashboard/orders/[id]/page.tsx`**
   - Main order details page component
   - Fetch order data and reports data
   - Handle loading and error states

2. **`/components/orders/OrderDetailsHeader.tsx`**
   - Display order information
   - Edit and delete action buttons
   - Reusable across different contexts if needed

3. **`/components/orders/OrderReportsSection.tsx`**
   - Reports table display
   - Add report button
   - Empty state handling

4. **`/components/reports/ReportFormDialog.tsx`**
   - Unified component for create/edit report
   - Accepts mode prop: 'create' | 'edit'
   - Contains enhanced lease selection

5. **`/components/leases/LeaseSearchSelect.tsx`**
   - Enhanced searchable multi-select component
   - Type-ahead filtering
   - Selected items display
   - Integration with inline lease creation

6. **`/components/leases/InlineLeaseCreateForm.tsx`**
   - Reusable lease creation component
   - Can be embedded in other dialogs
   - Minimal, focused on agency + lease number

#### Modified Components:
1. **`/app/dashboard/orders/page.tsx`**
   - Add navigation to order details on row click
   - Modify create order success callback to redirect to details page

2. **`/hooks/useOrders.ts`**
   - Potentially add `useOrderDetails(orderId)` hook for single order fetching

### 3.2 Backend Requirements

#### API Endpoints Needed:

**Orders**:
- `GET /api/orders/:id/` - Fetch single order with details
- Existing endpoints for update/delete should be sufficient

**Reports**:
- `GET /api/reports/?order_id=:id` - Fetch reports for specific order (may already exist)
- Existing create/update/delete endpoints should be sufficient

**Leases**:
- `GET /api/leases/?search=:term` - Search leases by agency or lease number
- Existing create endpoint should be sufficient



### 3.3 Routing Changes

**New Routes**:
- `/dashboard/orders/[id]` - Order details page (dynamic route)

**Navigation Updates**:
- Orders list → Order details (on row click or view button)
- Order creation success → Redirect to new order details page
- Order details → Back to orders list (back button)

---

## UI/UX Specifications

### Design Principles
1. **Single Source of Truth**: Order details page is the canonical view for all order-related operations
2. **Progressive Disclosure**: Show information in hierarchy - order basics first, then reports
3. **Minimal Navigation**: Reduce page transitions for related operations
4. **Contextual Actions**: Actions appear where they're needed
5. **Clear Affordances**: Make interactive elements obvious

### Visual Design Guidelines

#### Order Header Section
- Background: Subtle card/panel style to distinguish from reports section
- Typography: Order number as H1, other fields as metadata
- Spacing: Generous whitespace between information groups
- Action buttons: Aligned right, secondary and destructive styles

#### Reports Section
- Clear visual separation from header (spacing + optional divider)
- Section title: H2 with count badge
- Table: Standard data table styling with hover states
- Empty state: Centered, prominent call-to-action

#### Dialogs/Modals
- Report form: Wide modal (max-w-2xl) to accommodate form fields
- Nested lease creation: Can be inline expansion or nested modal (less preferred)
- Consistent spacing and field grouping
- Clear visual hierarchy between form sections

#### Lease Selection Component
- Search input: Clear icon, placeholder text
- Results list: Scrollable, max height
- Selected items: Chips/badges above search with remove icons
- Create button: Secondary style, full width, fixed at bottom


## Error Handling & Edge Cases

### Error States
1. **Order Not Found**: Display error message with link back to orders list
2. **Network Errors**: Show toast notifications with retry option
3. **Permission Errors**: Display appropriate message if user lacks access
4. **Validation Errors**: Inline field-level validation messages

### Edge Cases
1. **No Reports**: Show empty state with clear call-to-action
2. **Order with Many Reports**: Implement pagination or virtual scrolling if >20 reports
3. **Duplicate Lease Creation**: Prevent duplicate agency + lease number combinations
4. **Concurrent Edits**: Implement optimistic updates with rollback on error
5. **Orphaned Data**: Handle gracefully if referenced data is deleted

---

## Accessibility Requirements

1. **Keyboard Navigation**: All interactive elements accessible via keyboard
2. **Screen Readers**: Proper ARIA labels and semantic HTML
3. **Focus Management**: Focus returns appropriately when closing dialogs
4. **Color Contrast**: Meet WCAG AA standards
5. **Interactive Elements**: Minimum touch target size 44x44px


**Document End**

