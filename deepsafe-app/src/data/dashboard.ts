import type { DashboardMetrics, RiskTrendDataPoint, RecentIncident, Alert } from '../types';

export const dashboardMetrics: DashboardMetrics = {
  totalMeetings: 126,
  totalMeetingsTrend: 12, // +12% vs previous period
  uniqueParticipants: 1632,
  uniqueParticipantsTrend: 8, // +8%
  compromisedMeetings: 2,
  compromisedMeetingsTrend: 1, // +1 vs previous period (was 1)
  suspiciousUsers: 2,
  suspiciousUsersTrend: 1, // +1
  totalMoneyProtected: 295000,
  totalMoneyProtectedTrend: 140000, // +$140K
  avgResponseTime: 1.8, // minutes
  avgResponseTimeTrend: -0.3, // -0.3 minutes (improved)
};

// Generate risk trend data for the past 30 days
export const generateRiskTrendData = (): RiskTrendDataPoint[] => {
  const data: RiskTrendDataPoint[] = [];
  const today = new Date('2024-04-10');

  for (let i = 30; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);

    // Most days have low average risk (10-25%)
    // A few days have spikes (incidents on Apr 8 and 9)
    let avgRisk = Math.floor(Math.random() * 15) + 10;
    let highRiskCount = 0;
    let criticalAlerts = 0;

    // Spike on Apr 8 (nonprofit funding incident)
    if (date.toISOString().startsWith('2024-04-08')) {
      avgRisk = 45;
      highRiskCount = 1;
      criticalAlerts = 1;
    }

    // Spike on Apr 9 (CSO deepfake incident)
    if (date.toISOString().startsWith('2024-04-09')) {
      avgRisk = 52;
      highRiskCount = 1;
      criticalAlerts = 1;
    }

    data.push({
      date: date.toISOString().split('T')[0],
      averageRiskScore: avgRisk,
      highRiskCount,
      criticalAlerts,
    });
  }

  return data;
};

export const riskTrendData = generateRiskTrendData();

export const recentIncidents: RecentIncident[] = [
  {
    id: 'inc-20240409-001',
    incidentCode: 'INC-20240409-001',
    timestamp: '2024-04-09T14:05:00Z',
    type: 'Deepfake Impersonation',
    description: 'Deepfake attack prevented',
    amountProtected: 250000,
    riskScore: 94,
    status: 'resolved',
    meetingId: '34190412',
    meetingName: 'CSO <> Employee',
  },
  {
    id: 'inc-20240408-001',
    incidentCode: 'INC-20240408-001',
    timestamp: '2024-04-08T10:15:00Z',
    type: 'Social Engineering',
    description: 'Social engineering attempt',
    amountProtected: 45000,
    riskScore: 78,
    status: 'resolved',
    meetingId: '41930120',
    meetingName: 'Nonprofit Funding Discussion',
  },
  {
    id: 'normal-001',
    incidentCode: 'MTG-20240408-001',
    timestamp: '2024-04-08T09:00:00Z',
    type: 'Regular Monitoring',
    description: 'Team standup - No issues detected',
    riskScore: 8,
    status: 'resolved',
    meetingId: '19308139',
    meetingName: 'Product Team Standup',
  },
];

export const alerts: Alert[] = [
  {
    id: 'alert-1',
    type: 'critical',
    title: 'Deepfake attack in progress',
    message: 'Meeting: M&A Discussion - Risk: 94%',
    timestamp: '2024-04-09T14:05:00Z',
    meetingId: '34190412',
    incidentId: 'inc-20240409-001',
    isRead: false,
    actionUrl: '/meetings/34190412',
  },
  {
    id: 'alert-2',
    type: 'success',
    title: 'Fraud prevented',
    message: 'Amount protected: $45,000',
    timestamp: '2024-04-08T10:20:00Z',
    meetingId: '41930120',
    incidentId: 'inc-20240408-001',
    isRead: true,
    actionUrl: '/meetings/41930120',
  },
  {
    id: 'alert-3',
    type: 'info',
    title: 'System Update',
    message: 'Detection models updated - New patterns added',
    timestamp: '2024-04-08T09:00:00Z',
    isRead: true,
  },
  {
    id: 'alert-4',
    type: 'info',
    title: 'Weekly Report',
    message: '5 incidents prevented, $295K protected',
    timestamp: '2024-04-07T09:00:00Z',
    isRead: true,
    actionUrl: '/reports/weekly',
  },
];

// Date range presets
export const dateRangePresets = [
  { label: 'Last 7 Days', days: 7 },
  { label: 'Last 30 Days', days: 30 },
  { label: 'Last 90 Days', days: 90 },
  { label: 'This Month', days: -1 }, // Special handling
  { label: 'Last Month', days: -2 }, // Special handling
];
