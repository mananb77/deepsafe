// Mock current user data for DeepSafe application

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  department: string;
  avatar: string | null;
  initials: string;
  joinDate: string;
  lastLogin: string;
  timezone: string;
  stats: {
    meetingsMonitored: number;
    incidentsDetected: number;
    avgResponseTime: string;
    riskAlertsHandled: number;
  };
  security: {
    twoFactorEnabled: boolean;
    lastPasswordChange: string;
    activeSessions: number;
    loginHistory: Array<{
      timestamp: string;
      device: string;
      location: string;
      status: 'success' | 'failed';
    }>;
  };
  recentActivity: Array<{
    id: string;
    action: string;
    target: string;
    timestamp: string;
    type: 'view' | 'action' | 'report' | 'setting';
  }>;
  preferences: {
    theme: 'dark' | 'light' | 'system';
    dateFormat: 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';
    emailNotifications: {
      criticalIncidents: boolean;
      dailySummary: boolean;
      weeklyReports: boolean;
      systemUpdates: boolean;
    };
    inAppNotifications: boolean;
    alertThreshold: number;
    defaultDashboardView: 'overview' | 'meetings' | 'incidents';
  };
  integrations: {
    zoom: { connected: boolean; lastSync: string | null };
    teams: { connected: boolean; lastSync: string | null };
    googleMeet: { connected: boolean; lastSync: string | null };
    slack: { connected: boolean; lastSync: string | null };
  };
}

export const currentUser: UserProfile = {
  id: 'usr-001',
  name: 'Manan Bhargava',
  email: 'manan@company.com',
  role: 'Security Analyst',
  department: 'Information Security',
  avatar: null,
  initials: 'MB',
  joinDate: '2023-06-15',
  lastLogin: '2024-12-17T14:32:00Z',
  timezone: 'America/Los_Angeles',
  stats: {
    meetingsMonitored: 847,
    incidentsDetected: 23,
    avgResponseTime: '4.2 min',
    riskAlertsHandled: 156,
  },
  security: {
    twoFactorEnabled: true,
    lastPasswordChange: '2024-11-01',
    activeSessions: 2,
    loginHistory: [
      {
        timestamp: '2024-12-17T14:32:00Z',
        device: 'MacBook Pro - Chrome',
        location: 'San Francisco, CA',
        status: 'success',
      },
      {
        timestamp: '2024-12-16T09:15:00Z',
        device: 'iPhone 15 Pro - Safari',
        location: 'San Francisco, CA',
        status: 'success',
      },
      {
        timestamp: '2024-12-15T18:45:00Z',
        device: 'MacBook Pro - Chrome',
        location: 'San Francisco, CA',
        status: 'success',
      },
      {
        timestamp: '2024-12-14T11:20:00Z',
        device: 'Unknown Device - Firefox',
        location: 'New York, NY',
        status: 'failed',
      },
    ],
  },
  recentActivity: [
    {
      id: 'act-001',
      action: 'Viewed meeting details',
      target: 'Q4 Strategy Review',
      timestamp: '2024-12-17T14:28:00Z',
      type: 'view',
    },
    {
      id: 'act-002',
      action: 'Generated incident report',
      target: 'Unauthorized Access Attempt',
      timestamp: '2024-12-17T11:45:00Z',
      type: 'report',
    },
    {
      id: 'act-003',
      action: 'Updated alert threshold',
      target: 'Risk Score Settings',
      timestamp: '2024-12-16T16:30:00Z',
      type: 'setting',
    },
    {
      id: 'act-004',
      action: 'Reviewed participant',
      target: 'John Martinez',
      timestamp: '2024-12-16T14:15:00Z',
      type: 'view',
    },
    {
      id: 'act-005',
      action: 'Dismissed false positive',
      target: 'Network Anomaly Alert',
      timestamp: '2024-12-16T10:00:00Z',
      type: 'action',
    },
  ],
  preferences: {
    theme: 'dark',
    dateFormat: 'MM/DD/YYYY',
    emailNotifications: {
      criticalIncidents: true,
      dailySummary: true,
      weeklyReports: false,
      systemUpdates: true,
    },
    inAppNotifications: true,
    alertThreshold: 70,
    defaultDashboardView: 'overview',
  },
  integrations: {
    zoom: { connected: true, lastSync: '2024-12-17T14:00:00Z' },
    teams: { connected: true, lastSync: '2024-12-17T13:45:00Z' },
    googleMeet: { connected: false, lastSync: null },
    slack: { connected: true, lastSync: '2024-12-17T14:15:00Z' },
  },
};

// FAQ data for Support page
export interface FAQItem {
  id: string;
  category: 'general' | 'technical' | 'security' | 'billing';
  question: string;
  answer: string;
}

export const faqItems: FAQItem[] = [
  {
    id: 'faq-001',
    category: 'general',
    question: 'What is DeepSafe?',
    answer: 'DeepSafe is an AI-powered security platform that monitors video conferences for deepfakes, unauthorized participants, and suspicious behavior in real-time. It helps organizations protect their sensitive meetings from social engineering attacks and identity fraud.',
  },
  {
    id: 'faq-002',
    category: 'general',
    question: 'How does deepfake detection work?',
    answer: 'Our AI analyzes video feeds in real-time, examining facial movements, audio patterns, and behavioral cues to detect synthetic media. We use multiple neural networks trained on millions of authentic and manipulated videos to achieve high accuracy detection.',
  },
  {
    id: 'faq-003',
    category: 'technical',
    question: 'Which video platforms are supported?',
    answer: 'DeepSafe currently supports Zoom, Microsoft Teams, and Google Meet. We integrate directly with these platforms through their APIs to provide seamless monitoring without disrupting your workflow.',
  },
  {
    id: 'faq-004',
    category: 'technical',
    question: 'How do I configure alert thresholds?',
    answer: 'Navigate to Settings > Display Preferences to adjust your alert threshold. The default is 70%, meaning you\'ll be alerted when our confidence in detecting a threat exceeds 70%. Lower values increase sensitivity but may produce more false positives.',
  },
  {
    id: 'faq-005',
    category: 'security',
    question: 'Is my meeting data encrypted?',
    answer: 'Yes, all meeting data is encrypted both in transit (TLS 1.3) and at rest (AES-256). We never store raw video footage - only analyzed metadata and detection results. Your privacy and security are our top priorities.',
  },
  {
    id: 'faq-006',
    category: 'security',
    question: 'How do I enable two-factor authentication?',
    answer: 'Go to Settings > Security Settings and toggle on "Two-Factor Authentication". You can choose between authenticator app (recommended) or SMS verification. We strongly recommend enabling 2FA for all accounts.',
  },
  {
    id: 'faq-007',
    category: 'billing',
    question: 'What plans are available?',
    answer: 'DeepSafe offers three plans: Starter (up to 100 meetings/month), Professional (up to 1,000 meetings/month), and Enterprise (unlimited meetings with custom features). Contact our sales team for detailed pricing.',
  },
  {
    id: 'faq-008',
    category: 'billing',
    question: 'Can I upgrade or downgrade my plan?',
    answer: 'Yes, you can change your plan at any time from Settings > Subscription. Upgrades take effect immediately, while downgrades apply at the start of your next billing cycle.',
  },
];

// System status for Support page
export interface SystemStatus {
  service: string;
  status: 'operational' | 'degraded' | 'outage';
  lastUpdated: string;
}

export const systemStatus: SystemStatus[] = [
  { service: 'Detection Engine', status: 'operational', lastUpdated: '2024-12-17T14:30:00Z' },
  { service: 'Real-time Monitoring', status: 'operational', lastUpdated: '2024-12-17T14:30:00Z' },
  { service: 'API Gateway', status: 'operational', lastUpdated: '2024-12-17T14:30:00Z' },
  { service: 'Dashboard', status: 'operational', lastUpdated: '2024-12-17T14:30:00Z' },
  { service: 'Zoom Integration', status: 'operational', lastUpdated: '2024-12-17T14:30:00Z' },
  { service: 'Teams Integration', status: 'operational', lastUpdated: '2024-12-17T14:30:00Z' },
  { service: 'Google Meet Integration', status: 'degraded', lastUpdated: '2024-12-17T12:15:00Z' },
];

export default currentUser;
