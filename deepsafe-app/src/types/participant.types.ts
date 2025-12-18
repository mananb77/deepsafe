import type { RiskBreakdown, RiskCategory } from './meeting.types';

export type ParticipantStatus = 'verified' | 'guest' | 'external' | 'flagged' | 'blacklisted';

export interface ThreatIntelligence {
  deepfakeTechnologyUsed: boolean;
  voiceCloningDetected: boolean;
  faceSwapDetected: boolean;
  socialEngineeringTactics: string[];
  vpnUsage: boolean;
  vpnProvider?: string;
  originLocation: string;
  virtualCameraUsage: boolean;
  unknownDeviceFingerprint: boolean;
  multipleVerificationFailures: number;
  knownThreatPatternMatch: string;
  threatMatchPercentage: number;
}

export interface BlacklistDetails {
  blacklistedAt: string;
  blacklistedBy: string;
  reason: string;
  blockedAttributes: {
    email: string;
    ipRange?: string;
    deviceFingerprint?: string;
  };
  actions: string[];
  reportedToAuthorities: boolean;
  reportedToThreatDatabase: boolean;
}

export interface VerificationDetails {
  ssoVerified: boolean;
  ssoProvider?: string;
  knownDevices: { name: string; lastActive: string }[];
  typicalLocations: string[];
  behavioralBiometricsConsistent: boolean;
  noDeepfakeIndicators: boolean;
}

export interface ParticipantMeetingHistory {
  meetingId: string;
  meetingName: string;
  meetingDate: string;
  role: 'host' | 'participant';
  riskScore: number;
  minutesInMeeting: number;
  riskBreakdown: RiskBreakdown;
  incidentDetected: boolean;
  incidentType?: string;
  outcome?: string;
}

export interface Participant {
  id: string;
  name: string;
  email: string;
  status: ParticipantStatus;
  riskScore: number;
  riskCategory: RiskCategory;
  trustScore: number;
  department?: string;
  role?: string;
  firstSeen: string;
  lastSeen: string;
  totalMeetings: number;
  compromisedMeetings: number;
  incidentRate: number; // percentage
  verification?: VerificationDetails;
  threatIntelligence?: ThreatIntelligence;
  blacklistDetails?: BlacklistDetails;
  meetingHistory?: ParticipantMeetingHistory[];
}

export interface ParticipantFilters {
  status?: ParticipantStatus | 'all';
  riskCategory?: RiskCategory | 'all';
  hasIncidents?: boolean;
  meetingCountMin?: number;
  meetingCountMax?: number;
  searchQuery?: string;
  sortBy?: 'name' | 'riskScore' | 'trustScore' | 'totalMeetings' | 'lastSeen';
  sortOrder?: 'asc' | 'desc';
  page?: number;
  pageSize?: number;
}

export interface ParticipantSummary {
  totalParticipants: number;
  verifiedEmployees: number;
  externalGuests: number;
  blacklistedUsers: number;
  highRiskUsers: number;
}
