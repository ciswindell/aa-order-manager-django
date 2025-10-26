import { apiRequest, ApiResponse } from './client';
import { Lease, LeaseFormData, PaginatedResponse } from './types';

export async function getLeases(
  page = 1,
  pageSize = 20,
  reportId?: number,
  agency?: string
): Promise<ApiResponse<PaginatedResponse<Lease>>> {
  let url = `/leases/?page=${page}&page_size=${pageSize}`;
  if (reportId) {
    url += `&report=${reportId}`;
  }
  if (agency) {
    url += `&agency=${encodeURIComponent(agency)}`;
  }
  return apiRequest<PaginatedResponse<Lease>>(url);
}

export async function searchLeases(
  searchTerm: string,
  pageSize = 1000
): Promise<ApiResponse<PaginatedResponse<Lease>>> {
  const url = `/leases/?search=${encodeURIComponent(searchTerm)}&page_size=${pageSize}`;
  return apiRequest<PaginatedResponse<Lease>>(url);
}

export async function createLease(data: LeaseFormData): Promise<Lease> {
  const response = await apiRequest<Lease>('/leases/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  if (response.error) {
    throw new Error(response.error);
  }
  return response.data!;
}

export async function updateLease(id: number, data: LeaseFormData): Promise<Lease> {
  const response = await apiRequest<Lease>(`/leases/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  if (response.error) {
    throw new Error(response.error);
  }
  return response.data!;
}

export async function deleteLease(id: number): Promise<void> {
  const response = await apiRequest<void>(`/leases/${id}/`, {
    method: 'DELETE',
  });
  if (response.error) {
    throw new Error(response.error);
  }
}

