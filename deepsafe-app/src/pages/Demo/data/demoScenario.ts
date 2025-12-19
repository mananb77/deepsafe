import type { DemoStep, DemoParticipant, HotspotConfig, DemoAlert } from '../types/demo.types';

// ============================================
// Constants
// ============================================

export const DEMO_TOTAL_STEPS = 9;

// ============================================
// Participants
// ============================================

export const demoParticipants: DemoParticipant[] = [
  {
    id: 'david-mitchell',
    name: 'David Mitchell',
    role: 'CEO',
    email: 'd.mitchell@company.com',
    avatar: '/assets/demo/david-mitchell.jpg',
    trustScore: 85, // Starts high, drops during demo
    isAttacker: true,
    realIdentity: {
      name: 'Morgan Reed',
      location: 'Bucharest, Romania',
    },
  },
  {
    id: 'sarah-chen',
    name: 'Sarah Chen',
    role: 'CFO',
    email: 'sarah.chen@company.com',
    avatar: '/assets/demo/sarah-chen.jpg',
    trustScore: 98,
    isAttacker: false,
  },
  {
    id: 'deepsafe-bot',
    name: 'DeepSafe',
    role: 'Meeting Guardian',
    email: 'bot@deepsafe.ai',
    avatar: '/assets/demo/deepsafe-bot.svg',
    trustScore: 100,
    isAttacker: false,
  },
];

// ============================================
// Hotspot Definitions
// ============================================

const createHotspot = (
  id: string,
  type: 'info' | 'data' | 'action',
  anchor: string,
  tooltip: string,
  modalTitle: string,
  modalSize: 'sm' | 'md' | 'lg' = 'md'
): HotspotConfig => ({
  id,
  type,
  anchor,
  tooltip,
  modalConfig: {
    type: type === 'data' ? 'riskBreakdown' : 'explainer',
    title: modalTitle,
    size: modalSize,
  },
});

// Step 2 Hotspots (Lobby)
const lobbyHotspots: HotspotConfig[] = [
  createHotspot(
    'deepsafe-badge',
    'info',
    '#deepsafe-badge',
    'DeepSafe protected meeting',
    'Meeting Protection',
    'sm'
  ),
];

// Step 3 Hotspots (Normal Call)
const normalCallHotspots: HotspotConfig[] = [
  createHotspot(
    'risk-meter-low',
    'data',
    '#risk-meter',
    'Real-time threat assessment',
    'Risk Score Breakdown'
  ),
  createHotspot(
    'trust-badge-ceo',
    'info',
    '#trust-badge-david',
    'Participant trust score',
    'Trust Scores Explained'
  ),
  createHotspot(
    'deepsafe-bot-participant',
    'info',
    '#participant-deepsafe',
    'DeepSafe meeting guardian',
    'DeepSafe Bot',
    'sm'
  ),
];

// Step 4 Hotspots (First Suspicious)
const firstSuspiciousHotspots: HotspotConfig[] = [
  createHotspot(
    'flagged-message',
    'data',
    '#flagged-transcript-entry',
    'Risk analysis breakdown',
    'Message Risk Analysis'
  ),
  createHotspot(
    'risk-meter-medium',
    'data',
    '#risk-meter',
    'Risk score update',
    'Risk Score Breakdown'
  ),
];

// Step 5 Hotspots (Risk Escalation)
const riskEscalationHotspots: HotspotConfig[] = [
  createHotspot(
    'detection-overlay',
    'data',
    '#detection-overlay',
    'Deepfake analysis results',
    'Video Analysis Results',
    'lg'
  ),
  createHotspot(
    'risk-indicators',
    'info',
    '#risk-indicators',
    'Behavioral risk patterns',
    'Behavioral Analysis'
  ),
  createHotspot(
    'alert-banner',
    'action',
    '#alert-banner',
    'DeepSafe auto-response',
    'Automated Actions'
  ),
];

// Step 6 Hotspots (Verification)
const verificationHotspots: HotspotConfig[] = [
  createHotspot(
    'verification-modal',
    'info',
    '#verification-modal',
    'Identity verification process',
    'Multi-Factor Verification'
  ),
  createHotspot(
    'verification-step-1',
    'info',
    '#verification-step-1',
    'Video authenticity check',
    'Video Analysis'
  ),
  createHotspot(
    'verification-step-2',
    'info',
    '#verification-step-2',
    'Voice fingerprint check',
    'Audio Analysis'
  ),
];

// Step 7 Hotspots (Threat Confirmed)
const threatConfirmedHotspots: HotspotConfig[] = [
  {
    id: 'forensic-summary',
    type: 'data',
    anchor: '#forensic-summary',
    tooltip: 'Full forensic evidence',
    modalConfig: {
      type: 'forensic',
      title: 'Forensic Evidence',
      size: 'lg',
    },
  },
  createHotspot(
    'removal-notification',
    'info',
    '#removal-notification',
    'Threat removal process',
    'Automated Threat Response',
    'sm'
  ),
];

// Step 8 Hotspots (Incident Report)
const incidentReportHotspots: HotspotConfig[] = [
  createHotspot(
    'incident-type',
    'info',
    '#incident-type',
    'Attack classification',
    'Attack Types'
  ),
  {
    id: 'incident-timeline',
    type: 'data',
    anchor: '#incident-timeline',
    tooltip: 'Full event timeline',
    modalConfig: {
      type: 'timeline',
      title: 'Incident Timeline',
      size: 'lg',
    },
  },
  createHotspot(
    'evidence-links',
    'info',
    '#evidence-links',
    'Evidence preservation',
    'Forensic Evidence'
  ),
  createHotspot(
    'amount-protected',
    'info',
    '#amount-protected',
    'Protected amount calculation',
    'Financial Protection'
  ),
];

// Step 9 Hotspots (Success)
const successHotspots: HotspotConfig[] = [
  createHotspot(
    'detection-time',
    'info',
    '#detection-time',
    'Detection performance',
    'Detection Speed'
  ),
];

// ============================================
// Alert Definitions
// ============================================

const alertStep4: DemoAlert = {
  id: 'alert-1',
  type: 'warning',
  message: 'Suspicious pattern detected: Financial request with urgency',
  riskLevel: 'medium',
};

const alertStep5: DemoAlert = {
  id: 'alert-2',
  type: 'error',
  message: 'HIGH RISK: Multiple social engineering indicators detected',
  riskLevel: 'high',
};

const alertStep6: DemoAlert = {
  id: 'alert-3',
  type: 'error',
  message: 'Identity verification triggered - Analyzing participant...',
  riskLevel: 'high',
};

const alertStep7: DemoAlert = {
  id: 'alert-4',
  type: 'error',
  message: '🚨 THREAT CONFIRMED - Deepfake impersonation detected',
  riskLevel: 'critical',
};

// ============================================
// Demo Steps
// ============================================

export const demoScenario: DemoStep[] = [
  // Step 1: Welcome & Introduction
  {
    id: 1,
    name: 'Welcome',
    duration: 8,
    component: 'welcome',
    riskScore: 0,
    transcriptUpTo: 0,
    hotspots: [],
  },

  // Step 2: Meeting Lobby
  {
    id: 2,
    name: 'Meeting Lobby',
    duration: 10,
    component: 'lobby',
    riskScore: 0,
    transcriptUpTo: 0,
    hotspots: lobbyHotspots,
  },

  // Step 3: Meeting Joined - Normal State
  {
    id: 3,
    name: 'Call Joined',
    duration: 15,
    component: 'call',
    riskScore: 12,
    transcriptUpTo: 4, // Show first 4 transcript entries
    hotspots: normalCallHotspots,
    activeSpeaker: 'david-mitchell',
  },

  // Step 4: First Suspicious Message
  {
    id: 4,
    name: 'Suspicious Activity',
    duration: 12,
    component: 'call',
    riskScore: 45,
    transcriptUpTo: 7, // Show through first suspicious message
    hotspots: firstSuspiciousHotspots,
    alerts: [alertStep4],
    activeSpeaker: 'david-mitchell',
  },

  // Step 5: Risk Escalation
  {
    id: 5,
    name: 'Risk Escalation',
    duration: 15,
    component: 'call',
    riskScore: 78,
    transcriptUpTo: 10, // Show through escalation
    hotspots: riskEscalationHotspots,
    alerts: [alertStep5],
    activeSpeaker: 'david-mitchell',
  },

  // Step 6: Verification Triggered
  {
    id: 6,
    name: 'Verification',
    duration: 18, // Longer to show verification process
    component: 'call',
    riskScore: 78,
    transcriptUpTo: 11,
    hotspots: verificationHotspots,
    alerts: [alertStep6],
    showVerification: true,
    activeSpeaker: 'david-mitchell',
  },

  // Step 7: Threat Confirmed & Removal
  {
    id: 7,
    name: 'Threat Removed',
    duration: 12,
    component: 'call',
    riskScore: 92,
    transcriptUpTo: 12, // Full transcript
    hotspots: threatConfirmedHotspots,
    alerts: [alertStep7],
    showThreatConfirmed: true,
    showRemovalAnimation: true,
  },

  // Step 8: Incident Report
  {
    id: 8,
    name: 'Incident Report',
    duration: 15,
    component: 'report',
    riskScore: 0,
    transcriptUpTo: 12,
    hotspots: incidentReportHotspots,
  },

  // Step 9: Success Summary
  {
    id: 9,
    name: 'Attack Prevented',
    duration: 0, // No auto-advance from success
    component: 'success',
    riskScore: 0,
    transcriptUpTo: 12,
    hotspots: successHotspots,
  },
];

// ============================================
// Incident Data for Report Screen
// ============================================

export const demoIncident = {
  id: 'INC-2024-1217-001',
  type: 'deepfake_impersonation' as const,
  description: 'Deepfake impersonation of CEO David Mitchell combined with social engineering tactics targeting CFO for unauthorized wire transfer.',
  detectedAt: '2024-12-17T14:03:58Z',
  resolvedAt: '2024-12-17T14:04:15Z',
  outcome: 'prevented' as const,
  amountProtected: 250000,
  duration: '3 minutes 42 seconds',
  detectionTime: '1 minute 38 seconds',
  riskBreakdown: {
    audioRisk: 67,
    videoRisk: 92,
    credentialRisk: 94,
  },
};

// ============================================
// Timeline Events for Report Screen
// ============================================

export const demoTimeline = [
  {
    id: 't1',
    timestamp: '14:00:00',
    type: 'meeting_start' as const,
    title: 'Meeting Started',
    description: 'Video call initiated by "David Mitchell"',
    severity: 'info' as const,
  },
  {
    id: 't2',
    timestamp: '14:00:03',
    type: 'bot_joined' as const,
    title: 'DeepSafe Active',
    description: 'DeepSafe protection enabled, monitoring all participants',
    severity: 'info' as const,
  },
  {
    id: 't3',
    timestamp: '14:01:02',
    type: 'anomaly_detected' as const,
    title: 'First Anomaly',
    description: 'Process irregularity detected in conversation',
    riskScore: 18,
    severity: 'warning' as const,
  },
  {
    id: 't4',
    timestamp: '14:01:38',
    type: 'risk_escalation' as const,
    title: 'Risk Escalation',
    description: 'Urgency tactics and authority bypass patterns detected',
    riskScore: 45,
    severity: 'warning' as const,
  },
  {
    id: 't5',
    timestamp: '14:02:45',
    type: 'risk_escalation' as const,
    title: 'High Risk Alert',
    description: 'Multiple social engineering indicators confirmed',
    riskScore: 72,
    severity: 'error' as const,
  },
  {
    id: 't6',
    timestamp: '14:03:08',
    type: 'verification_triggered' as const,
    title: 'Verification Triggered',
    description: 'Identity verification initiated via SMS to verified contact',
    riskScore: 78,
    severity: 'warning' as const,
  },
  {
    id: 't7',
    timestamp: '14:03:58',
    type: 'fraud_confirmed' as const,
    title: 'Threat Confirmed',
    description: 'Deepfake detected (92% confidence), real CEO confirmed not in meeting',
    riskScore: 92,
    severity: 'error' as const,
  },
  {
    id: 't8',
    timestamp: '14:04:15',
    type: 'incident_resolved' as const,
    title: 'Incident Resolved',
    description: 'Threat actor removed, IT Security notified, evidence preserved',
    severity: 'success' as const,
  },
];
