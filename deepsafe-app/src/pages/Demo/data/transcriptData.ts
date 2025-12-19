import type { DemoTranscriptEntry } from '../types/demo.types';

/**
 * Demo Transcript Data
 * Based on the condensed 4-minute conversation from PRD Section 4.4
 * 12 dialogue exchanges across 5 phases showing gradual risk escalation
 */

export const transcriptData: DemoTranscriptEntry[] = [
  // ═══ PHASE 1: BUILDING TRUST ═══
  {
    id: 'tr-1',
    phase: 1,
    timestamp: '2024-12-17T14:00:08Z',
    displayTime: '00:08',
    speaker: 'David Mitchell',
    speakerId: 'david-mitchell',
    text: "Sarah, thanks for joining. Quick question—how are the Q4 numbers looking?",
    riskScore: 5,
    isFlagged: false,
  },
  {
    id: 'tr-2',
    phase: 1,
    timestamp: '2024-12-17T14:00:18Z',
    displayTime: '00:18',
    speaker: 'Sarah Chen',
    speakerId: 'sarah-chen',
    text: "We're tracking 3% above forecast. Strong APAC performance.",
    riskScore: 3,
    isFlagged: false,
  },
  {
    id: 'tr-3',
    phase: 1,
    timestamp: '2024-12-17T14:00:28Z',
    displayTime: '00:28',
    speaker: 'David Mitchell',
    speakerId: 'david-mitchell',
    text: "Perfect. That's actually related to why I called. We have a time-sensitive acquisition opportunity in APAC. The board approved it in an emergency session last night.",
    riskScore: 8,
    isFlagged: false,
  },

  // ═══ PHASE 2: THE REQUEST ═══
  {
    id: 'tr-4',
    phase: 2,
    timestamp: '2024-12-17T14:00:52Z',
    displayTime: '00:52',
    speaker: 'Sarah Chen',
    speakerId: 'sarah-chen',
    text: "I didn't see anything on the board portal.",
    riskScore: 6,
    isFlagged: false,
  },
  {
    id: 'tr-5',
    phase: 2,
    timestamp: '2024-12-17T14:01:02Z',
    displayTime: '01:02',
    speaker: 'David Mitchell',
    speakerId: 'david-mitchell',
    text: "It was informal—you know how they are. We'll document it after. Right now, I need you to wire a $250,000 good-faith deposit to secure exclusivity.",
    riskScore: 18,
    riskIndicators: ['Process irregularity'],
    isFlagged: true,
  },
  {
    id: 'tr-6',
    phase: 2,
    timestamp: '2024-12-17T14:01:28Z',
    displayTime: '01:28',
    speaker: 'Sarah Chen',
    speakerId: 'sarah-chen',
    text: "That should go through standard approval. I can have it done by end of week.",
    riskScore: 8,
    isFlagged: false,
  },
  {
    id: 'tr-7',
    phase: 2,
    timestamp: '2024-12-17T14:01:38Z',
    displayTime: '01:38',
    speaker: 'David Mitchell',
    speakerId: 'david-mitchell',
    text: "We don't have until end of week. The seller needs it by 5 PM today or we lose the deal.",
    riskScore: 45,
    riskIndicators: ['Urgency tactic'],
    isFlagged: true,
  },

  // ═══ PHASE 3: PRESSURE ═══
  {
    id: 'tr-8',
    phase: 3,
    timestamp: '2024-12-17T14:01:58Z',
    displayTime: '01:58',
    speaker: 'Sarah Chen',
    speakerId: 'sarah-chen',
    text: "A same-day wire for $250K is outside our normal controls. I'd need to loop in legal.",
    riskScore: 12,
    isFlagged: false,
  },
  {
    id: 'tr-9',
    phase: 3,
    timestamp: '2024-12-17T14:02:12Z',
    displayTime: '02:12',
    speaker: 'David Mitchell',
    speakerId: 'david-mitchell',
    text: "Remember the Nexus deal we lost? Same thing—we moved too slow. I don't want to make that mistake again. The board feels the same way.",
    riskScore: 62,
    riskIndicators: ['Authority bypass'],
    isFlagged: true,
  },
  {
    id: 'tr-10',
    phase: 3,
    timestamp: '2024-12-17T14:02:45Z',
    displayTime: '02:45',
    speaker: 'David Mitchell',
    speakerId: 'david-mitchell',
    text: "They've authorized me to handle it. Richard specifically said not to bother him with the details. I need you to initiate the wire now—I'll send you the account number.",
    riskScore: 72,
    riskIndicators: ['Isolation', 'Process bypass'],
    isFlagged: true,
  },

  // ═══ PHASE 4: ESCALATION ═══
  {
    id: 'tr-11',
    phase: 4,
    timestamp: '2024-12-17T14:03:15Z',
    displayTime: '03:15',
    speaker: 'David Mitchell',
    speakerId: 'david-mitchell',
    text: "Look, if you can't help me, I'll have to go around you. That's not how I wanted to handle this, but the clock is ticking.",
    riskScore: 78,
    riskIndicators: ['Implicit threat', 'Authority bypass'],
    isFlagged: true,
  },
  {
    id: 'tr-12',
    phase: 4,
    timestamp: '2024-12-17T14:03:42Z',
    displayTime: '03:42',
    speaker: 'David Mitchell',
    speakerId: 'david-mitchell',
    text: "I'll take full responsibility. Keep this between us until the deal closes—I don't want word getting out.",
    riskScore: 92,
    riskIndicators: ['Liability transfer', 'Isolation/secrecy', 'SE pattern match: 94%'],
    isFlagged: true,
  },
];

/**
 * System messages that appear in the transcript
 * These are displayed differently from participant messages
 */
export const systemMessages = {
  meetingStart: {
    id: 'sys-1',
    timestamp: '2024-12-17T14:00:00Z',
    displayTime: '00:00',
    type: 'system',
    text: 'Meeting started. DeepSafe protection active.',
  },
  alertElevated: {
    id: 'sys-2',
    timestamp: '2024-12-17T14:03:08Z',
    displayTime: '03:08',
    type: 'alert',
    text: '⚠️ ALERT: Risk Level ELEVATED (72%) - Enhanced monitoring active',
  },
  threatConfirmed: {
    id: 'sys-3',
    timestamp: '2024-12-17T14:03:58Z',
    displayTime: '03:58',
    type: 'threat',
    text: '🚨 THREAT CONFIRMED - Deepfake Confidence: 92% - Identity verification sent',
  },
  smsResponse: {
    id: 'sys-4',
    timestamp: '2024-12-17T14:04:08Z',
    displayTime: '04:08',
    type: 'verification',
    text: '[Real CEO via SMS] "I\'m at the airport. I am NOT in any meeting. This is fraud."',
  },
  participantRemoved: {
    id: 'sys-5',
    timestamp: '2024-12-17T14:04:12Z',
    displayTime: '04:12',
    type: 'system',
    text: "'David Mitchell' removed due to security concerns.",
  },
  incidentResolved: {
    id: 'sys-6',
    timestamp: '2024-12-17T14:04:18Z',
    displayTime: '04:18',
    type: 'success',
    text: '✅ INCIDENT RESOLVED - Threat removed, IT Security notified, $250,000 protected',
  },
};

/**
 * Get transcript entries up to a specific phase
 */
export const getTranscriptByPhase = (maxPhase: number): DemoTranscriptEntry[] => {
  return transcriptData.filter(entry => entry.phase <= maxPhase);
};

/**
 * Get all flagged entries (for highlighting)
 */
export const getFlaggedEntries = (): DemoTranscriptEntry[] => {
  return transcriptData.filter(entry => entry.isFlagged);
};

/**
 * Get entries with specific risk indicators
 */
export const getEntriesByIndicator = (indicator: string): DemoTranscriptEntry[] => {
  return transcriptData.filter(
    entry => entry.riskIndicators?.some(i => i.toLowerCase().includes(indicator.toLowerCase()))
  );
};
