// Types mirroring backend Pydantic schemas exactly

export interface ApiTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  expires_at: string;
}

export interface ApiUserResponse {
  id: string;
  email: string;
  full_name: string;
  phone_number: string | null;
  company_id: string;
  role: 'admin' | 'security_analyst' | 'user' | 'viewer';
  is_active: boolean;
  is_verified: boolean;
  is_blacklisted: boolean;
  is_whitelisted: boolean;
  last_login_at: string | null;
  last_active_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApiMeetingResponse {
  id: string;
  platform: 'zoom' | 'google_meet' | 'microsoft_teams';
  platform_meeting_id: string;
  platform_meeting_url: string | null;
  company_id: string;
  title: string;
  description: string | null;
  host_email: string;
  scheduled_start_at: string | null;
  scheduled_end_at: string | null;
  actual_start_at: string | null;
  actual_end_at: string | null;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  participant_count: number;
  max_participants: number | null;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  deepfake_detected: boolean;
  social_engineering_detected: boolean;
  verification_triggered: boolean;
  is_recorded: boolean;
  recording_url: string | null;
  transcript_available: boolean;
  bot_joined: boolean;
  bot_joined_at: string | null;
  bot_left_at: string | null;
  extra_data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ApiMeetingDetailResponse extends ApiMeetingResponse {
  participants: ApiParticipantResponse[];
  incident_count: number;
  risk_indicator_count: number;
}

export interface ApiMeetingStatsResponse {
  total_meetings: number;
  active_meetings: number;
  completed_meetings: number;
  high_risk_meetings: number;
  deepfake_detections: number;
  social_engineering_detections: number;
  verification_triggers: number;
  avg_risk_score: number;
  avg_participant_count: number;
}

export interface ApiParticipantResponse {
  id: string;
  meeting_id: string;
  user_id: string | null;
  display_name: string;
  email: string | null;
  phone_number: string | null;
  avatar_url: string | null;
  platform_participant_id: string | null;
  platform_user_id: string | null;
  role: 'host' | 'co_host' | 'presenter' | 'attendee';
  joined_at: string | null;
  left_at: string | null;
  is_active: boolean;
  trust_level: 'unknown' | 'trusted' | 'suspicious' | 'verified' | 'blacklisted';
  trust_score: number;
  deepfake_confidence: number;
  social_engineering_score: number;
  composite_risk_score: number;
  is_deepfake_suspect: boolean;
  is_social_engineering_suspect: boolean;
  is_flagged: boolean;
  flag_reason: string | null;
  is_verified: boolean;
  verified_at: string | null;
  verification_method: string | null;
  has_video: boolean;
  has_audio: boolean;
  is_screen_sharing: boolean;
  device_type: string | null;
  connection_quality: string | null;
  extra_data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ApiParticipantDetailResponse extends ApiParticipantResponse {
  meeting_title: string;
  incident_count: number;
  verification_count: number;
  risk_indicator_count: number;
}

export interface ApiIncidentResponse {
  id: string;
  meeting_id: string;
  participant_id: string | null;
  incident_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'detected' | 'investigating' | 'verified' | 'false_positive' | 'resolved';
  title: string;
  description: string | null;
  confidence_score: number;
  detected_at: string;
  meeting_timestamp_seconds: number | null;
  evidence_summary: string | null;
  evidence_references: Record<string, unknown> | null;
  screenshot_url: string | null;
  audio_clip_url: string | null;
  resolved_at: string | null;
  resolved_by_user_id: string | null;
  resolution_notes: string | null;
  actions_taken: unknown[] | null;
  verification_triggered: boolean;
  alert_sent: boolean;
  detection_method: string | null;
  detection_model: string | null;
  raw_analysis_data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ApiIncidentStatsResponse {
  total_incidents: number;
  open_incidents: number;
  resolved_incidents: number;
  false_positives: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  detection_accuracy: number;
}

export interface ApiPaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
