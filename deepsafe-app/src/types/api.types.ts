export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    totalItems: number;
    totalPages: number;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
}

export interface DashboardMetrics {
  totalMeetings: number;
  totalMeetingsTrend: number; // percentage change from previous period
  uniqueParticipants: number;
  uniqueParticipantsTrend: number;
  compromisedMeetings: number;
  compromisedMeetingsTrend: number;
  suspiciousUsers: number;
  suspiciousUsersTrend: number;
  totalMoneyProtected: number;
  totalMoneyProtectedTrend: number;
  avgResponseTime: number;
  avgResponseTimeTrend: number;
}

export interface RiskTrendDataPoint {
  date: string;
  averageRiskScore: number;
  highRiskCount: number;
  criticalAlerts: number;
}

export interface RecentIncident {
  id: string;
  incidentCode: string;
  timestamp: string;
  type: string;
  description: string;
  amountProtected?: number;
  riskScore: number;
  status: 'resolved' | 'investigating' | 'pending';
  meetingId: string;
  meetingName: string;
}

export interface Alert {
  id: string;
  type: 'critical' | 'warning' | 'info' | 'success';
  title: string;
  message: string;
  timestamp: string;
  meetingId?: string;
  incidentId?: string;
  isRead: boolean;
  actionUrl?: string;
}

export interface DateRange {
  startDate: string;
  endDate: string;
  label?: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  department: string;
  avatar?: string;
  phone?: string;
  connectedDevices: { name: string; lastActive: string; verificationMethod: string }[];
}
