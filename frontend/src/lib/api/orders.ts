import { apiRequest, ApiResponse } from './client';
import { Order, OrderFormData, PaginatedResponse } from './types';

export async function getOrders(
  page = 1,
  pageSize = 20
): Promise<ApiResponse<PaginatedResponse<Order>>> {
  return apiRequest<PaginatedResponse<Order>>(`/orders/?page=${page}&page_size=${pageSize}`);
}

export async function createOrder(data: OrderFormData): Promise<ApiResponse<Order>> {
  return apiRequest<Order>('/orders/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateOrder(id: number, data: OrderFormData): Promise<ApiResponse<Order>> {
  return apiRequest<Order>(`/orders/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteOrder(id: number): Promise<ApiResponse<void>> {
  return apiRequest<void>(`/orders/${id}/`, {
    method: 'DELETE',
  });
}

