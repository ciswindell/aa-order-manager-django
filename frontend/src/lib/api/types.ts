/**
 * API Type Definitions
 */

export interface User {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  user: User;
}

export interface ApiError {
  detail?: string;
  message?: string;
  error?: {
    message: string;
    code?: string;
    details?: Record<string, string[]>;
  };
}

export interface IntegrationStatus {
  provider: string;
  is_connected: boolean;
  is_authenticated: boolean;
  last_sync: string;
  blocking_problem: boolean;
  reason: string;
  cta_label: string | null;
  cta_url: string | null;
  // T008: Account identification fields
  account_name?: string | null;
  account_email?: string | null;
  connected_at?: string | null;
}

export interface Order {
  id: number;
  order_number: string;
  order_date: string;
  order_notes: string | null;
  delivery_link: string | null;
  report_count: number;
  created_at: string;
  updated_at: string;
  created_by: number | null;
  created_by_username: string | null;
  updated_by: number | null;
  updated_by_username: string | null;
}

export interface OrderFormData {
  order_number: string;
  order_date: string;
  order_notes?: string;
  delivery_link?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Report {
  id: number;
  order: {
    id: number;
    order_number: string;
  };
  report_type: string;
  legal_description: string;
  start_date: string | null;
  end_date: string | null;
  report_notes: string | null;
  leases: Lease[];
  lease_ids: number[];
  lease_count: number;
  created_at: string;
  updated_at: string;
  created_by: {
    id: number;
    username: string;
  } | null;
  updated_by: {
    id: number;
    username: string;
  } | null;
}

export interface ReportFormData {
  order_id: number;
  report_type: string;
  legal_description: string;
  start_date?: string;
  end_date?: string;
  report_notes?: string;
  lease_ids?: number[];
}

export type ReportType =
  | 'RUNSHEET'
  | 'BASE_ABSTRACT'
  | 'SUPPLEMENTAL_ABSTRACT'
  | 'DOL_ABSTRACT';

export const REPORT_TYPE_LABELS: Record<ReportType, string> = {
  RUNSHEET: 'Runsheet',
  BASE_ABSTRACT: 'Base Abstract',
  SUPPLEMENTAL_ABSTRACT: 'Supplemental Abstract',
  DOL_ABSTRACT: 'DOL Abstract',
};

export type RunsheetStatus = 'Found' | 'Not Found' | 'Pending';

export type AgencyType = 'BLM' | 'NMSLO';

export interface Lease {
  id: number;
  agency: AgencyType;
  lease_number: string;
  runsheet_link: string | null;
  runsheet_report_found: boolean;
  created_at: string;
  updated_at: string;
  created_by: {
    id: number;
    username: string;
  } | null;
  updated_by: {
    id: number;
    username: string;
  } | null;
}

export interface LeaseFormData {
  agency: AgencyType;
  lease_number: string;
}

// Extended Order type for order details page
export interface OrderDetails extends Order {
  reports?: Report[];
}

// Component-specific types for order details feature

export interface LeaseOption {
  label: string;
  value: number;
  lease: Lease;
}

export type ReportDialogMode = 'create' | 'edit';

export interface ReportDialogState {
  open: boolean;
  mode: ReportDialogMode;
  report?: Report;
}

export interface LeaseDisplayItem {
  id: number;
  lease_number: string;
  agency: AgencyType;
  runsheet_report_found: boolean;
}

/**
 * Workflow automation types
 */
export interface WorkflowResult {
  success: boolean;
  workflows_created: string[];
  failed_products?: string[];
  total_count: number;
  message: string;
}

