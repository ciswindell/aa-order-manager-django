import { apiRequest, ApiResponse } from './client';
import { IntegrationStatus, User } from './types';

export interface DashboardData {
  user: User;
  integrations: IntegrationStatus[];
  stats: {
    total_orders: number;
    total_reports: number;
    total_leases: number;
  };
}

export async function getDashboard(): Promise<ApiResponse<DashboardData>> {
  return apiRequest<DashboardData>('/dashboard/');
}

