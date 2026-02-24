import type { ApiParticipantResponse, ApiParticipantDetailResponse } from '../api.types';
import type { Participant, ParticipantStatus, RiskCategory } from '../../types';

function mapTrustLevel(level: string): ParticipantStatus {
  switch (level) {
    case 'blacklisted': return 'blacklisted';
    case 'suspicious': return 'flagged';
    case 'verified': return 'verified';
    case 'trusted': return 'verified';
    default: return 'external';
  }
}

function mapRiskCategory(score: number): RiskCategory {
  if (score >= 86) return 'critical';
  if (score >= 61) return 'high';
  if (score >= 31) return 'medium';
  return 'low';
}

export function adaptParticipantFromApi(api: ApiParticipantResponse): Participant {
  return {
    id: api.id,
    name: api.display_name,
    email: api.email || '',
    status: api.is_flagged ? 'flagged' : mapTrustLevel(api.trust_level),
    riskScore: api.composite_risk_score,
    riskCategory: mapRiskCategory(api.composite_risk_score),
    trustScore: api.trust_score,
    department: undefined,
    role: api.role === 'host' ? 'Host' : api.role === 'co_host' ? 'Co-host' : 'Participant',
    firstSeen: api.joined_at || api.created_at,
    lastSeen: api.left_at || api.updated_at,
    totalMeetings: 1,
    compromisedMeetings: api.is_deepfake_suspect || api.is_social_engineering_suspect ? 1 : 0,
    incidentRate: api.is_flagged ? 100 : 0,
  };
}

export function adaptParticipantDetailFromApi(api: ApiParticipantDetailResponse): Participant {
  const base = adaptParticipantFromApi(api);
  return {
    ...base,
    totalMeetings: api.incident_count > 0 ? api.incident_count : 1,
  };
}
