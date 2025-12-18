export type RiskCategory = 'low' | 'medium' | 'high' | 'critical';

export interface RiskBreakdown {
  audioRisk: number;
  videoRisk: number;
  credentialRisk: number;
}

export interface MeetingParticipant {
  id: string;
  name: string;
  email: string;
  role: 'host' | 'participant';
  trustScore: number;
  isFlagged: boolean;
  isVerified: boolean;
  joinTime: string;
  leaveTime?: string;
  minutesInMeeting: number;
  riskBreakdown?: RiskBreakdown;
}

export interface Incident {
  id: string;
  type: 'deepfake_impersonation' | 'social_engineering' | 'bec_attack' | 'credential_theft' | 'unknown';
  description: string;
  detectedAt: string;
  resolvedAt?: string;
  outcome: 'prevented' | 'detected' | 'investigating' | 'false_positive';
  amountProtected?: number;
  riskBreakdown: RiskBreakdown;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  type: 'meeting_start' | 'bot_joined' | 'anomaly_detected' | 'risk_escalation' | 'verification_triggered' | 'fraud_confirmed' | 'incident_resolved' | 'meeting_end';
  title: string;
  description: string;
  riskScore?: number;
  severity?: 'info' | 'warning' | 'error' | 'success';
}

export interface TranscriptEntry {
  id: string;
  timestamp: string;
  speaker: string;
  speakerId: string;
  text: string;
  riskScore: number;
  riskIndicators?: string[];
  isFlagged: boolean;
}

export interface ForensicEvidence {
  videoAnalysis: {
    deepfakeConfidence: number;
    facialLandmarkInconsistencies: number;
    microExpressionAnomalies: boolean;
    lightingInconsistencies: number;
    edgeArtifacts: boolean;
    temporalInconsistencies: boolean;
    evidenceSamples: { frameNumber: number; description: string }[];
  };
  audioAnalysis: {
    voiceCloningConfidence: number;
    spectralAnomalies: boolean;
    prosodyAnomalies: boolean;
    audioVideoDesync: number; // milliseconds
    backgroundNoiseInconsistency: boolean;
    voiceFingerprintMatch: boolean;
    evidenceSamples: { timestamp: string; description: string }[];
  };
  networkAnalysis: {
    ipAddress: string;
    location: string;
    vpnDetected: boolean;
    vpnProvider?: string;
    deviceOS: string;
    browser: string;
    deviceFingerprint: string;
    isKnownDevice: boolean;
    virtualCameraDetected: boolean;
    virtualCameraName?: string;
  };
  behavioralAnalysis: {
    socialEngineeringScore: number;
    authorityBypass: number;
    urgencyTactics: number;
    isolationTactics: number;
    credentialRequestRisk: number;
    conversationPatternMatch: number;
    knownAttackPatternSimilarity: string;
  };
}

export interface Meeting {
  id: string;
  meetingName: string;
  meetingDate: string;
  duration: number; // minutes
  platform: 'zoom' | 'teams' | 'meet' | 'webex';
  host: string;
  hostId: string;
  riskScore: number;
  riskCategory: RiskCategory;
  isCompromised: boolean;
  participants: MeetingParticipant[];
  incident?: Incident;
  timeline?: TimelineEvent[];
  transcript?: TranscriptEntry[];
  forensics?: ForensicEvidence;
  status: 'active' | 'completed' | 'cancelled';
}

export interface MeetingFilters {
  startDate?: string;
  endDate?: string;
  riskCategory?: RiskCategory | 'all';
  isCompromised?: boolean;
  searchQuery?: string;
  sortBy?: 'date' | 'riskScore' | 'name' | 'compromised';
  sortOrder?: 'asc' | 'desc';
  page?: number;
  pageSize?: number;
}

export interface MeetingSummary {
  totalMeetings: number;
  uniqueParticipants: number;
  compromisedMeetings: number;
  suspiciousUsers: number;
  totalMoneyProtected: number;
  avgResponseTime: number; // minutes
}
