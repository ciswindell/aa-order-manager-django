'use client';

import { OrderDetailsHeader } from '@/components/orders/OrderDetailsHeader';
import { OrderReportsSection } from '@/components/orders/OrderReportsSection';
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
import { useLeases } from '@/hooks/useLeases';
import { useOrderDetails } from '@/hooks/useOrderDetails';
import { useOrders } from '@/hooks/useOrders';
import { useReports } from '@/hooks/useReports';
import { OrderFormData, Report, ReportFormData } from '@/lib/api/types';
import { triggerWorkflow } from '@/lib/api/workflows';
import { useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Edit, Send, Trash2 } from 'lucide-react';
import dynamic from 'next/dynamic';
import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import { toast } from 'sonner';

const ReportFormDialog = dynamic(
  () => import('@/components/reports/ReportFormDialog').then((mod) => ({ default: mod.ReportFormDialog })),
  { ssr: false }
);

export default function OrderDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const orderId = Number(params.id);

  const { orderDetails, isLoading: isLoadingOrder, isError, error } = useOrderDetails(orderId);
  const { reports, isLoading: isLoadingReports, createReport, updateReport, deleteReport, isCreating, isUpdating: isUpdatingReport, isDeleting: isDeletingReport } = useReports(1, 100, orderId);
  const { updateOrder, deleteOrder, isUpdating, isDeleting } = useOrders();
  const { leases } = useLeases(1, 10000);

  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [reportDialogOpen, setReportDialogOpen] = useState(false);
  const [reportDialogMode, setReportDialogMode] = useState<'create' | 'edit'>('create');
  const [editingReportId, setEditingReportId] = useState<number | null>(null);
  const [deleteReportDialogOpen, setDeleteReportDialogOpen] = useState(false);
  const [reportToDelete, setReportToDelete] = useState<number | null>(null);
  const [isCreatingWorkflow, setIsCreatingWorkflow] = useState(false);
  
  const [formData, setFormData] = useState<OrderFormData>({
    order_number: '',
    order_date: '',
    order_notes: '',
    delivery_link: '',
  });

  const [reportFormData, setReportFormData] = useState<ReportFormData>({
    order_id: orderId,
    report_type: 'RUNSHEET',
    legal_description: '',
    start_date: '',
    end_date: '',
    report_notes: '',
    lease_ids: [],
  });

  const handleEditClick = () => {
    if (orderDetails) {
      setFormData({
        order_number: orderDetails.order_number,
        order_date: orderDetails.order_date,
        order_notes: orderDetails.order_notes || '',
        delivery_link: orderDetails.delivery_link || '',
      });
      setEditDialogOpen(true);
    }
  };

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateOrder(
      { id: orderId, data: formData },
      {
        onSuccess: () => {
          setEditDialogOpen(false);
          // Invalidate the order details query to refetch updated data
          queryClient.invalidateQueries({ queryKey: ['order', orderId] });
        },
      }
    );
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    deleteOrder(orderId, {
      onSuccess: () => {
        router.push('/dashboard/orders');
      },
    });
  };

  const handleAddReportClick = () => {
    setReportFormData({
      order_id: orderId,
      report_type: 'RUNSHEET',
      legal_description: '',
      start_date: '',
      end_date: '',
      report_notes: '',
      lease_ids: [],
    });
    setReportDialogMode('create');
    setEditingReportId(null);
    setReportDialogOpen(true);
  };

  const handleReportSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanedData = {
      ...reportFormData,
      start_date: reportFormData.start_date || undefined,
      end_date: reportFormData.end_date || undefined,
      report_notes: reportFormData.report_notes || undefined,
      lease_ids: reportFormData.lease_ids || [],
    };
    
    if (reportDialogMode === 'create') {
      createReport(cleanedData, {
        onSuccess: () => {
          setReportDialogOpen(false);
          queryClient.invalidateQueries({ queryKey: ['reports'] });
        },
      });
    } else if (reportDialogMode === 'edit' && editingReportId) {
      updateReport(
        { id: editingReportId, data: cleanedData },
        {
          onSuccess: () => {
            setReportDialogOpen(false);
            queryClient.invalidateQueries({ queryKey: ['reports'] });
            setEditingReportId(null);
          },
        }
      );
    }
  };

  const handleEditReport = (report: Report) => {
    setReportFormData({
      order_id: orderId,
      report_type: report.report_type,
      legal_description: report.legal_description,
      start_date: report.start_date || '',
      end_date: report.end_date || '',
      report_notes: report.report_notes || '',
      lease_ids: report.leases?.map((l) => l.id) || [],
    });
    setReportDialogMode('edit');
    setEditingReportId(report.id);
    setReportDialogOpen(true);
  };

  const handleDeleteReport = (report: Report) => {
    setReportToDelete(report.id);
    setDeleteReportDialogOpen(true);
  };

  const handleDeleteReportConfirm = () => {
    if (reportToDelete) {
      deleteReport(reportToDelete, {
        onSuccess: () => {
          setDeleteReportDialogOpen(false);
          setReportToDelete(null);
          queryClient.invalidateQueries({ queryKey: ['reports'] });
          queryClient.invalidateQueries({ queryKey: ['order', orderId] });
        },
      });
    }
  };

  const handlePushToBasecamp = async () => {
    setIsCreatingWorkflow(true);
    try {
      const result = await triggerWorkflow(orderId);
      
      if (result.success) {
        toast.success(result.message, {
          description: result.workflows_created.length > 0 
            ? `Created workflows in: ${result.workflows_created.join(', ')}`
            : undefined,
          duration: 5000,
        });
        
        if (result.failed_products && result.failed_products.length > 0) {
          toast.warning(`Some workflows failed`, {
            description: `Failed: ${result.failed_products.join(', ')}`,
            duration: 5000,
          });
        }
      } else {
        toast.warning(result.message);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || 'Failed to create workflows';
      toast.error('Workflow creation failed', {
        description: errorMessage,
        duration: 5000,
      });
    } finally {
      setIsCreatingWorkflow(false);
    }
  };

  if (isLoadingOrder) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading order details...</p>
      </div>
    );
  }

  if (isError || !orderDetails) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4">
        <p className="text-destructive">
          {error?.message || 'Failed to load order details'}
        </p>
        <Button onClick={() => router.push('/dashboard/orders')} variant="outline">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Orders
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <Button
            variant="ghost"
            onClick={() => router.push('/dashboard/orders')}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Orders
          </Button>
          <div className="flex gap-2">
            <Button
              variant="default"
              onClick={handlePushToBasecamp}
              disabled={isCreatingWorkflow}
            >
              <Send className="mr-2 h-4 w-4" />
              {isCreatingWorkflow ? 'Creating...' : 'Push to Basecamp'}
            </Button>
            <Button
              variant="outline"
              onClick={handleEditClick}
            >
              <Edit className="mr-2 h-4 w-4" />
              Edit Order
            </Button>
            <Button
              variant="outline"
              onClick={handleDeleteClick}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete Order
            </Button>
          </div>
        </div>

        <OrderDetailsHeader order={orderDetails} />
      </div>

      <div className="border-t pt-6">
        <OrderReportsSection 
          reports={reports} 
          isLoading={isLoadingReports} 
          onAddReport={handleAddReportClick}
          onEditReport={handleEditReport}
          onDeleteReport={handleDeleteReport}
        />
      </div>

      {/* Edit Order Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <form onSubmit={handleEditSubmit}>
            <DialogHeader>
              <DialogTitle>Edit Order</DialogTitle>
              <DialogDescription>Update order details</DialogDescription>
            </DialogHeader>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="edit_order_number">Order Number</FieldLabel>
                <Input
                  id="edit_order_number"
                  value={formData.order_number}
                  onChange={(e) => setFormData({ ...formData, order_number: e.target.value })}
                  required
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="edit_order_date">Order Date</FieldLabel>
                <Input
                  id="edit_order_date"
                  type="date"
                  value={formData.order_date}
                  onChange={(e) => setFormData({ ...formData, order_date: e.target.value })}
                  required
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="edit_delivery_link">Delivery Link (Optional)</FieldLabel>
                <Input
                  id="edit_delivery_link"
                  type="url"
                  value={formData.delivery_link}
                  onChange={(e) => setFormData({ ...formData, delivery_link: e.target.value })}
                  placeholder="https://..."
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="edit_order_notes">Order Notes (Optional)</FieldLabel>
                <Input
                  id="edit_order_notes"
                  value={formData.order_notes}
                  onChange={(e) => setFormData({ ...formData, order_notes: e.target.value })}
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
                {isUpdating ? 'Updating...' : 'Update Order'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Order?</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete order &quot;{orderDetails.order_number}&quot;? This
              action cannot be undone.
              {orderDetails.report_count > 0 && (
                <span className="block mt-2 text-destructive">
                  This order has {orderDetails.report_count} associated report(s). You must delete
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
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={isDeleting || orderDetails.report_count > 0}
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create/Edit Report Dialog */}
      <ReportFormDialog
        open={reportDialogOpen}
        onOpenChange={setReportDialogOpen}
        mode={reportDialogMode}
        orderId={orderId}
        leases={leases}
        formData={reportFormData}
        onFormDataChange={setReportFormData}
        onSubmit={handleReportSubmit}
        isSubmitting={reportDialogMode === 'create' ? isCreating : isUpdatingReport}
      />

      {/* Delete Report Confirmation Dialog */}
      <Dialog open={deleteReportDialogOpen} onOpenChange={setDeleteReportDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Report?</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this report? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteReportDialogOpen(false)}
              disabled={isDeletingReport}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteReportConfirm}
              disabled={isDeletingReport}
            >
              {isDeletingReport ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

