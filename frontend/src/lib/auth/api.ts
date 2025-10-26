import { apiRequest, ApiResponse } from '@/lib/api/client';
import { LoginResponse, User } from '@/lib/api/types';
import { userStorage } from './storage';

export async function login(username: string, password: string): Promise<ApiResponse<LoginResponse>> {
  const response = await apiRequest<LoginResponse>('/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });

  // Store user data in localStorage for quick client-side checks
  if (response.data?.user) {
    userStorage.setUser(response.data.user);
  }

  return response;
}

export async function logout(): Promise<void> {
  await apiRequest('/auth/logout/', {
    method: 'POST',
  });

  userStorage.clearUser();
}

export async function getUserProfile(): Promise<ApiResponse<User>> {
  return apiRequest<User>('/auth/user/');
}
