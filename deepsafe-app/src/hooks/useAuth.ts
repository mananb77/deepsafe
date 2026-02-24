import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { config } from '../config/env';
import apiClient from '../services/apiClient';
import { currentUser } from '../data/user';
import type { ApiTokenResponse, ApiUserResponse } from '../services/api.types';

interface LoginCredentials {
  email: string;
  password: string;
}

export function useCurrentUser() {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      if (config.isMock) {
        return {
          id: currentUser.id,
          name: currentUser.name,
          email: currentUser.email,
          role: currentUser.role,
          isAuthenticated: true,
        };
      }
      const token = localStorage.getItem('access_token');
      if (!token) return null;
      const { data } = await apiClient.get<ApiUserResponse>('/auth/me');
      return {
        id: data.id,
        name: data.full_name,
        email: data.email,
        role: data.role,
        isAuthenticated: true,
      };
    },
    staleTime: config.isMock ? Infinity : 5 * 60_000,
    retry: false,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const { data } = await apiClient.post<ApiTokenResponse>('/auth/login', credentials);
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth', 'me'] });
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      if (config.isLive) {
        try {
          await apiClient.post('/auth/logout');
        } catch {
          // Ignore errors on logout
        }
      }
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
    onSuccess: () => {
      queryClient.clear();
    },
  });
}
