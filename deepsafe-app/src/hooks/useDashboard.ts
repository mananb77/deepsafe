import { useQuery } from '@tanstack/react-query';
import { config } from '../config/env';
import apiClient from '../services/apiClient';
import { dashboardMetrics, riskTrendData, recentIncidents, alerts, dateRangePresets } from '../data';
import { adaptMeetingStatsToMetrics } from '../services/adapters';
import type { DashboardMetrics, RiskTrendDataPoint, RecentIncident, Alert } from '../types';
import type { ApiMeetingStatsResponse, ApiIncidentStatsResponse } from '../services/api.types';

export function useDashboardMetrics() {
  return useQuery<DashboardMetrics>({
    queryKey: ['dashboard', 'metrics'],
    queryFn: async () => {
      if (config.isMock) return dashboardMetrics;
      const { data } = await apiClient.get<ApiMeetingStatsResponse>('/meetings/stats');
      const partial = adaptMeetingStatsToMetrics(data);
      // Merge with defaults for fields the backend doesn't provide yet
      return { ...dashboardMetrics, ...partial };
    },
    staleTime: config.isMock ? Infinity : 30_000,
  });
}

export function useRiskTrends() {
  return useQuery<RiskTrendDataPoint[]>({
    queryKey: ['dashboard', 'riskTrends'],
    queryFn: async () => {
      if (config.isMock) return riskTrendData;
      // Backend doesn't have a dedicated risk-trend endpoint yet — fall back to mock
      return riskTrendData;
    },
    staleTime: config.isMock ? Infinity : 60_000,
  });
}

export function useRecentIncidents() {
  return useQuery<RecentIncident[]>({
    queryKey: ['dashboard', 'recentIncidents'],
    queryFn: async () => {
      if (config.isMock) return recentIncidents;
      const { data } = await apiClient.get<ApiIncidentStatsResponse>('/incidents/stats');
      // For now, the stats endpoint doesn't return the full incident list,
      // so fall back to mock until the backend returns recent incidents
      void data;
      return recentIncidents;
    },
    staleTime: config.isMock ? Infinity : 30_000,
  });
}

export function useAlerts() {
  return useQuery<Alert[]>({
    queryKey: ['dashboard', 'alerts'],
    queryFn: async () => {
      // Backend doesn't have a dedicated alerts list endpoint yet
      return alerts;
    },
    staleTime: config.isMock ? Infinity : 30_000,
  });
}

export { dateRangePresets };
