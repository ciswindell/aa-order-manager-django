import { getOrder } from '@/lib/api/orders';
import { Order } from '@/lib/api/types';
import { useQuery } from '@tanstack/react-query';

export function useOrderDetails(orderId: number) {
  const orderDetailsQuery = useQuery<Order>({
    queryKey: ['order', orderId],
    queryFn: async () => {
      const response = await getOrder(orderId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!orderId,
  });

  return {
    orderDetails: orderDetailsQuery.data,
    isLoading: orderDetailsQuery.isLoading,
    isError: orderDetailsQuery.isError,
    error: orderDetailsQuery.error,
  };
}

