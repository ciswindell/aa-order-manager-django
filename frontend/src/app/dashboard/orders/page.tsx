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
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { useAuth } from '@/hooks/useAuth';
import { useOrders } from '@/hooks/useOrders';
import { OrderFormData } from '@/lib/api/types';
import { format } from 'date-fns';
import { ChevronLeft, ChevronRight, Edit, Plus, Trash2 } from 'lucide-react';
import { useState } from 'react';

export default function OrdersPage() {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const {
    orders,
    totalCount,
    isLoading,
    createOrder,
    updateOrder,
    deleteOrder,
    isCreating,
    isUpdating,
    isDeleting,
  } = useOrders(page, pageSize);

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<any>(null);

  const [formData, setFormData] = useState<OrderFormData>({
    order_number: '',
    order_date: '',
    order_notes: '',
    delivery_link: '',
  });

  const totalPages = Math.ceil(totalCount / pageSize);

  const handleCreateClick = () => {
    setFormData({
      order_number: '',
      order_date: new Date().toISOString().split('T')[0],
      order_notes: '',
      delivery_link: '',
    });
    setCreateDialogOpen(true);
  };

  const handleEditClick = (order: any) => {
    setSelectedOrder(order);
    setFormData({
      order_number: order.order_number,
      order_date: order.order_date,
      order_notes: order.order_notes || '',
      delivery_link: order.delivery_link || '',
    });
    setEditDialogOpen(true);
  };

  const handleDeleteClick = (order: any) => {
    setSelectedOrder(order);
    setDeleteDialogOpen(true);
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createOrder(formData, {
      onSuccess: () => {
        setCreateDialogOpen(false);
      },
    });
  };

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedOrder) {
      updateOrder(
        { id: selectedOrder.id, data: formData },
        {
          onSuccess: () => {
            setEditDialogOpen(false);
            setSelectedOrder(null);
          },
        }
      );
    }
  };

  const handleDeleteConfirm = () => {
    if (selectedOrder) {
      deleteOrder(selectedOrder.id, {
        onSuccess: () => {
          setDeleteDialogOpen(false);
          setSelectedOrder(null);
        },
      });
    }
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
          <h1 className="text-3xl font-bold">Orders</h1>
          <p className="text-muted-foreground">Manage your orders</p>
        </div>
        <Button onClick={handleCreateClick}>
          <Plus className="mr-2 h-4 w-4" />
          Create Order
        </Button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <p className="text-muted-foreground">Loading orders...</p>
        </div>
      ) : orders.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-muted-foreground mb-4">No orders found</p>
          <Button onClick={handleCreateClick} variant="outline">
            <Plus className="mr-2 h-4 w-4" />
            Create your first order
          </Button>
        </div>
      ) : (
        <>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Order Number</TableHead>
                  <TableHead>Order Date</TableHead>
                  <TableHead>Reports</TableHead>
                  <TableHead>Delivery Link</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {orders.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell className="font-medium">{order.order_number}</TableCell>
                    <TableCell>{format(new Date(order.order_date), 'PP')}</TableCell>
                    <TableCell>{order.report_count}</TableCell>
                    <TableCell>
                      {order.delivery_link ? (
                        <a
                          href={order.delivery_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline"
                        >
                          Link
                        </a>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>{format(new Date(order.created_at), 'PP')}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditClick(order)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteClick(order)}
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

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                Page {page} of {totalPages} ({totalCount} total orders)
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

      {/* Create Order Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent>
          <form onSubmit={handleCreateSubmit}>
            <DialogHeader>
              <DialogTitle>Create Order</DialogTitle>
              <DialogDescription>Add a new order to the system</DialogDescription>
            </DialogHeader>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="order_number">Order Number</FieldLabel>
                <Input
                  id="order_number"
                  value={formData.order_number}
                  onChange={(e) => setFormData({ ...formData, order_number: e.target.value })}
                  required
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="order_date">Order Date</FieldLabel>
                <Input
                  id="order_date"
                  type="date"
                  value={formData.order_date}
                  onChange={(e) => setFormData({ ...formData, order_date: e.target.value })}
                  required
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="delivery_link">Delivery Link (Optional)</FieldLabel>
                <Input
                  id="delivery_link"
                  type="url"
                  value={formData.delivery_link}
                  onChange={(e) => setFormData({ ...formData, delivery_link: e.target.value })}
                  placeholder="https://..."
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="order_notes">Order Notes (Optional)</FieldLabel>
                <Input
                  id="order_notes"
                  value={formData.order_notes}
                  onChange={(e) => setFormData({ ...formData, order_notes: e.target.value })}
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
                {isCreating ? 'Creating...' : 'Create Order'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

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
              Are you sure you want to delete order &quot;{selectedOrder?.order_number}&quot;? This
              action cannot be undone.
              {selectedOrder?.report_count > 0 && (
                <span className="block mt-2 text-destructive">
                  This order has {selectedOrder.report_count} associated report(s). You must delete
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

