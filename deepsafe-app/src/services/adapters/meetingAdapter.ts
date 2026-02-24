import type { ApiMeetingResponse, ApiMeetingDetailResponse, ApiMeetingStatsResponse } from '../api.types';
import type { Meeting, RiskCategory, MeetingParticipant } from '../../types';
import type { DashboardMetrics } from '../../types';
import { adaptParticipantFromApi } from './participantAdapter';

function mapRiskLevel(level: string): RiskCategory {
  switch (level) {
    case 'critical': return 'critical';
    case 'high': return 'high';
    case 'medium': return 'medium';
    default: return 'low';
  }
}

function mapPlatform(platform: string): Meeting['platform'] {
  switch (platform) {
    case 'google_meet': return 'meet';
    case 'microsoft_teams': return 'teams';
    case 'zoom': return 'zoom';
    default: return 'zoom';
  }
}

function mapStatus(status: string): Meeting['status'] {
  switch (status) {
    case 'in_progress': return 'active';
    case 'completed': return 'completed';
    case 'cancelled': return 'cancelled';
    default: return 'completed';
  }
}

export function adaptMeetingFromApi(api: ApiMeetingResponse): Meeting {
  const duration = api.actual_start_at && api.actual_end_at
    ? Math.round((new Date(api.actual_end_at).getTime() - new Date(api.actual_start_at).getTime()) / 60000)
    : api.scheduled_start_at && api.scheduled_end_at
      ? Math.round((new Date(api.scheduled_end_at).getTime() - new Date(api.scheduled_start_at).getTime()) / 60000)
      : 0;

  return {
    id: api.id,
    meetingName: api.title,
    meetingDate: api.actual_start_at || api.scheduled_start_at || api.created_at,
    duration,
    platform: mapPlatform(api.platform),
    host: api.host_email,
    hostId: api.host_email,
    riskScore: api.risk_score,
    riskCategory: mapRiskLevel(api.risk_level),
    isCompromised: api.deepfake_detected || api.social_engineering_detected,
    participants: [],
    status: mapStatus(api.status),
  };
}

export function adaptMeetingDetailFromApi(api: ApiMeetingDetailResponse): Meeting {
  const base = adaptMeetingFromApi(api);
  const participants: MeetingParticipant[] = api.participants.map((p) => ({
    id: p.id,
    name: p.display_name,
    email: p.email || '',
    role: p.role === 'host' || p.role === 'co_host' ? 'host' : 'participant',
    trustScore: p.trust_score,
    isFlagged: p.is_flagged,
    isVerified: p.is_verified,
    joinTime: p.joined_at || p.created_at,
    leaveTime: p.left_at || undefined,
    minutesInMeeting: p.joined_at && p.left_at
      ? Math.round((new Date(p.left_at).getTime() - new Date(p.joined_at).getTime()) / 60000)
      : 0,
  }));
  return { ...base, participants };
}

export function adaptMeetingStatsToMetrics(
  stats: ApiMeetingStatsResponse,
): Partial<DashboardMetrics> {
  return {
    totalMeetings: stats.total_meetings,
    totalMeetingsTrend: 0,
    compromisedMeetings: stats.deepfake_detections + stats.social_engineering_detections,
    compromisedMeetingsTrend: 0,
    uniqueParticipants: Math.round(stats.avg_participant_count * stats.total_meetings),
    uniqueParticipantsTrend: 0,
  };
}

export function adaptParticipantToMeetingParticipant(
  p: ReturnType<typeof adaptParticipantFromApi>,
): MeetingParticipant {
  return {
    id: p.id,
    name: p.name,
    email: p.email,
    role: 'participant',
    trustScore: p.trustScore,
    isFlagged: p.status === 'flagged' || p.status === 'blacklisted',
    isVerified: p.status === 'verified',
    joinTime: p.firstSeen,
    minutesInMeeting: 0,
  };
}
