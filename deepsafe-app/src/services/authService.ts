import apiClient from './apiClient';
import type { ApiTokenResponse } from './api.types';

export async function login(email: string, password: string): Promise<ApiTokenResponse> {
  const { data } = await apiClient.post<ApiTokenResponse>('/auth/login', { email, password });
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  return data;
}

export function logout(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

export function getAccessToken(): string | null {
  return localStorage.getItem('access_token');
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem('access_token');
}
