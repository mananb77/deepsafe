"""Initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2025-12-17 00:00:01

Creates all initial tables for the DeepSafe platform:
- companies
- users
- meetings
- participants
- incidents
- verifications
- risk_indicators
- policies
- audit_logs
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all initial tables."""

    # Create enum types
    op.execute("""
        CREATE TYPE subscription_tier AS ENUM (
            'free', 'starter', 'professional', 'enterprise'
        )
    """)

    op.execute("""
        CREATE TYPE user_role AS ENUM (
            'admin', 'security_analyst', 'user', 'viewer'
        )
    """)

    op.execute("""
        CREATE TYPE meeting_platform AS ENUM (
            'zoom', 'google_meet', 'microsoft_teams'
        )
    """)

    op.execute("""
        CREATE TYPE meeting_status AS ENUM (
            'scheduled', 'in_progress', 'completed', 'cancelled'
        )
    """)

    op.execute("""
        CREATE TYPE risk_level AS ENUM (
            'low', 'medium', 'high', 'critical'
        )
    """)

    op.execute("""
        CREATE TYPE trust_level AS ENUM (
            'unknown', 'trusted', 'suspicious', 'verified', 'blacklisted'
        )
    """)

    op.execute("""
        CREATE TYPE participant_role AS ENUM (
            'host', 'co_host', 'presenter', 'attendee'
        )
    """)

    op.execute("""
        CREATE TYPE incident_type AS ENUM (
            'audio_deepfake', 'video_deepfake', 'social_engineering',
            'impersonation', 'unauthorized_access', 'suspicious_behavior',
            'verification_failed', 'policy_violation'
        )
    """)

    op.execute("""
        CREATE TYPE incident_severity AS ENUM (
            'low', 'medium', 'high', 'critical'
        )
    """)

    op.execute("""
        CREATE TYPE incident_status AS ENUM (
            'detected', 'investigating', 'verified', 'false_positive', 'resolved'
        )
    """)

    op.execute("""
        CREATE TYPE verification_channel AS ENUM (
            'sms', 'voice', 'push', 'email'
        )
    """)

    op.execute("""
        CREATE TYPE verification_status AS ENUM (
            'pending', 'sent', 'delivered', 'verified', 'failed', 'expired'
        )
    """)

    op.execute("""
        CREATE TYPE verification_type AS ENUM (
            'identity', 'transaction', 'high_risk', 'manual'
        )
    """)

    op.execute("""
        CREATE TYPE indicator_type AS ENUM (
            'audio_deepfake', 'video_deepfake', 'av_sync_anomaly',
            'spectral_anomaly', 'facial_anomaly', 'virtual_camera',
            'scenario_match', 'keyword_detection', 'gpt4_analysis',
            'behavioral_indicator', 'participant_mismatch', 'metadata_anomaly',
            'identity_mismatch', 'custom'
        )
    """)

    op.execute("""
        CREATE TYPE indicator_source AS ENUM (
            'resemble_ai', 'sensity', 'openai_gpt4',
            'wav2vec', 'efficientnet', 'custom_model',
            'keyword_rules', 'behavioral_rules', 'metadata_analysis',
            'analyst'
        )
    """)

    op.execute("""
        CREATE TYPE policy_type AS ENUM (
            'risk_threshold', 'verification', 'notification',
            'approval', 'recording', 'blocking'
        )
    """)

    op.execute("""
        CREATE TYPE policy_trigger AS ENUM (
            'meeting_start', 'participant_join', 'risk_score_change',
            'deepfake_detected', 'social_engineering_detected',
            'transaction_mentioned', 'verification_requested', 'verification_failed'
        )
    """)

    op.execute("""
        CREATE TYPE audit_action AS ENUM (
            'login', 'logout', 'login_failed', 'password_changed', 'password_reset',
            'user_created', 'user_updated', 'user_deleted', 'user_blacklisted',
            'user_whitelisted', 'role_changed',
            'meeting_joined', 'meeting_left', 'meeting_monitored', 'bot_joined', 'bot_left',
            'incident_created', 'incident_updated', 'incident_resolved', 'incident_false_positive',
            'deepfake_detected', 'social_engineering_detected',
            'verification_initiated', 'verification_completed', 'verification_failed',
            'policy_created', 'policy_updated', 'policy_deleted', 'policy_triggered',
            'data_exported', 'report_generated', 'transcript_accessed', 'recording_accessed',
            'settings_updated', 'integration_configured', 'custom'
        )
    """)

    op.execute("""
        CREATE TYPE audit_category AS ENUM (
            'authentication', 'user_management', 'meeting', 'security',
            'verification', 'policy', 'data_access', 'settings', 'other'
        )
    """)

    # Companies table
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("domain", sa.String(255), nullable=False, unique=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("subscription_tier", postgresql.ENUM("free", "starter", "professional", "enterprise", name="subscription_tier", create_type=False), nullable=False, server_default="free"),
        sa.Column("subscription_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("subscription_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("max_users", sa.Integer, nullable=False, server_default="5"),
        sa.Column("max_meetings_per_month", sa.Integer, nullable=False, server_default="100"),
        sa.Column("max_concurrent_meetings", sa.Integer, nullable=False, server_default="3"),
        sa.Column("deepfake_detection_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("social_engineering_detection_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("verification_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("sso_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("siem_integration_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("sso_provider", sa.String(50), nullable=True),
        sa.Column("sso_config", sa.Text, nullable=True),
        sa.Column("default_risk_threshold", sa.Integer, nullable=False, server_default="60"),
        sa.Column("auto_record_high_risk", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notify_security_team", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("security_email", sa.String(255), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("is_sso_user", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("sso_provider", sa.String(50), nullable=True),
        sa.Column("sso_subject_id", sa.String(255), nullable=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", postgresql.ENUM("admin", "security_analyst", "user", "viewer", name="user_role", create_type=False), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("phone_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_blacklisted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("blacklist_reason", sa.String(500), nullable=True),
        sa.Column("blacklisted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_whitelisted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("whitelisted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notify_email", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notify_push", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notify_sms", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("fcm_token", sa.String(500), nullable=True),
        sa.Column("apns_token", sa.String(500), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_company_role", "users", ["company_id", "role"])
    op.create_index("ix_users_sso", "users", ["sso_provider", "sso_subject_id"])

    # Meetings table
    op.create_table(
        "meetings",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("platform", postgresql.ENUM("zoom", "google_meet", "microsoft_teams", name="meeting_platform", create_type=False), nullable=False),
        sa.Column("platform_meeting_id", sa.String(255), nullable=False),
        sa.Column("platform_meeting_url", sa.String(500), nullable=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False, server_default="Untitled Meeting"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("host_email", sa.String(255), nullable=True),
        sa.Column("scheduled_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", postgresql.ENUM("scheduled", "in_progress", "completed", "cancelled", name="meeting_status", create_type=False), nullable=False, server_default="scheduled"),
        sa.Column("participant_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("max_participants", sa.Integer, nullable=False, server_default="0"),
        sa.Column("risk_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("risk_level", postgresql.ENUM("low", "medium", "high", "critical", name="risk_level", create_type=False), nullable=False, server_default="low"),
        sa.Column("peak_risk_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("peak_risk_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deepfake_detected", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("social_engineering_detected", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("verification_triggered", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_recorded", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("recording_url", sa.String(500), nullable=True),
        sa.Column("transcript_available", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("bot_joined", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("bot_joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("bot_left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_meetings_company_status", "meetings", ["company_id", "status"])
    op.create_index("ix_meetings_company_risk", "meetings", ["company_id", "risk_level"])
    op.create_index("ix_meetings_platform", "meetings", ["platform", "platform_meeting_id"])
    op.create_index("ix_meetings_scheduled", "meetings", ["scheduled_start_at"])

    # Participants table
    op.create_table(
        "participants",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("platform_participant_id", sa.String(255), nullable=False),
        sa.Column("platform_user_id", sa.String(255), nullable=True),
        sa.Column("role", postgresql.ENUM("host", "co_host", "presenter", "attendee", name="participant_role", create_type=False), nullable=False, server_default="attendee"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("trust_level", postgresql.ENUM("unknown", "trusted", "suspicious", "verified", "blacklisted", name="trust_level", create_type=False), nullable=False, server_default="unknown"),
        sa.Column("trust_score", sa.Float, nullable=False, server_default="50.0"),
        sa.Column("deepfake_confidence", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("social_engineering_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("composite_risk_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("is_deepfake_suspect", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_social_engineering_suspect", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_flagged", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("flag_reason", sa.String(500), nullable=True),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_method", sa.String(50), nullable=True),
        sa.Column("has_video", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("has_audio", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_screen_sharing", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("device_type", sa.String(50), nullable=True),
        sa.Column("connection_quality", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_participants_meeting", "participants", ["meeting_id"])
    op.create_index("ix_participants_user", "participants", ["user_id"])
    op.create_index("ix_participants_trust", "participants", ["meeting_id", "trust_level"])
    op.create_index("ix_participants_risk", "participants", ["meeting_id", "composite_risk_score"])
    op.create_index("ix_participants_platform", "participants", ["platform_participant_id"])

    # Incidents table
    op.create_table(
        "incidents",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("participant_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("participants.id", ondelete="SET NULL"), nullable=True),
        sa.Column("incident_type", postgresql.ENUM("audio_deepfake", "video_deepfake", "social_engineering", "impersonation", "unauthorized_access", "suspicious_behavior", "verification_failed", "policy_violation", name="incident_type", create_type=False), nullable=False),
        sa.Column("severity", postgresql.ENUM("low", "medium", "high", "critical", name="incident_severity", create_type=False), nullable=False, server_default="medium"),
        sa.Column("status", postgresql.ENUM("detected", "investigating", "verified", "false_positive", "resolved", name="incident_status", create_type=False), nullable=False, server_default="detected"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("meeting_timestamp_seconds", sa.Float, nullable=True),
        sa.Column("evidence_summary", sa.Text, nullable=True),
        sa.Column("evidence_references", postgresql.JSONB, nullable=True),
        sa.Column("screenshot_url", sa.String(500), nullable=True),
        sa.Column("audio_clip_url", sa.String(500), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by_user_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("resolution_notes", sa.Text, nullable=True),
        sa.Column("actions_taken", postgresql.JSONB, nullable=True),
        sa.Column("verification_triggered", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("alert_sent", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("alert_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("detection_method", sa.String(100), nullable=True),
        sa.Column("detection_model", sa.String(100), nullable=True),
        sa.Column("raw_analysis_data", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_incidents_meeting", "incidents", ["meeting_id"])
    op.create_index("ix_incidents_meeting_type", "incidents", ["meeting_id", "incident_type"])
    op.create_index("ix_incidents_status_severity", "incidents", ["status", "severity"])
    op.create_index("ix_incidents_detected_at", "incidents", ["detected_at"])

    # Verifications table
    op.create_table(
        "verifications",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("participant_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("incident_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verification_type", postgresql.ENUM("identity", "transaction", "high_risk", "manual", name="verification_type", create_type=False), nullable=False, server_default="identity"),
        sa.Column("channel", postgresql.ENUM("sms", "voice", "push", "email", name="verification_channel", create_type=False), nullable=False),
        sa.Column("destination", sa.String(255), nullable=False),
        sa.Column("status", postgresql.ENUM("pending", "sent", "delivered", "verified", "failed", "expired", name="verification_status", create_type=False), nullable=False, server_default="pending"),
        sa.Column("verification_code", sa.String(20), nullable=True),
        sa.Column("verification_token", sa.String(255), nullable=True),
        sa.Column("initiated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempt_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer, nullable=False, server_default="3"),
        sa.Column("provider", sa.String(50), nullable=False, server_default="twilio"),
        sa.Column("provider_message_id", sa.String(255), nullable=True),
        sa.Column("provider_status", sa.String(50), nullable=True),
        sa.Column("failure_reason", sa.Text, nullable=True),
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("transaction_amount", sa.Float, nullable=True),
        sa.Column("transaction_description", sa.String(500), nullable=True),
        sa.Column("transaction_metadata", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_verifications_participant", "verifications", ["participant_id"])
    op.create_index("ix_verifications_incident", "verifications", ["incident_id"])
    op.create_index("ix_verifications_status", "verifications", ["status"])
    op.create_index("ix_verifications_channel_status", "verifications", ["channel", "status"])
    op.create_index("ix_verifications_token", "verifications", ["verification_token"])

    # Risk Indicators table
    op.create_table(
        "risk_indicators",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("participant_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("participants.id", ondelete="SET NULL"), nullable=True),
        sa.Column("indicator_type", postgresql.ENUM("audio_deepfake", "video_deepfake", "av_sync_anomaly", "spectral_anomaly", "facial_anomaly", "virtual_camera", "scenario_match", "keyword_detection", "gpt4_analysis", "behavioral_indicator", "participant_mismatch", "metadata_anomaly", "identity_mismatch", "custom", name="indicator_type", create_type=False), nullable=False),
        sa.Column("source", postgresql.ENUM("resemble_ai", "sensity", "openai_gpt4", "wav2vec", "efficientnet", "custom_model", "keyword_rules", "behavioral_rules", "metadata_analysis", "analyst", name="indicator_source", create_type=False), nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("weight", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("weighted_score", sa.Float, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("meeting_timestamp_seconds", sa.Float, nullable=True),
        sa.Column("raw_data", postgresql.JSONB, nullable=True),
        sa.Column("audio_segment_url", sa.String(500), nullable=True),
        sa.Column("video_frame_url", sa.String(500), nullable=True),
        sa.Column("transcript_segment", sa.Text, nullable=True),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("model_threshold", sa.Float, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_risk_indicators_meeting", "risk_indicators", ["meeting_id"])
    op.create_index("ix_risk_indicators_participant", "risk_indicators", ["participant_id"])
    op.create_index("ix_risk_indicators_type", "risk_indicators", ["indicator_type"])
    op.create_index("ix_risk_indicators_meeting_type", "risk_indicators", ["meeting_id", "indicator_type"])
    op.create_index("ix_risk_indicators_confidence", "risk_indicators", ["confidence"])
    op.create_index("ix_risk_indicators_detected", "risk_indicators", ["detected_at"])

    # Policies table
    op.create_table(
        "policies",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("policy_type", postgresql.ENUM("risk_threshold", "verification", "notification", "approval", "recording", "blocking", name="policy_type", create_type=False), nullable=False),
        sa.Column("is_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("priority", sa.Integer, nullable=False, server_default="100"),
        sa.Column("trigger", postgresql.ENUM("meeting_start", "participant_join", "risk_score_change", "deepfake_detected", "social_engineering_detected", "transaction_mentioned", "verification_requested", "verification_failed", name="policy_trigger", create_type=False), nullable=False),
        sa.Column("conditions", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("actions", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("min_risk_score", sa.Float, nullable=True),
        sa.Column("max_risk_score", sa.Float, nullable=True),
        sa.Column("min_transaction_amount", sa.Float, nullable=True),
        sa.Column("max_transaction_amount", sa.Float, nullable=True),
        sa.Column("active_days", postgresql.JSONB, nullable=True),
        sa.Column("active_hours_start", sa.Integer, nullable=True),
        sa.Column("active_hours_end", sa.Integer, nullable=True),
        sa.Column("cooldown_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trigger_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_policies_company", "policies", ["company_id"])
    op.create_index("ix_policies_company_enabled", "policies", ["company_id", "is_enabled"])
    op.create_index("ix_policies_type_trigger", "policies", ["policy_type", "trigger"])
    op.create_index("ix_policies_priority", "policies", ["priority"])

    # Audit Logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", postgresql.ENUM("login", "logout", "login_failed", "password_changed", "password_reset", "user_created", "user_updated", "user_deleted", "user_blacklisted", "user_whitelisted", "role_changed", "meeting_joined", "meeting_left", "meeting_monitored", "bot_joined", "bot_left", "incident_created", "incident_updated", "incident_resolved", "incident_false_positive", "deepfake_detected", "social_engineering_detected", "verification_initiated", "verification_completed", "verification_failed", "policy_created", "policy_updated", "policy_deleted", "policy_triggered", "data_exported", "report_generated", "transcript_accessed", "recording_accessed", "settings_updated", "integration_configured", "custom", name="audit_action", create_type=False), nullable=False),
        sa.Column("category", postgresql.ENUM("authentication", "user_management", "meeting", "security", "verification", "policy", "data_access", "settings", "other", name="audit_category", create_type=False), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("target_type", sa.String(50), nullable=True),
        sa.Column("target_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("ip_address", postgresql.INET, nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("session_id", sa.String(255), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("old_values", postgresql.JSONB, nullable=True),
        sa.Column("new_values", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("is_sensitive", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("risk_level", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_user", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_category", "audit_logs", ["category"])
    op.create_index("ix_audit_logs_occurred", "audit_logs", ["occurred_at"])
    op.create_index("ix_audit_logs_company", "audit_logs", ["company_id"])
    op.create_index("ix_audit_logs_meeting", "audit_logs", ["meeting_id"])
    op.create_index("ix_audit_logs_target", "audit_logs", ["target_type", "target_id"])
    op.create_index("ix_audit_logs_company_occurred", "audit_logs", ["company_id", "occurred_at"])


def downgrade() -> None:
    """Drop all tables and enum types."""

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table("audit_logs")
    op.drop_table("policies")
    op.drop_table("risk_indicators")
    op.drop_table("verifications")
    op.drop_table("incidents")
    op.drop_table("participants")
    op.drop_table("meetings")
    op.drop_table("users")
    op.drop_table("companies")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS audit_category")
    op.execute("DROP TYPE IF EXISTS audit_action")
    op.execute("DROP TYPE IF EXISTS policy_trigger")
    op.execute("DROP TYPE IF EXISTS policy_type")
    op.execute("DROP TYPE IF EXISTS indicator_source")
    op.execute("DROP TYPE IF EXISTS indicator_type")
    op.execute("DROP TYPE IF EXISTS verification_type")
    op.execute("DROP TYPE IF EXISTS verification_status")
    op.execute("DROP TYPE IF EXISTS verification_channel")
    op.execute("DROP TYPE IF EXISTS incident_status")
    op.execute("DROP TYPE IF EXISTS incident_severity")
    op.execute("DROP TYPE IF EXISTS incident_type")
    op.execute("DROP TYPE IF EXISTS participant_role")
    op.execute("DROP TYPE IF EXISTS trust_level")
    op.execute("DROP TYPE IF EXISTS risk_level")
    op.execute("DROP TYPE IF EXISTS meeting_status")
    op.execute("DROP TYPE IF EXISTS meeting_platform")
    op.execute("DROP TYPE IF EXISTS user_role")
    op.execute("DROP TYPE IF EXISTS subscription_tier")
