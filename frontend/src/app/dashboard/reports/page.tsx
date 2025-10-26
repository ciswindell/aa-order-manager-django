'use client';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { MultiSelect } from '@/components/ui/multi-select';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '@/hooks/useAuth';
import { useLeases } from '@/hooks/useLeases';
import { useOrders } from '@/hooks/useOrders';
import { useReports } from '@/hooks/useReports';
import { REPORT_TYPE_LABELS, ReportFormData, ReportType } from '@/lib/api/types';
import { format } from 'date-fns';
import { ChevronLeft, ChevronRight, Edit, ExternalLink, Plus, Trash2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useMemo, useState } from 'react';

const REPORT_TYPES: ReportType[] = [
  'RUNSHEET',
  'BASE_ABSTRACT',
  'SUPPLEMENTAL_ABSTRACT',
  'DOL_ABSTRACT',
];

export default function ReportsPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [selectedOrderId, setSelectedOrderId] = useState<number | undefined>(undefined);
  const pageSize = 20;

  const { orders: allOrders } = useOrders(1, 100);
  const { leases: allLeases } = useLeases(1, 10000);

  const leaseOptions = useMemo(() => 
    allLeases.map(lease => ({
      label: `${lease.agency} - ${lease.lease_number}`,
      value: lease.id,
    })),
    [allLeases]
  );

  const {
    reports,
    totalCount,
    isLoading,
    createReport,
    updateReport,
    deleteReport,
    isCreating,
    isUpdating,
    isDeleting,
  } = useReports(page, pageSize, selectedOrderId);

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState<any>(null);

  const [formData, setFormData] = useState<ReportFormData>({
    order_id: 0,
    report_type: 'RUNSHEET',
    legal_description: '',
    start_date: '',
    end_date: '',
    report_notes: '',
    lease_ids: [],
  });

  const totalPages = Math.ceil(totalCount / pageSize);

  const handleCreateClick = () => {
    setFormData({
      order_id: allOrders[0]?.id || 0,
      report_type: 'RUNSHEET',
      legal_description: '',
      start_date: '',
      end_date: '',
      report_notes: '',
      lease_ids: [],
    });
    setCreateDialogOpen(true);
  };

  const handleEditClick = (report: any) => {
    setSelectedReport(report);
    setFormData({
      order_id: report.order.id,
      report_type: report.report_type,
      legal_description: report.legal_description,
      start_date: report.start_date || '',
      end_date: report.end_date || '',
      report_notes: report.report_notes || '',
      lease_ids: report.lease_ids || [],
    });
    setEditDialogOpen(true);
  };

  const handleDeleteClick = (report: any) => {
    setSelectedReport(report);
    setDeleteDialogOpen(true);
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanedData = {
      ...formData,
      start_date: formData.start_date || undefined,
      end_date: formData.end_date || undefined,
      report_notes: formData.report_notes || undefined,
      lease_ids: formData.lease_ids || [],
    };
    createReport(cleanedData, {
      onSuccess: () => {
        setCreateDialogOpen(false);
      },
    });
  };

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedReport) {
      const cleanedData = {
        ...formData,
        start_date: formData.start_date || undefined,
        end_date: formData.end_date || undefined,
        report_notes: formData.report_notes || undefined,
        lease_ids: formData.lease_ids || [],
      };
      updateReport(
        { id: selectedReport.id, data: cleanedData },
        {
          onSuccess: () => {
            setEditDialogOpen(false);
            setSelectedReport(null);
          },
        }
      );
    }
  };

  const handleDeleteConfirm = () => {
    if (selectedReport) {
      deleteReport(selectedReport.id, {
        onSuccess: () => {
          setDeleteDialogOpen(false);
          setSelectedReport(null);
        },
      });
    }
  };

  const handleLeaseCountClick = (reportId: number) => {
    router.push(`/dashboard/leases?report_id=${reportId}`);
  };

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reports</h1>
          <p className="text-muted-foreground">Manage your reports</p>
        </div>
        <div className="flex gap-2">
          <Select
            value={selectedOrderId?.toString() || 'all'}
            onValueChange={(value: string) => {
              if (value === 'all') {
                setSelectedOrderId(undefined);
              } else {
                setSelectedOrderId(Number(value));
              }
              setPage(1);
            }}
          >
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Filter by Order" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Orders</SelectItem>
              {allOrders.map((order) => (
                <SelectItem key={order.id} value={order.id.toString()}>
                  {order.order_number}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button onClick={handleCreateClick}>
            <Plus className="mr-2 h-4 w-4" />
            Create Report
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <p className="text-muted-foreground">Loading reports...</p>
        </div>
      ) : reports.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-muted-foreground mb-4">
            {selectedOrderId ? 'No reports found for selected order' : 'No reports found'}
          </p>
          <Button onClick={handleCreateClick} variant="outline">
            <Plus className="mr-2 h-4 w-4" />
            Create your first report
          </Button>
        </div>
      ) : (
        <>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Order Number</TableHead>
                  <TableHead>Report Type</TableHead>
                  <TableHead>Legal Description</TableHead>
                  <TableHead>Date Range</TableHead>
                  <TableHead>Leases</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reports.map((report) => (
                  <TableRow key={report.id}>
                    <TableCell className="font-medium">{report.order.order_number}</TableCell>
                    <TableCell>{REPORT_TYPE_LABELS[report.report_type as ReportType] || report.report_type}</TableCell>
                    <TableCell className="max-w-xs truncate" title={report.legal_description}>
                      {report.legal_description}
                    </TableCell>
                    <TableCell>
                      {report.start_date || report.end_date ? (
                        <>
                          {report.start_date ? format(new Date(report.start_date), 'PP') : '-'} 
                          {' to '}
                          {report.end_date ? format(new Date(report.end_date), 'PP') : '-'}
                        </>
                      ) : '-'}
                    </TableCell>
                    <TableCell>
                      {report.lease_count > 0 ? (
                        <button
                          onClick={() => handleLeaseCountClick(report.id)}
                          className="text-primary hover:underline flex items-center gap-1"
                        >
                          {report.lease_count}
                          <ExternalLink className="h-3 w-3" />
                        </button>
                      ) : (
                        <span className="text-muted-foreground">0</span>
                      )}
                    </TableCell>
                    <TableCell>{format(new Date(report.created_at), 'PP')}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="sm" onClick={() => handleEditClick(report)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteClick(report)}
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

          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                Page {page} of {totalPages} ({totalCount} total reports)
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={page === totalPages}
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Create Report Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="max-w-2xl">
          <form onSubmit={handleCreateSubmit}>
            <DialogHeader>
              <DialogTitle>Create Report</DialogTitle>
              <DialogDescription>Add a new report to the system</DialogDescription>
            </DialogHeader>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="order_id">Order</FieldLabel>
                <Select
                  value={formData.order_id.toString()}
                  onValueChange={(value: string) => setFormData({ ...formData, order_id: Number(value) })}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select order" />
                  </SelectTrigger>
                  <SelectContent>
                    {allOrders.map((order) => (
                      <SelectItem key={order.id} value={order.id.toString()}>
                        {order.order_number}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>
              <Field>
                <FieldLabel htmlFor="report_type">Report Type</FieldLabel>
                <Select
                  value={formData.report_type}
                  onValueChange={(value: string) => setFormData({ ...formData, report_type: value })}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select report type" />
                  </SelectTrigger>
                  <SelectContent>
                    {REPORT_TYPES.map((type) => (
                      <SelectItem key={type} value={type}>
                        {REPORT_TYPE_LABELS[type]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>
              <Field>
                <FieldLabel htmlFor="legal_description">Legal Description</FieldLabel>
                <Textarea
                  id="legal_description"
                  value={formData.legal_description}
                  onChange={(e) =>
                    setFormData({ ...formData, legal_description: e.target.value })
                  }
                  placeholder="Enter legal description..."
                  required
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="start_date">Start Date (Optional)</FieldLabel>
                <Input
                  id="start_date"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="end_date">End Date (Optional)</FieldLabel>
                <Input
                  id="end_date"
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="report_notes">Notes (Optional)</FieldLabel>
                <Textarea
                  id="report_notes"
                  value={formData.report_notes}
                  onChange={(e) => setFormData({ ...formData, report_notes: e.target.value })}
                  placeholder="Enter any notes..."
                />
              </Field>
              <Field>
                <FieldLabel>Leases *</FieldLabel>
                <MultiSelect
                  options={leaseOptions}
                  selected={formData.lease_ids || []}
                  onChange={(selected) => setFormData({ ...formData, lease_ids: selected as number[] })}
                  placeholder="Select at least one lease..."
                  emptyText="No leases found."
                />
              </Field>
            </FieldGroup>
            <DialogFooter className="mt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setCreateDialogOpen(false)}
                disabled={isCreating}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isCreating}>
                {isCreating ? 'Creating...' : 'Create Report'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Report Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <form onSubmit={handleEditSubmit}>
            <DialogHeader>
              <DialogTitle>Edit Report</DialogTitle>
              <DialogDescription>Update report details</DialogDescription>
            </DialogHeader>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="edit_order_id">Order</FieldLabel>
                <Select
                  value={formData.order_id.toString()}
                  onValueChange={(value: string) => setFormData({ ...formData, order_id: Number(value) })}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select order" />
                  </SelectTrigger>
                  <SelectContent>
                    {allOrders.map((order) => (
                      <SelectItem key={order.id} value={order.id.toString()}>
                        {order.order_number}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>
              <Field>
                <FieldLabel htmlFor="edit_report_type">Report Type</FieldLabel>
                <Select
                  value={formData.report_type}
                  onValueChange={(value: string) => setFormData({ ...formData, report_type: value })}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select report type" />
                  </SelectTrigger>
                  <SelectContent>
                    {REPORT_TYPES.map((type) => (
                      <SelectItem key={type} value={type}>
                        {REPORT_TYPE_LABELS[type]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>
              <Field>
                <FieldLabel htmlFor="edit_legal_description">Legal Description</FieldLabel>
                <Textarea
                  id="edit_legal_description"
                  value={formData.legal_description}
                  onChange={(e) =>
                    setFormData({ ...formData, legal_description: e.target.value })
                  }
                  placeholder="Enter legal description..."
                  required
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="edit_start_date">Start Date (Optional)</FieldLabel>
                <Input
                  id="edit_start_date"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="edit_end_date">End Date (Optional)</FieldLabel>
                <Input
                  id="edit_end_date"
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="edit_report_notes">Notes (Optional)</FieldLabel>
                <Textarea
                  id="edit_report_notes"
                  value={formData.report_notes}
                  onChange={(e) => setFormData({ ...formData, report_notes: e.target.value })}
                  placeholder="Enter any notes..."
                />
              </Field>
              <Field>
                <FieldLabel>Leases *</FieldLabel>
                <MultiSelect
                  options={leaseOptions}
                  selected={formData.lease_ids || []}
                  onChange={(selected) => setFormData({ ...formData, lease_ids: selected as number[] })}
                  placeholder="Select at least one lease..."
                  emptyText="No leases found."
                />
              </Field>
            </FieldGroup>
            <DialogFooter className="mt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setEditDialogOpen(false)}
                disabled={isUpdating}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isUpdating}>
                {isUpdating ? 'Updating...' : 'Update Report'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Report?</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this report? This action cannot be undone.
              {selectedReport?.lease_count > 0 && (
                <span className="block mt-2 text-destructive">
                  This report has {selectedReport.lease_count} associated lease(s). You must delete
                  them first.
                </span>
              )}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteConfirm} disabled={isDeleting}>
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

