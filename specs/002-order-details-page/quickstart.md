# Quickstart: Order Details Page Enhancement

**Feature**: 002-order-details-page  
**Created**: October 26, 2025  
**Purpose**: Step-by-step implementation guide for developers

---

## Prerequisites

Before starting, ensure you have:

- [x] Development environment running (`docker-compose up`)
- [x] Frontend dev server running (`npm run dev` in `/frontend/`)
- [x] Read [spec.md](./spec.md), [research.md](./research.md), and [data-model.md](./data-model.md)
- [x] Reviewed [contracts/api-spec.md](./contracts/api-spec.md)
- [x] Verified existing API endpoints work (use curl or Postman)

**Estimated Time**: 8-12 hours for full implementation

---

## Implementation Phases

### Phase 1: Backend Verification (30 mins)

Verify existing endpoints support required functionality.

#### 1.1 Test Single Order Endpoint

```bash
# Get your access token (login first if needed)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Test get single order
curl http://localhost:8000/api/orders/1/ \
  -H "Cookie: access_token=YOUR_TOKEN"
```

**Expected**: 200 OK with order JSON  
**If 404/not found**: Create a test order first

#### 1.2 Test Reports Filter by Order

```bash
curl http://localhost:8000/api/reports/?order_id=1 \
  -H "Cookie: access_token=YOUR_TOKEN"
```

**Expected**: 200 OK with filtered reports  
**If filter doesn't work**: Add `order_id` query parameter support to `/web/api/views/reports.py`

```python
# In ReportViewSet.get_queryset()
order_id = self.request.query_params.get('order_id')
if order_id:
    queryset = queryset.filter(order_id=order_id)
```

#### 1.3 Test Lease Search

```bash
curl "http://localhost:8000/api/leases/?search=NMNM" \
  -H "Cookie: access_token=YOUR_TOKEN"
```

**Expected**: 200 OK with filtered leases  
**If search doesn't work**: Add `search` parameter support to `/web/api/views/leases.py`

```python
# In LeaseViewSet.get_queryset()
from django.db.models import Q

search = self.request.query_params.get('search')
if search:
    queryset = queryset.filter(
        Q(lease_number__icontains=search) |
        Q(agency__icontains=search)
    )
```

#### 1.4 Verify Report Response Includes Leases

Check if `/api/reports/` includes full `leases` array in response:

```bash
curl http://localhost:8000/api/reports/1/ \
  -H "Cookie: access_token=YOUR_TOKEN"
```

**Expected**: Response should include `"leases": [...]` array  
**If missing**: Update serializer in `/web/api/serializers/reports.py`

```python
from .leases import LeaseSerializer

class ReportSerializer(serializers.ModelSerializer):
    leases = LeaseSerializer(many=True, read_only=True)
    lease_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Lease.objects.all(), source='leases', write_only=True
    )
    # ... rest of serializer
```

---

### Phase 2: Frontend API Functions (1 hour)

Add API client functions for new data fetching patterns.

#### 2.1 Add getOrder Function

File: `/frontend/src/lib/api/orders.ts`

```typescript
// Add to existing file
export async function getOrder(id: number): Promise<Order> {
  const response = await api.get(`/api/orders/${id}/`);
  return response.data;
}
```

#### 2.2 Add searchLeases Function (if needed)

File: `/frontend/src/lib/api/leases.ts`

```typescript
// Add to existing file
export async function searchLeases(searchTerm: string): Promise<Lease[]> {
  const response = await api.get('/api/leases/', {
    params: {
      search: searchTerm,
      page_size: 1000, // Get all matching leases
    },
  });
  return response.data.results;
}
```

---

### Phase 3: Custom Hooks (1 hour)

Create hooks for order details data fetching.

#### 3.1 Add useOrderDetails Hook

File: `/frontend/src/hooks/useOrderDetails.ts` (NEW FILE)

```typescript
import { getOrder } from '@/lib/api/orders';
import { Order } from '@/lib/api/types';
import { useQuery } from '@tanstack/react-query';

export function useOrderDetails(orderId: number) {
  return useQuery<Order>({
    queryKey: ['order', orderId],
    queryFn: () => getOrder(orderId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!orderId, // Only fetch if orderId is provided
  });
}
```

#### 3.2 Update useOrders Hook for Redirect

File: `/frontend/src/hooks/useOrders.ts`

Update the `createMutation` success callback to accept custom onSuccess:

```typescript
const createMutation = useMutation({
  mutationFn: (data: OrderFormData) => createOrder(data),
  onSuccess: (newOrder, variables, context) => {
    queryClient.invalidateQueries({ queryKey: ['orders'] });
    toast.success('Order Created', {
      description: 'The order has been created successfully',
      duration: 5000,
    });
    // Custom onSuccess callback will be called by caller
  },
  // ... rest of mutation
});

// Return mutation with ability to pass onSuccess
return {
  // ... existing returns
  createOrder: (data: OrderFormData, options?: { onSuccess?: (order: Order) => void }) => {
    createMutation.mutate(data, options);
  },
};
```

---

### Phase 4: UI Components (4-6 hours)

Build reusable components following the research patterns.

#### 4.1 Create OrderDetailsHeader Component

File: `/frontend/src/components/orders/OrderDetailsHeader.tsx` (NEW FILE)

```typescript
'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Order } from '@/lib/api/types';
import { format } from 'date-fns';
import { ArrowLeft, Edit, ExternalLink, Trash2 } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface OrderDetailsHeaderProps {
  order: Order;
  onEdit: () => void;
  onDelete: () => void;
}

export function OrderDetailsHeader({ order, onEdit, onDelete }: OrderDetailsHeaderProps) {
  const router = useRouter();

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/dashboard/orders')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Orders
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Order {order.order_number}</h1>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onEdit}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="destructive" onClick={onDelete}>
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Order Date</p>
            <p className="font-medium">{format(new Date(order.order_date), 'PPP')}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Created</p>
            <p className="font-medium">
              {format(new Date(order.created_at), 'PPP')}
              {order.created_by_username && ` by ${order.created_by_username}`}
            </p>
          </div>
          {order.order_notes && (
            <div className="col-span-2">
              <p className="text-sm text-muted-foreground">Notes</p>
              <p className="font-medium">{order.order_notes}</p>
            </div>
          )}
          {order.delivery_link && (
            <div className="col-span-2">
              <p className="text-sm text-muted-foreground">Delivery Link</p>
              <a
                href={order.delivery_link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline inline-flex items-center gap-1"
              >
                {order.delivery_link}
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

#### 4.2 Create OrderReportsSection Component

File: `/frontend/src/components/orders/OrderReportsSection.tsx` (NEW FILE)

```typescript
'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Report, REPORT_TYPE_LABELS, ReportType } from '@/lib/api/types';
import { format } from 'date-fns';
import { Edit, Plus, Trash2 } from 'lucide-react';

interface OrderReportsSectionProps {
  reports: Report[];
  isLoading: boolean;
  onAddReport: () => void;
  onEditReport: (report: Report) => void;
  onDeleteReport: (report: Report) => void;
}

export function OrderReportsSection({
  reports,
  isLoading,
  onAddReport,
  onEditReport,
  onDeleteReport,
}: OrderReportsSectionProps) {
  if (isLoading) {
    return <div className="text-center py-8">Loading reports...</div>;
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Reports ({reports.length})</CardTitle>
        <Button onClick={onAddReport}>
          <Plus className="h-4 w-4 mr-2" />
          Add Report
        </Button>
      </CardHeader>
      <CardContent>
        {reports.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground mb-4">No reports added yet</p>
            <Button onClick={onAddReport} variant="outline">
              <Plus className="h-4 w-4 mr-2" />
              Create your first report
            </Button>
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Legal Description</TableHead>
                  <TableHead>Date Range</TableHead>
                  <TableHead>Leases</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reports.map((report) => (
                  <TableRow key={report.id}>
                    <TableCell className="font-medium">
                      {REPORT_TYPE_LABELS[report.report_type as ReportType]}
                    </TableCell>
                    <TableCell
                      className="max-w-xs truncate"
                      title={report.legal_description}
                    >
                      {report.legal_description}
                    </TableCell>
                    <TableCell>
                      {report.start_date || report.end_date ? (
                        <>
                          {report.start_date ? format(new Date(report.start_date), 'PP') : '-'}
                          {' to '}
                          {report.end_date ? format(new Date(report.end_date), 'PP') : '-'}
                        </>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {report.leases.slice(0, 5).map((lease) => (
                          <span
                            key={lease.id}
                            className="text-primary hover:underline cursor-pointer"
                          >
                            {lease.lease_number}
                          </span>
                        ))}
                        {report.leases.length > 5 && (
                          <span className="text-muted-foreground">
                            +{report.leases.length - 5} more
                          </span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onEditReport(report)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onDeleteReport(report)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

#### 4.3 Create LeaseSearchSelect Component

See [research.md](./research.md) section 3 for detailed implementation.

File: `/frontend/src/components/leases/LeaseSearchSelect.tsx` (NEW FILE)

**Implementation tip**: Base this on existing `/components/ui/multi-select.tsx` and enhance with:
- Real-time search filtering
- Debounced input (300ms)
- Selected items as chips
- "Create New Lease" button at bottom

#### 4.4 Create InlineLeaseCreateForm Component

File: `/frontend/src/components/leases/InlineLeaseCreateForm.tsx` (NEW FILE)

```typescript
'use client';

import { Button } from '@/components/ui/button';
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useLeases } from '@/hooks/useLeases';
import { AgencyType, Lease, LeaseFormData } from '@/lib/api/types';
import { useState } from 'react';

interface InlineLeaseCreateFormProps {
  onSuccess: (lease: Lease) => void;
  onCancel: () => void;
}

export function InlineLeaseCreateForm({ onSuccess, onCancel }: InlineLeaseCreateFormProps) {
  const { createLease, isCreating } = useLeases();
  const [formData, setFormData] = useState<LeaseFormData>({
    agency: 'BLM',
    lease_number: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createLease(formData, {
      onSuccess: (newLease) => {
        onSuccess(newLease);
      },
    });
  };

  return (
    <form onSubmit={handleSubmit} className="border rounded-lg p-4 bg-muted/50">
      <h4 className="font-medium mb-3">Create New Lease</h4>
      <FieldGroup>
        <Field>
          <FieldLabel>Agency</FieldLabel>
          <Select
            value={formData.agency}
            onValueChange={(value: AgencyType) =>
              setFormData({ ...formData, agency: value })
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="BLM">BLM</SelectItem>
              <SelectItem value="NMSLO">NMSLO</SelectItem>
            </SelectContent>
          </Select>
        </Field>
        <Field>
          <FieldLabel>Lease Number</FieldLabel>
          <Input
            value={formData.lease_number}
            onChange={(e) =>
              setFormData({ ...formData, lease_number: e.target.value })
            }
            placeholder="e.g., NMNM 12345"
            required
          />
        </Field>
      </FieldGroup>
      <div className="flex justify-end gap-2 mt-4">
        <Button type="button" variant="outline" onClick={onCancel} disabled={isCreating}>
          Cancel
        </Button>
        <Button type="submit" disabled={isCreating}>
          {isCreating ? 'Creating...' : 'Create Lease'}
        </Button>
      </div>
    </form>
  );
}
```

#### 4.5 Create ReportFormDialog Component

File: `/frontend/src/components/reports/ReportFormDialog.tsx` (NEW FILE)

This component combines LeaseSearchSelect and InlineLeaseCreateForm.  
**Implementation tip**: See existing `/app/dashboard/reports/page.tsx` for report form pattern, then adapt to use enhanced lease selection.

---

### Phase 5: Order Details Page (2 hours)

Create the main order details page.

#### 5.1 Create Dynamic Route Directory

```bash
mkdir -p /frontend/src/app/dashboard/orders/[id]
```

#### 5.2 Create Order Details Page

File: `/frontend/src/app/dashboard/orders/[id]/page.tsx` (NEW FILE)

```typescript
'use client';

import { OrderDetailsHeader } from '@/components/orders/OrderDetailsHeader';
import { OrderReportsSection } from '@/components/orders/OrderReportsSection';
import { ReportFormDialog } from '@/components/reports/ReportFormDialog';
import { useOrderDetails } from '@/hooks/useOrderDetails';
import { useOrders } from '@/hooks/useOrders';
import { useReports } from '@/hooks/useReports';
import { Report } from '@/lib/api/types';
import { use, useState } from 'react';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function OrderDetailsPage({ params }: PageProps) {
  const { id } = use(params);
  const orderId = parseInt(id);

  const { data: order, isLoading: orderLoading } = useOrderDetails(orderId);
  const { reports, isLoading: reportsLoading } = useReports(1, 100, orderId);
  const { deleteOrder } = useOrders();

  const [reportDialogOpen, setReportDialogOpen] = useState(false);
  const [editingReport, setEditingReport] = useState<Report | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  if (orderLoading || reportsLoading) {
    return <div className="container mx-auto p-6">Loading...</div>;
  }

  if (!order) {
    return (
      <div className="container mx-auto p-6">
        <h1>Order Not Found</h1>
        <p>This order may have been deleted.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <OrderDetailsHeader
        order={order}
        onEdit={() => {
          // Open edit order dialog (reuse existing from orders list page)
        }}
        onDelete={() => {
          if (order.report_count > 0) {
            alert(`Cannot delete order with ${order.report_count} reports`);
          } else {
            setDeleteDialogOpen(true);
          }
        }}
      />

      <OrderReportsSection
        reports={reports}
        isLoading={reportsLoading}
        onAddReport={() => {
          setEditingReport(null);
          setReportDialogOpen(true);
        }}
        onEditReport={(report) => {
          setEditingReport(report);
          setReportDialogOpen(true);
        }}
        onDeleteReport={(report) => {
          // Open delete confirmation dialog
        }}
      />

      <ReportFormDialog
        open={reportDialogOpen}
        onOpenChange={setReportDialogOpen}
        orderId={orderId}
        report={editingReport}
        mode={editingReport ? 'edit' : 'create'}
      />
    </div>
  );
}
```

---

### Phase 6: Navigation Integration (30 mins)

Update orders list page to navigate to order details.

#### 6.1 Update Orders List Page

File: `/frontend/src/app/dashboard/orders/page.tsx`

Add click handler to table rows:

```typescript
import { useRouter } from 'next/navigation';

export default function OrdersPage() {
  const router = useRouter();
  
  // ... existing code ...
  
  return (
    // ... existing JSX ...
    <TableBody>
      {orders.map((order) => (
        <TableRow 
          key={order.id}
          className="cursor-pointer hover:bg-muted/50"
          onClick={() => router.push(`/dashboard/orders/${order.id}`)}
        >
          {/* existing cells */}
        </TableRow>
      ))}
    </TableBody>
  );
}
```

#### 6.2 Update Order Creation to Redirect

In the same file, update create success callback:

```typescript
const handleCreateSubmit = (e: React.FormEvent) => {
  e.preventDefault();
  createOrder(formData, {
    onSuccess: (newOrder) => {
      router.push(`/dashboard/orders/${newOrder.id}`);
      setCreateDialogOpen(false);
    },
  });
};
```

---

## Testing Checklist

### Manual Testing

- [ ] Navigate to orders list
- [ ] Click on an order → lands on order details page
- [ ] See order information displayed correctly
- [ ] See reports table (or empty state)
- [ ] Click "Add Report" → dialog opens
- [ ] Fill report form → select existing leases
- [ ] Submit → report appears in table
- [ ] Click lease number in table → see lease details
- [ ] Click "Create New Lease" in report form → inline form appears
- [ ] Create new lease → automatically selected in report
- [ ] Submit report with new lease → works
- [ ] Click edit on report → pre-filled form appears
- [ ] Modify report → changes saved
- [ ] Click delete on report → confirmation dialog
- [ ] Confirm delete → report removed
- [ ] Click "Edit Order Details" → modal opens
- [ ] Update order info → changes reflected
- [ ] Click "Delete Order" with reports → warning shown
- [ ] Delete all reports → delete order succeeds
- [ ] Test error cases (network error, validation error)
- [ ] Test with mobile viewport
- [ ] Test keyboard navigation (Tab, Enter, Escape)

### Performance Testing

- [ ] Order details page loads in <2 seconds
- [ ] Lease search filters in <300ms
- [ ] Creating report feels instant (optimistic update)
- [ ] No console errors or warnings

---

## Troubleshooting

### Issue: "Order not found"

**Cause**: Order doesn't exist or user not authenticated  
**Fix**: Create test order or check authentication

### Issue: Reports not loading

**Cause**: `order_id` filter not working  
**Fix**: Verify backend endpoint supports `?order_id=` parameter

### Issue: Lease search not working

**Cause**: `search` parameter not implemented  
**Fix**: Add search filter to backend (see Phase 1.3)

### Issue: "Cannot read property of undefined"

**Cause**: Missing null checks in components  
**Fix**: Add optional chaining (`order?.field`) and loading states

---

## Next Steps

After completing this feature:

1. Create pull request with implementation
2. Request code review focusing on:
   - Constitution compliance
   - Component reusability
   - Error handling completeness
   - Accessibility (ARIA labels, keyboard nav)
3. Address review feedback
4. Merge to main branch
5. Deploy to production

---

## Additional Resources

- [spec.md](./spec.md) - Feature requirements
- [research.md](./research.md) - Technical decisions
- [data-model.md](./data-model.md) - Entity relationships
- [contracts/api-spec.md](./contracts/api-spec.md) - API documentation
- Next.js App Router: https://nextjs.org/docs/app
- shadcn/ui Components: https://ui.shadcn.com
- TanStack Query: https://tanstack.com/query/latest

---

**Quickstart Complete** - You now have a complete implementation guide. Follow the phases sequentially for best results!

