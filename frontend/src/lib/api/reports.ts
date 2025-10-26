import { apiRequest, ApiResponse } from './client';
import { PaginatedResponse, Report, ReportFormData } from './types';

export async function getReports(
  page = 1,
  pageSize = 20,
  orderId?: number
): Promise<ApiResponse<PaginatedResponse<Report>>> {
  let url = `/reports/?page=${page}&page_size=${pageSize}`;
  if (orderId) {
    url += `&order=${orderId}`;
  }
  return apiRequest<PaginatedResponse<Report>>(url);
}

export async function createReport(data: ReportFormData): Promise<Report> {
  const response = await apiRequest<Report>('/reports/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  if (response.error) {
    throw new Error(response.error);
  }
  return response.data!;
}

export async function updateReport(
  id: number,
  data: ReportFormData
): Promise<Report> {
  const response = await apiRequest<Report>(`/reports/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  if (response.error) {
    throw new Error(response.error);
  }
  return response.data!;
}

export async function deleteReport(id: number): Promise<void> {
  const response = await apiRequest<void>(`/reports/${id}/`, {
    method: 'DELETE',
  });
  if (response.error) {
    throw new Error(response.error);
  }
}

