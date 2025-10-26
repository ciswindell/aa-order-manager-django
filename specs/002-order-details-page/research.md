# Research: Order Details Page Enhancement

**Feature**: 002-order-details-page  
**Created**: October 26, 2025  
**Purpose**: Document technical decisions, patterns, and best practices for implementation

---

## 1. Next.js Dynamic Route Implementation

### Decision: Use App Router Dynamic Routes with TypeScript

**Chosen Approach**: Create `/app/dashboard/orders/[id]/page.tsx` with typed params

```typescript
// Pattern for dynamic route page component
interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function OrderDetailsPage({ params }: PageProps) {
  const { id } = await params;
  // Use id to fetch order data
}
```

**Rationale**:
- App Router supports dynamic routes via folder naming convention `[id]`
- TypeScript params are now promises in Next.js 15+ requiring await
- Server components can fetch data directly, but we'll use client component with hooks for interactivity

**Alternatives Considered**:
- ❌ Pages Router: Outdated, not aligned with constitution requirement for App Router
- ❌ Query parameters: Less clean URLs, harder to share/bookmark specific orders

**References**:
- Next.js App Router Dynamic Routes: https://nextjs.org/docs/app/building-your-application/routing/dynamic-routes
- Existing codebase pattern: `frontend/src/app/dashboard/` structure

---

## 2. Component Architecture & Composition

### Decision: Create Feature-Specific Component Directories

**Chosen Structure**:
```
components/
├── orders/              # Order-specific components
│   ├── OrderDetailsHeader.tsx
│   └── OrderReportsSection.tsx
├── reports/             # Report-specific components
│   └── ReportFormDialog.tsx
└── leases/              # Lease-specific components
    ├── LeaseSearchSelect.tsx
    └── InlineLeaseCreateForm.tsx
```

**Rationale**:
- **Feature Co-location**: Groups related components by domain entity (orders, reports, leases)
- **Reusability**: Components can be imported and reused across different pages
- **Single Responsibility**: Each component has one clear purpose
- **Discoverability**: Easy to find order-related vs report-related vs lease-related components

**Alternatives Considered**:
- ❌ Flat `components/` directory: Poor organization as codebase grows
- ❌ Co-locate with page: Makes reuse harder, violates DRY if needed elsewhere
- ✅ Hybrid: Keep `ui/` for shadcn components, feature directories for domain logic

**Example Component Responsibilities**:
- `OrderDetailsHeader`: Display order info, edit/delete actions (read + actions)
- `OrderReportsSection`: Reports table, add report button, empty state (list + create trigger)
- `ReportFormDialog`: Report creation/editing form with lease selection (complex form)
- `LeaseSearchSelect`: Searchable multi-select with inline create trigger (complex input)
- `InlineLeaseCreateForm`: Lease creation form embedded in report dialog (nested form)

---

## 3. Enhanced Lease Selection Component Pattern

### Decision: Combobox-Style Multi-Select with Inline Creation

**Chosen Approach**: Custom component built on shadcn/ui primitives

**Key Features**:
1. **Search Input**: Real-time filtering of lease list as user types
2. **Visual Selection**: Show selected leases as removable chips/badges
3. **Inline Results**: Scrollable list below search showing matches
4. **Inline Create**: "Create New Lease" button always visible at bottom
5. **Keyboard Navigation**: Support arrow keys and enter for accessibility

**Component API**:
```typescript
interface LeaseSearchSelectProps {
  selected: number[];              // Array of selected lease IDs
  onChange: (selected: number[]) => void;
  onCreateLease?: () => void;      // Trigger inline creation
  placeholder?: string;
  disabled?: boolean;
}
```

**Implementation Strategy**:
```typescript
// State management within component
const [searchTerm, setSearchTerm] = useState('')
const [open, setOpen] = useState(false)

// Filter leases based on search term (client-side)
const filteredLeases = allLeases.filter(lease => 
  lease.lease_number.toLowerCase().includes(searchTerm.toLowerCase())
)

// Debounce search for performance (300ms)
const debouncedSearch = useMemo(
  () => debounce(setSearchTerm, 300),
  []
)
```

**Rationale**:
- **User Experience**: No page navigation, immediate feedback
- **Performance**: Client-side filtering for <10K leases, debounced for responsiveness
- **Accessibility**: Keyboard navigation, ARIA labels, screen reader support
- **Flexibility**: Can be reused anywhere lease selection is needed

**Alternatives Considered**:
- ❌ Simple multi-select dropdown: Poor UX for large lists, no search
- ❌ Modal with search: Extra click, breaks flow, more complex state
- ✅ Combobox pattern: Industry standard, accessible, performant

**References**:
- shadcn/ui Combobox: https://ui.shadcn.com/docs/components/combobox
- shadcn/ui Multi-Select (community): Similar pattern for inspiration
- Existing codebase: `frontend/src/components/ui/multi-select.tsx` exists and can be enhanced

---

## 4. Inline Form Handling Pattern

### Decision: Embedded Form with Local State Management

**Chosen Pattern**: Toggle between display mode and create mode within same component

```typescript
// Parent component (ReportFormDialog)
const [isCreatingLease, setIsCreatingLease] = useState(false)

// Toggle between modes
{isCreatingLease ? (
  <InlineLeaseCreateForm
    onSuccess={(newLease) => {
      // Add new lease to selection
      setFormData({...formData, lease_ids: [...formData.lease_ids, newLease.id]})
      setIsCreatingLease(false)
    }}
    onCancel={() => setIsCreatingLease(false)}
  />
) : (
  <LeaseSearchSelect
    selected={formData.lease_ids}
    onChange={(ids) => setFormData({...formData, lease_ids: ids})}
    onCreateLease={() => setIsCreatingLease(true)}
  />
)}
```

**Rationale**:
- **Context Preservation**: User stays in report creation dialog
- **Simple State**: Boolean toggle, no complex navigation state
- **Error Recovery**: Errors in lease creation don't lose report form data
- **Immediate Feedback**: New lease automatically selected in parent form

**Alternatives Considered**:
- ❌ Nested modal: Complex z-index management, poor UX, mobile issues
- ❌ Separate page: Loses context, requires state persistence
- ✅ Inline toggle: Clean, simple, preserves context

**Error Handling**:
- Validation errors keep inline form open with error messages
- Network errors show toast notification + keep form open with retry option
- Success closes inline form, adds lease to selection, shows success toast

---

## 5. Data Fetching & State Management Strategy

### Decision: TanStack Query with Optimistic Updates

**Chosen Approach**: Leverage existing hooks pattern, add new hooks as needed

**New Hook**: `useOrderDetails(orderId: number)`
```typescript
export function useOrderDetails(orderId: number) {
  return useQuery({
    queryKey: ['order', orderId],
    queryFn: () => getOrder(orderId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
```

**Parallel Data Fetching**:
```typescript
// In order details page component
const { data: order, isLoading: orderLoading } = useOrderDetails(orderId)
const { reports, isLoading: reportsLoading } = useReports(1, 100, orderId)

// Show loading state until both complete
if (orderLoading || reportsLoading) return <LoadingState />
```

**Optimistic Updates** (existing pattern):
- Create report: Immediately add to list, rollback on error
- Delete report: Immediately remove from list, rollback on error
- Edit report: Immediately update in list, rollback on error

**Cache Invalidation**:
```typescript
// After creating/updating/deleting reports
queryClient.invalidateQueries({ queryKey: ['reports'] })
queryClient.invalidateQueries({ queryKey: ['order', orderId] }) // Update report count
```

**Rationale**:
- **Consistency**: Matches existing codebase patterns (useOrders, useReports, useLeases)
- **Performance**: TanStack Query handles caching, deduplication, background refetch
- **UX**: Optimistic updates provide instant feedback
- **Reliability**: Automatic rollback on errors maintains data consistency

**Alternatives Considered**:
- ❌ useState + useEffect: Manual cache management, more code, error-prone
- ❌ SWR: Different from existing pattern, would break consistency
- ✅ TanStack Query: Constitutional requirement, already in use

---

## 6. Lease Number Display Strategy

### Decision: Inline Comma-Separated List with Truncation

**Chosen Approach**: Display lease numbers inline in table cell with smart truncation

**Display Pattern**:
```typescript
// For reports with few leases (1-5): Show all
"NMNM 12345, NMNM 67890, NMNM 11111"

// For reports with many leases (6+): Show first 5 + count
"NMNM 12345, NMNM 67890, NMNM 11111, NMNM 22222, NMNM 33333 +3 more"

// Clicking "+3 more" expands to show all inline or opens popover
```

**Implementation**:
```typescript
interface LeaseDisplayProps {
  leases: Lease[];
  maxVisible?: number; // Default: 5
}

function LeaseNumberDisplay({ leases, maxVisible = 5 }: LeaseDisplayProps) {
  const [expanded, setExpanded] = useState(false)
  const visibleLeases = expanded ? leases : leases.slice(0, maxVisible)
  const hiddenCount = leases.length - maxVisible
  
  return (
    <div className="flex flex-wrap gap-1">
      {visibleLeases.map(lease => (
        <button
          key={lease.id}
          onClick={() => showLeaseDetails(lease)}
          className="text-primary hover:underline"
        >
          {lease.lease_number}
        </button>
      ))}
      {!expanded && hiddenCount > 0 && (
        <button onClick={() => setExpanded(true)} className="text-muted-foreground">
          +{hiddenCount} more
        </button>
      )}
    </div>
  )
}
```

**Rationale**:
- **Immediate Visibility**: Users see lease numbers without clicking
- **Scalability**: Handles reports with many leases gracefully
- **Interaction**: Each lease number is clickable for details
- **Responsive**: Wraps on smaller screens, truncates on very small screens

**Alternatives Considered**:
- ❌ Show count only: Doesn't meet requirement for inline visibility
- ❌ Show all always: Poor UX for reports with 20+ leases
- ❌ Fixed truncation: May cut mid-number, poor UX
- ✅ Smart truncation: Best balance of visibility and space

**Lease Details Interaction**:
- Click lease number → Show popover/modal with:
  - Agency
  - Lease Number
  - Runsheet Status (badge with color coding)
  - Runsheet Link (if available)
  - Document Archive Link (if available)
- Popover positioned near clicked lease number
- Click outside or ESC to close

---

## 7. Backend API Requirements

### Decision: Minimal Backend Changes - Leverage Existing Endpoints

**Required Endpoints** (verify/add query parameters):

1. **Get Single Order**: `GET /api/orders/{id}/`
   - **Status**: Likely exists (verify)
   - **Response**: Full order object with all fields
   - **No changes needed if exists**

2. **Get Reports by Order**: `GET /api/reports/?order_id={id}`
   - **Status**: Likely exists (verify)
   - **Response**: Paginated list of reports
   - **May need to add**: `order_id` query parameter if not present

3. **Search Leases**: `GET /api/leases/?search={term}`
   - **Status**: May need to add `search` parameter
   - **Implementation**: Django filter on `lease_number__icontains=term`
   - **Response**: Paginated list of matching leases

**Verification Steps**:
```bash
# Test existing endpoints
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/orders/1/
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/reports/?order_id=1
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/leases/?search=NMNM
```

**Backend Changes (if needed)**:
```python
# In web/api/views/leases.py
class LeaseViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = Lease.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(lease_number__icontains=search) |
                Q(agency__icontains=search)
            )
        return queryset
```

**Rationale**:
- **Minimal Changes**: Leverage existing infrastructure
- **Django Patterns**: Query parameters are standard DRF practice
- **Performance**: Database indexes on lease_number already exist
- **Backward Compatible**: Adding optional query params doesn't break existing clients

---

## 8. Navigation & URL Structure

### Decision: Automatic Redirect After Order Creation

**URL Structure**:
- Orders list: `/dashboard/orders`
- Order details: `/dashboard/orders/{id}`
- Reports page (keep existing): `/dashboard/reports`
- Leases page (keep existing): `/dashboard/leases`

**Navigation Flow**:
```typescript
// After creating order
createOrder(formData, {
  onSuccess: (newOrder) => {
    router.push(`/dashboard/orders/${newOrder.id}`)
  }
})

// Back button on order details
<Button onClick={() => router.push('/dashboard/orders')}>
  <ArrowLeft /> Back to Orders
</Button>

// Clicking order row
<TableRow 
  className="cursor-pointer hover:bg-muted/50"
  onClick={() => router.push(`/dashboard/orders/${order.id}`)}
>
```

**Rationale**:
- **Clear Hierarchy**: Orders → Order Details → Reports (nested information)
- **Bookmarkable**: Each order has permanent URL for sharing
- **Intuitive**: Back button returns to list, forward navigation feels natural
- **Consistent**: Follows existing Next.js App Router patterns

---

## 9. Accessibility & Keyboard Navigation

### Decision: Full Keyboard Support for All Interactive Elements

**Required Keyboard Interactions**:
- **Tab**: Navigate between interactive elements
- **Enter/Space**: Activate buttons, toggle selections
- **Escape**: Close modals, cancel inline forms
- **Arrow Keys**: Navigate within lease selection dropdown
- **Backspace**: Remove selected lease chips when focused

**ARIA Labels**:
```typescript
// Lease search component
<input
  role="combobox"
  aria-label="Search and select leases"
  aria-expanded={open}
  aria-controls="lease-listbox"
/>

<ul role="listbox" id="lease-listbox" aria-label="Available leases">
  {filteredLeases.map(lease => (
    <li role="option" aria-selected={selected.includes(lease.id)}>
      {lease.lease_number}
    </li>
  ))}
</ul>
```

**Focus Management**:
- Opening modal: Focus first form field
- Closing modal: Return focus to trigger button
- Creating lease inline: Focus agency dropdown
- After successful creation: Focus back to lease search input

**Rationale**:
- **Legal Requirement**: WCAG AA compliance for web applications
- **Better UX**: Power users prefer keyboard navigation
- **Constitution**: Accessibility is implied in UI best practices

---

## 10. Error Handling & Loading States

### Decision: Granular Loading States with Error Recovery

**Loading States**:
```typescript
// Page-level loading (first load)
if (orderLoading || reportsLoading) {
  return <OrderDetailsSkeleton />
}

// Component-level loading (mutations)
<Button disabled={isCreating}>
  {isCreating ? 'Creating...' : 'Create Report'}
</Button>
```

**Error Display**:
```typescript
// Order not found
if (orderError?.response?.status === 404) {
  return (
    <EmptyState
      title="Order Not Found"
      description="This order may have been deleted."
      action={{ label: 'Back to Orders', href: '/dashboard/orders' }}
    />
  )
}

// Network errors
if (orderError) {
  return (
    <ErrorState
      title="Failed to Load Order"
      description={orderError.message}
      action={{ label: 'Retry', onClick: () => refetch() }}
    />
  )
}
```

**Toast Notifications** (existing pattern):
```typescript
// Success
toast.success('Report Created', {
  description: 'The report has been added to the order',
  duration: 5000,
})

// Error
toast.error('Creation Failed', {
  description: error?.message || 'Failed to create report',
})
```

**Rationale**:
- **User Confidence**: Clear feedback on what's happening
- **Error Recovery**: Users can retry without losing context
- **Consistency**: Matches existing toast notification patterns
- **Graceful Degradation**: Specific errors get specific messages

---

## 11. Performance Optimization

### Decision: Code Splitting & Lazy Loading for Components

**Lazy Load Pattern**:
```typescript
// Order details page
const ReportFormDialog = lazy(() => import('@/components/reports/ReportFormDialog'))
const InlineLeaseCreateForm = lazy(() => import('@/components/leases/InlineLeaseCreateForm'))

// Wrap in Suspense
<Suspense fallback={<LoadingSpinner />}>
  <ReportFormDialog {...props} />
</Suspense>
```

**Data Fetching Optimization**:
```typescript
// Prefetch on hover (optional enhancement)
<TableRow
  onMouseEnter={() => queryClient.prefetchQuery({
    queryKey: ['order', order.id],
    queryFn: () => getOrder(order.id)
  })}
  onClick={() => router.push(`/dashboard/orders/${order.id}`)}
>
```

**Lease Search Optimization**:
- Client-side filtering for <10K leases (acceptable per assumptions)
- Debounce search input by 300ms
- Virtual scrolling if lease list >100 items (react-window)

**Rationale**:
- **Initial Load**: Smaller bundle size, faster TTI
- **Perceived Performance**: Lazy load non-critical dialogs
- **Network Efficiency**: Prefetch reduces wait on navigation
- **Meets Success Criteria**: <2s page load, <300ms search

---

## Implementation Checklist

- [ ] Verify existing backend endpoints support required query parameters
- [ ] Create dynamic route `/app/dashboard/orders/[id]/page.tsx`
- [ ] Build OrderDetailsHeader component
- [ ] Build OrderReportsSection component with reports table
- [ ] Build ReportFormDialog component (create + edit modes)
- [ ] Enhance/create LeaseSearchSelect component with search
- [ ] Build InlineLeaseCreateForm component
- [ ] Add useOrderDetails hook
- [ ] Update useOrders hook to redirect after creation
- [ ] Add click handler to order rows for navigation
- [ ] Implement lease number inline display in reports table
- [ ] Add accessibility labels and keyboard navigation
- [ ] Test error states (404, network errors)
- [ ] Verify performance targets (<2s load, <300ms search)
- [ ] Test with multiple leases (1, 5, 20+)
- [ ] Validate mobile responsiveness

---

## References

- **Next.js App Router**: https://nextjs.org/docs/app
- **shadcn/ui Components**: https://ui.shadcn.com/docs/components
- **TanStack Query**: https://tanstack.com/query/latest/docs/framework/react/overview
- **React Aria**: https://react-spectrum.adobe.com/react-aria/ (for accessibility patterns)
- **Existing Codebase**: 
  - `/frontend/src/hooks/useOrders.ts`
  - `/frontend/src/hooks/useReports.ts`
  - `/frontend/src/hooks/useLeases.ts`
  - `/frontend/src/components/ui/multi-select.tsx`
  - `/frontend/src/app/dashboard/orders/page.tsx`
  - `/frontend/src/app/dashboard/reports/page.tsx`

---

**Research Complete**: October 26, 2025  
**All technical decisions documented with rationale and alternatives considered**

