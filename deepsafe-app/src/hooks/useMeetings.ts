import { useQuery } from '@tanstack/react-query';
import { config } from '../config/env';
import apiClient from '../services/apiClient';
import { allMeetings, filterMeetings, getMeetingById } from '../data';
import { adaptMeetingFromApi, adaptMeetingDetailFromApi } from '../services/adapters';
import type { Meeting, MeetingFilters } from '../types';
import type { ApiMeetingResponse, ApiMeetingDetailResponse, ApiPaginatedResponse } from '../services/api.types';

export function useMeetings(filters?: MeetingFilters) {
  return useQuery<Meeting[]>({
    queryKey: ['meetings', filters],
    queryFn: async () => {
      if (config.isMock) {
        return filterMeetings(allMeetings, filters || {});
      }
      const params: Record<string, string> = {};
      if (filters?.searchQuery) params.search = filters.searchQuery;
      if (filters?.riskCategory && filters.riskCategory !== 'all') params.risk_level = filters.riskCategory;
      if (filters?.page) params.page = String(filters.page);
      if (filters?.pageSize) params.size = String(filters.pageSize);
      const { data } = await apiClient.get<ApiPaginatedResponse<ApiMeetingResponse>>('/meetings', { params });
      return data.items.map(adaptMeetingFromApi);
    },
    staleTime: config.isMock ? Infinity : 15_000,
  });
}

export function useMeeting(id: string | undefined) {
  return useQuery<Meeting | undefined>({
    queryKey: ['meetings', id],
    queryFn: async () => {
      if (!id) return undefined;
      if (config.isMock) {
        return getMeetingById(id);
      }
      const { data } = await apiClient.get<ApiMeetingDetailResponse>(`/meetings/${id}`);
      return adaptMeetingDetailFromApi(data);
    },
    enabled: !!id,
    staleTime: config.isMock ? Infinity : 10_000,
  });
}

// Re-export mock data and filter for direct use (e.g., client-side sorting in mock mode)
export { allMeetings, filterMeetings };
