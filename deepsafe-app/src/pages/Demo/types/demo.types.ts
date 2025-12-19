import type { ReactNode } from 'react';
import type { ForensicEvidence, TranscriptEntry, TimelineEvent, RiskCategory } from '../../../types/meeting.types';

// Re-export for convenience
export type { ForensicEvidence, TranscriptEntry, TimelineEvent, RiskCategory };

// ============================================
// Demo State Types
// ============================================

export type PlaybackSpeed = 'slow' | 'normal' | 'fast';
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type ModalType = 'explainer' | 'riskBreakdown' | 'forensic' | 'timeline' | 'transcript';
export type ScreenType = 'welcome' | 'lobby' | 'call' | 'report' | 'success';

// ============================================
// Demo Step Configuration
// ============================================

export interface DemoAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  riskLevel?: RiskLevel;
}

export interface DemoStep {
  id: number;
  name: string;
  duration: number; // seconds for auto-play
  component: ScreenType;
  riskScore: number;
  transcriptUpTo: number; // show transcript entries up to this index
  hotspots: HotspotConfig[];
  alerts?: DemoAlert[];
  showVerification?: boolean;
  showThreatConfirmed?: boolean;
  showRemovalAnimation?: boolean;
  activeSpeaker?: string; // participant id
}

// ============================================
// Participant Types
// ============================================

export interface DemoParticipant {
  id: string;
  name: string;
  role: string; // "CEO", "CFO"
  email: string;
  avatar: string;
  trustScore: number;
  isAttacker: boolean;
  isSpeaking?: boolean;
  showDetectionOverlay?: boolean;
  showRemovalAnimation?: boolean;
  realIdentity?: {
    name: string;
    location: string;
  };
}

// ============================================
// Transcript Types (extends existing)
// ============================================

export interface DemoTranscriptEntry extends Omit<TranscriptEntry, 'id'> {
  id: string;
  phase: number; // Which phase of the attack (1-5)
  displayTime: string; // "00:00" format for display
}

// ============================================
// Hotspot System
// ============================================

export interface HotspotConfig {
  id: string;
  type: 'info' | 'data' | 'action';
  anchor: string; // CSS selector or element ID
  offsetX?: number;
  offsetY?: number;
  position?: 'left' | 'right' | 'auto'; // Position relative to anchor (default: 'auto')
  tooltip: string;
  modalConfig: ModalConfig;
}

export interface ModalConfig {
  type: ModalType;
  title: string;
  size: 'sm' | 'md' | 'lg' | 'xl';
  content?: ReactNode;
  data?: RiskBreakdownData | ForensicModalData | TimelineModalData;
}

export interface RiskBreakdownData {
  videoAnalysis: number;
  audioAnalysis: number;
  behavioralAnalysis: number;
  networkAnalysis: number;
  overallScore: number;
}

export interface ForensicModalData {
  forensics: ForensicEvidence;
  activeTab?: 'video' | 'audio' | 'network' | 'behavioral';
}

export interface TimelineModalData {
  events: TimelineEvent[];
  highlightEventId?: string;
}

// ============================================
// Demo State
// ============================================

export interface DemoState {
  // Navigation
  currentStep: number;
  isPlaying: boolean;
  playbackSpeed: PlaybackSpeed;

  // UI State
  activeModal: ModalConfig | null;
  visitedHotspots: Set<string>;
  transcriptExpanded: boolean;

  // Demo Content State
  currentRiskScore: number;
  visibleTranscriptCount: number;
  activeAlerts: DemoAlert[];

  // Verification Flow
  verificationStep: number | null;
  threatConfirmed: boolean;
  participantRemoved: boolean;
}

// ============================================
// Demo Actions
// ============================================

export type DemoAction =
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' }
  | { type: 'GO_TO_STEP'; step: number }
  | { type: 'TOGGLE_PLAY' }
  | { type: 'SET_SPEED'; speed: PlaybackSpeed }
  | { type: 'OPEN_MODAL'; modal: ModalConfig }
  | { type: 'CLOSE_MODAL' }
  | { type: 'MARK_HOTSPOT_VISITED'; hotspotId: string }
  | { type: 'SET_RISK_SCORE'; score: number }
  | { type: 'ADD_ALERT'; alert: DemoAlert }
  | { type: 'CLEAR_ALERTS' }
  | { type: 'SET_VERIFICATION_STEP'; step: number }
  | { type: 'CONFIRM_THREAT' }
  | { type: 'REMOVE_PARTICIPANT' }
  | { type: 'TOGGLE_TRANSCRIPT' }
  | { type: 'RESET_DEMO' };

// ============================================
// Demo Context Value
// ============================================

export interface DemoContextValue {
  state: DemoState;
  dispatch: React.Dispatch<DemoAction>;
  // Derived state
  currentStepConfig: DemoStep;
  riskLevel: RiskLevel;
  canGoBack: boolean;
  canGoForward: boolean;
  activeHotspots: HotspotConfig[];
  progressPercentage: number;
  visibleTranscripts: DemoTranscriptEntry[];
  participants: DemoParticipant[];
}

// ============================================
// Demo Preferences (localStorage)
// ============================================

export interface DemoPreferences {
  playbackSpeed: PlaybackSpeed;
  hintsEnabled: boolean;
  visitedHotspots: string[];
  lastStep: number;
}

// ============================================
// Constants
// ============================================

export const TOTAL_STEPS = 9;

export const SPEED_DURATIONS: Record<PlaybackSpeed, number> = {
  slow: 20000,    // 20 seconds per step
  normal: 12000,  // 12 seconds per step
  fast: 6000,     // 6 seconds per step
};

export const RISK_THRESHOLDS = {
  low: 30,
  medium: 60,
  high: 85,
  critical: 100,
} as const;
