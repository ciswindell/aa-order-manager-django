/**
 * API client for Basecamp workflow creation from orders.
 */

import axios from 'axios';
import { WorkflowResult } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Trigger Basecamp workflow creation for an order.
 *
 * @param orderId - The ID of the order to create workflows for
 * @returns Promise with WorkflowResult containing created workflows
 * @throws Error with response data if request fails
 */
export async function triggerWorkflow(orderId: number): Promise<WorkflowResult> {
  const response = await axios.post<WorkflowResult>(
    `${API_BASE_URL}/orders/${orderId}/workflows/`,
    {}, // Empty body for POST request
    {
      withCredentials: true, // Include JWT cookies
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  return response.data;
}

