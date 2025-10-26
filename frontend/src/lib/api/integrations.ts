import { apiRequest, ApiResponse } from './client';
import { IntegrationStatus } from './types';

export async function getIntegrationStatus(): Promise<ApiResponse<IntegrationStatus[]>> {
  return apiRequest<IntegrationStatus[]>('/integrations/status/');
}

export async function connectDropbox(): Promise<ApiResponse<{ authorize_url: string }>> {
  return apiRequest<{ authorize_url: string }>('/integrations/dropbox/connect/', {
    method: 'POST',
  });
}

export async function disconnectDropbox(): Promise<ApiResponse<{ message: string }>> {
  return apiRequest<{ message: string }>('/integrations/dropbox/disconnect/', {
    method: 'POST',
  });
}

