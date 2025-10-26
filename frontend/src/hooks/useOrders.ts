import { createOrder, deleteOrder, getOrders, updateOrder } from '@/lib/api/orders';
import { Order, OrderFormData } from '@/lib/api/types';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

export function useOrders(page = 1, pageSize = 20) {
  const queryClient = useQueryClient();

  const ordersQuery = useQuery({
    queryKey: ['orders', page, pageSize],
    queryFn: () => getOrders(page, pageSize),
  });

  const createMutation = useMutation({
    mutationFn: (data: OrderFormData) => createOrder(data),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      toast.success('Order Created', {
        description: 'The order has been created successfully',
        duration: 5000,
      });
      // Custom onSuccess callback will be called by mutation.mutate options
    },
    onError: (error: any) => {
      toast.error('Creation Failed', {
        description: error?.message || 'Failed to create order',
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: OrderFormData }) => updateOrder(id, data),
    onMutate: async ({ id, data }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['orders'] });
      const previousOrders = queryClient.getQueryData(['orders', page, pageSize]);

      queryClient.setQueryData(['orders', page, pageSize], (old: any) => {
        if (!old?.data?.results) return old;
        return {
          ...old,
          data: {
            ...old.data,
            results: old.data.results.map((order: Order) =>
              order.id === id ? { ...order, ...data } : order
            ),
          },
        };
      });

      return { previousOrders };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      toast.success('Order Updated', {
        description: 'The order has been updated successfully',
        duration: 5000,
      });
    },
    onError: (error: any, _variables, context) => {
      // Rollback on error
      if (context?.previousOrders) {
        queryClient.setQueryData(['orders', page, pageSize], context.previousOrders);
      }
      toast.error('Update Failed', {
        description: error?.message || 'Failed to update order',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteOrder(id),
    onMutate: async (id) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['orders'] });
      const previousOrders = queryClient.getQueryData(['orders', page, pageSize]);

      queryClient.setQueryData(['orders', page, pageSize], (old: any) => {
        if (!old?.data?.results) return old;
        return {
          ...old,
          data: {
            ...old.data,
            results: old.data.results.filter((order: Order) => order.id !== id),
            count: old.data.count - 1,
          },
        };
      });

      return { previousOrders };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      toast.success('Order Deleted', {
        description: 'The order has been deleted successfully',
        duration: 5000,
      });
    },
    onError: (error: any, _variables, context) => {
      // Rollback on error
      if (context?.previousOrders) {
        queryClient.setQueryData(['orders', page, pageSize], context.previousOrders);
      }
      const errorMessage =
        error?.message || error?.response?.data?.error || 'Failed to delete order';
      toast.error('Deletion Failed', {
        description: errorMessage,
      });
    },
  });

  return {
    orders: ordersQuery.data?.data?.results || [],
    totalCount: ordersQuery.data?.data?.count || 0,
    isLoading: ordersQuery.isLoading,
    isError: ordersQuery.isError,
    error: ordersQuery.error,
    createOrder: createMutation.mutate,
    updateOrder: updateMutation.mutate,
    deleteOrder: deleteMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

