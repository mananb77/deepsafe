import { useQuery } from '@tanstack/react-query';
import { config } from '../config/env';
import apiClient from '../services/apiClient';
import { allParticipants, filterParticipants, getParticipantById } from '../data';
import { adaptParticipantFromApi, adaptParticipantDetailFromApi } from '../services/adapters';
import type { Participant, ParticipantFilters } from '../types';
import type { ApiParticipantResponse, ApiParticipantDetailResponse, ApiPaginatedResponse } from '../services/api.types';

export function useParticipants(filters?: ParticipantFilters) {
  return useQuery<Participant[]>({
    queryKey: ['participants', filters],
    queryFn: async () => {
      if (config.isMock) {
        return filterParticipants(allParticipants, filters || {});
      }
      const params: Record<string, string> = {};
      if (filters?.searchQuery) params.search = filters.searchQuery;
      if (filters?.page) params.page = String(filters.page);
      if (filters?.pageSize) params.size = String(filters.pageSize);
      const { data } = await apiClient.get<ApiPaginatedResponse<ApiParticipantResponse>>('/participants', { params });
      return data.items.map(adaptParticipantFromApi);
    },
    staleTime: config.isMock ? Infinity : 15_000,
  });
}

export function useParticipant(id: string | undefined) {
  return useQuery<Participant | undefined>({
    queryKey: ['participants', id],
    queryFn: async () => {
      if (!id) return undefined;
      if (config.isMock) {
        return getParticipantById(id);
      }
      const { data } = await apiClient.get<ApiParticipantDetailResponse>(`/participants/${id}`);
      return adaptParticipantDetailFromApi(data);
    },
    enabled: !!id,
    staleTime: config.isMock ? Infinity : 10_000,
  });
}

// Re-export for client-side filtering in mock mode
export { allParticipants, filterParticipants };
