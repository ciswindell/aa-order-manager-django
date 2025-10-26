const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      credentials: 'include', // Send cookies with requests
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      
      // Handle Django REST Framework validation errors
      if (errorData && typeof errorData === 'object' && !errorData.detail) {
        const errors: string[] = [];
        for (const [field, messages] of Object.entries(errorData)) {
          if (Array.isArray(messages)) {
            errors.push(...messages);
          } else if (typeof messages === 'string') {
            errors.push(messages);
          }
        }
        return { error: errors.join(', ') || 'Validation error' };
      }
      
      return { error: errorData.detail || errorData.message || 'An error occurred' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Network error' };
  }
}

