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

export async function createLease(data: LeaseFormData): Promise<ApiResponse<Lease>> {
  return apiRequest<Lease>('/leases/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateLease(id: number, data: LeaseFormData): Promise<ApiResponse<Lease>> {
  return apiRequest<Lease>(`/leases/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteLease(id: number): Promise<ApiResponse<void>> {
  return apiRequest<void>(`/leases/${id}/`, {
    method: 'DELETE',
  });
}

