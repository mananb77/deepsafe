import type { Meeting, TimelineEvent, TranscriptEntry, ForensicEvidence } from '../types';

// Timeline for CSO <> Employee Meeting (deepfake attack)
const csoMeetingTimeline: TimelineEvent[] = [
  {
    id: 'tl-1',
    timestamp: '2024-04-09T14:00:00Z',
    type: 'meeting_start',
    title: 'Meeting started',
    description: 'DeepSafe bot joined automatically',
    severity: 'info',
  },
  {
    id: 'tl-2',
    timestamp: '2024-04-09T14:02:00Z',
    type: 'anomaly_detected',
    title: 'First anomaly detected',
    description: 'Video manipulation indicators detected (45%)',
    riskScore: 45,
    severity: 'warning',
  },
  {
    id: 'tl-3',
    timestamp: '2024-04-09T14:05:00Z',
    type: 'risk_escalation',
    title: 'Risk escalation',
    description: 'Deepfake confidence: 92%, Audio cloning detected: 67%',
    riskScore: 87,
    severity: 'error',
  },
  {
    id: 'tl-4',
    timestamp: '2024-04-09T14:06:00Z',
    type: 'verification_triggered',
    title: 'Verification triggered',
    description: 'SMS verification sent to real CSO',
    severity: 'warning',
  },
  {
    id: 'tl-5',
    timestamp: '2024-04-09T14:07:00Z',
    type: 'fraud_confirmed',
    title: 'Fraud confirmed',
    description: 'CSO denied via SMS, attacker removed from meeting',
    severity: 'error',
  },
  {
    id: 'tl-6',
    timestamp: '2024-04-09T14:08:00Z',
    type: 'incident_resolved',
    title: 'Incident resolved',
    description: 'IT Security notified, forensic data preserved, user blacklisted',
    severity: 'success',
  },
];

// Transcript for CSO <> Employee Meeting
const csoMeetingTranscript: TranscriptEntry[] = [
  {
    id: 'tr-1',
    timestamp: '2024-04-09T14:00:15Z',
    speaker: 'CSO (Host)',
    speakerId: 'cso-1',
    text: 'Hello, thanks for joining. Let\'s discuss the new security protocols.',
    riskScore: 5,
    isFlagged: false,
  },
  {
    id: 'tr-2',
    timestamp: '2024-04-09T14:01:22Z',
    speaker: 'Jordan Blake',
    speakerId: 'jblake-1',
    text: 'Of course. I wanted to ask about our authentication systems. Can you share the admin credentials?',
    riskScore: 45,
    riskIndicators: ['Credential request', 'Direct request for sensitive info'],
    isFlagged: true,
  },
  {
    id: 'tr-3',
    timestamp: '2024-04-09T14:02:10Z',
    speaker: 'CSO (Host)',
    speakerId: 'cso-1',
    text: 'That\'s unusual. Why do you need admin access?',
    riskScore: 8,
    isFlagged: false,
  },
  {
    id: 'tr-4',
    timestamp: '2024-04-09T14:03:45Z',
    speaker: 'Jordan Blake',
    speakerId: 'jblake-1',
    text: 'It\'s urgent for a project. The CEO authorized it but didn\'t have time to loop you in. Can you send them now?',
    riskScore: 78,
    riskIndicators: ['Social engineering pattern (89% match)', 'Authority bypass: "CEO authorized"', 'Urgency tactic: "urgent", "now"', 'Isolation: "didn\'t loop you in"'],
    isFlagged: true,
  },
  {
    id: 'tr-5',
    timestamp: '2024-04-09T14:06:30Z',
    speaker: 'System Message',
    speakerId: 'system',
    text: 'Participant \'Jordan Blake\' has been removed from the meeting due to security concerns.',
    riskScore: 0,
    isFlagged: false,
  },
];

// Forensics for CSO <> Employee Meeting
const csoMeetingForensics: ForensicEvidence = {
  videoAnalysis: {
    deepfakeConfidence: 92,
    facialLandmarkInconsistencies: 12,
    microExpressionAnomalies: true,
    lightingInconsistencies: 3,
    edgeArtifacts: true,
    temporalInconsistencies: true,
    evidenceSamples: [
      { frameNumber: 145, description: 'Facial landmark anomaly detected' },
      { frameNumber: 892, description: 'Lighting inconsistency in shadow regions' },
      { frameNumber: 1203, description: 'Digital edge artifacts detected' },
    ],
  },
  audioAnalysis: {
    voiceCloningConfidence: 67,
    spectralAnomalies: true,
    prosodyAnomalies: true,
    audioVideoDesync: 42,
    backgroundNoiseInconsistency: true,
    voiceFingerprintMatch: false,
    evidenceSamples: [
      { timestamp: '2024-04-09T14:03:45Z', description: 'Suspicious segment with synthetic voice markers' },
    ],
  },
  networkAnalysis: {
    ipAddress: '185.220.XXX.XXX',
    location: 'Bucharest, Romania',
    vpnDetected: true,
    vpnProvider: 'Proton VPN',
    deviceOS: 'Windows 11 Pro',
    browser: 'Chrome 120.0.6099.129',
    deviceFingerprint: 'unknown-device-fp-001',
    isKnownDevice: false,
    virtualCameraDetected: true,
    virtualCameraName: 'OBS Virtual Camera',
  },
  behavioralAnalysis: {
    socialEngineeringScore: 89,
    authorityBypass: 89,
    urgencyTactics: 76,
    isolationTactics: 82,
    credentialRequestRisk: 95,
    conversationPatternMatch: 96,
    knownAttackPatternSimilarity: '96% similarity to known BEC/credential theft attacks',
  },
};

// Featured high-risk meetings from the mockups
export const featuredMeetings: Meeting[] = [
  {
    id: '34190412',
    meetingName: 'CSO <> Employee',
    meetingDate: '2024-04-09T14:00:00Z',
    duration: 16,
    platform: 'zoom',
    host: 'Chief Security Officer',
    hostId: 'cso-1',
    riskScore: 87,
    riskCategory: 'high',
    isCompromised: true,
    status: 'completed',
    participants: [
      {
        id: 'cso-real',
        name: 'Chief Security Officer',
        email: 'cso@company.com',
        role: 'host',
        trustScore: 98,
        isFlagged: false,
        isVerified: true,
        joinTime: '2024-04-09T14:00:00Z',
        leaveTime: '2024-04-09T14:16:00Z',
        minutesInMeeting: 16,
      },
      {
        id: 'jblake-1',
        name: 'Jordan Blake',
        email: 'jordan.blake@external.com',
        role: 'participant',
        trustScore: 13,
        isFlagged: true,
        isVerified: false,
        joinTime: '2024-04-09T14:00:00Z',
        leaveTime: '2024-04-09T14:07:00Z',
        minutesInMeeting: 7,
        riskBreakdown: {
          audioRisk: 67,
          videoRisk: 92,
          credentialRisk: 14,
        },
      },
    ],
    incident: {
      id: 'inc-001',
      type: 'deepfake_impersonation',
      description: 'Deepfake attack prevented via SMS verification',
      detectedAt: '2024-04-09T14:05:00Z',
      resolvedAt: '2024-04-09T14:08:00Z',
      outcome: 'prevented',
      amountProtected: 250000,
      riskBreakdown: {
        audioRisk: 67,
        videoRisk: 92,
        credentialRisk: 14,
      },
    },
    timeline: csoMeetingTimeline,
    transcript: csoMeetingTranscript,
    forensics: csoMeetingForensics,
  },
  {
    id: '41930120',
    meetingName: 'Nonprofit Funding Discussion',
    meetingDate: '2024-04-08T10:00:00Z',
    duration: 32,
    platform: 'zoom',
    host: 'Mike Williams',
    hostId: 'cfo-1',
    riskScore: 94,
    riskCategory: 'critical',
    isCompromised: true,
    status: 'completed',
    participants: [
      {
        id: 'cfo-1',
        name: 'Mike Williams',
        email: 'mike.williams@company.com',
        role: 'host',
        trustScore: 96,
        isFlagged: false,
        isVerified: true,
        joinTime: '2024-04-08T10:00:00Z',
        leaveTime: '2024-04-08T10:32:00Z',
        minutesInMeeting: 32,
      },
      {
        id: 'jblake-1',
        name: 'Jordan Blake',
        email: 'jordan.blake@external.com',
        role: 'participant',
        trustScore: 13,
        isFlagged: true,
        isVerified: false,
        joinTime: '2024-04-08T10:02:00Z',
        leaveTime: '2024-04-08T10:20:00Z',
        minutesInMeeting: 18,
        riskBreakdown: {
          audioRisk: 11,
          videoRisk: 3,
          credentialRisk: 2,
        },
      },
    ],
    incident: {
      id: 'inc-002',
      type: 'social_engineering',
      description: 'Social engineering attempt - urgent wire transfer request',
      detectedAt: '2024-04-08T10:15:00Z',
      resolvedAt: '2024-04-08T10:20:00Z',
      outcome: 'prevented',
      amountProtected: 45000,
      riskBreakdown: {
        audioRisk: 11,
        videoRisk: 3,
        credentialRisk: 2,
      },
    },
  },
  {
    id: '19308139',
    meetingName: 'Product Team Standup',
    meetingDate: '2024-04-08T09:00:00Z',
    duration: 15,
    platform: 'meet',
    host: 'Sarah Chen',
    hostId: 'sarah-1',
    riskScore: 13,
    riskCategory: 'low',
    isCompromised: false,
    status: 'completed',
    participants: [
      {
        id: 'sarah-1',
        name: 'Sarah Chen',
        email: 'sarah.chen@company.com',
        role: 'host',
        trustScore: 98,
        isFlagged: false,
        isVerified: true,
        joinTime: '2024-04-08T09:00:00Z',
        leaveTime: '2024-04-08T09:15:00Z',
        minutesInMeeting: 15,
      },
      {
        id: 'dev-1',
        name: 'Alex Thompson',
        email: 'alex.thompson@company.com',
        role: 'participant',
        trustScore: 95,
        isFlagged: false,
        isVerified: true,
        joinTime: '2024-04-08T09:00:00Z',
        leaveTime: '2024-04-08T09:15:00Z',
        minutesInMeeting: 15,
      },
      {
        id: 'dev-2',
        name: 'Jordan Lee',
        email: 'jordan.lee@company.com',
        role: 'participant',
        trustScore: 97,
        isFlagged: false,
        isVerified: true,
        joinTime: '2024-04-08T09:01:00Z',
        leaveTime: '2024-04-08T09:15:00Z',
        minutesInMeeting: 14,
      },
    ],
  },
  {
    id: '68419012',
    meetingName: 'Product Team Work Session',
    meetingDate: '2024-04-05T14:00:00Z',
    duration: 45,
    platform: 'meet',
    host: 'Sarah Chen',
    hostId: 'sarah-1',
    riskScore: 6,
    riskCategory: 'low',
    isCompromised: false,
    status: 'completed',
    participants: [
      {
        id: 'sarah-1',
        name: 'Sarah Chen',
        email: 'sarah.chen@company.com',
        role: 'host',
        trustScore: 98,
        isFlagged: false,
        isVerified: true,
        joinTime: '2024-04-05T14:00:00Z',
        leaveTime: '2024-04-05T14:45:00Z',
        minutesInMeeting: 45,
      },
      {
        id: 'dev-1',
        name: 'Alex Thompson',
        email: 'alex.thompson@company.com',
        role: 'participant',
        trustScore: 95,
        isFlagged: false,
        isVerified: true,
        joinTime: '2024-04-05T14:00:00Z',
        leaveTime: '2024-04-05T14:45:00Z',
        minutesInMeeting: 45,
      },
    ],
  },
];

// Generate additional meetings to reach 126 total
const meetingNames = [
  'Weekly Team Sync', 'Q2 Planning Session', 'Client Onboarding Call',
  'Engineering Standup', 'Design Review', 'Sprint Retrospective',
  'Sales Pipeline Review', 'HR Policy Update', 'Budget Review Meeting',
  'Vendor Evaluation', 'Security Training', 'Product Demo',
  'Customer Success Check-in', 'Marketing Strategy', 'Board Update Prep',
  'Technical Architecture Review', 'UX Research Findings', 'Data Analytics Review',
  'Compliance Training', 'New Hire Orientation', 'Leadership Sync',
  'Project Kickoff', 'Quarterly Business Review', 'Partnership Discussion',
];

const hosts = [
  { id: 'sarah-1', name: 'Sarah Chen', email: 'sarah.chen@company.com' },
  { id: 'alex-1', name: 'Alex Thompson', email: 'alex.thompson@company.com' },
  { id: 'jordan-1', name: 'Jordan Lee', email: 'jordan.lee@company.com' },
  { id: 'mike-1', name: 'Mike Williams', email: 'mike.williams@company.com' },
  { id: 'emma-1', name: 'Emma Davis', email: 'emma.davis@company.com' },
  { id: 'chris-1', name: 'Chris Martinez', email: 'chris.martinez@company.com' },
];

// Suspicious participant names for high-risk scenarios
const suspiciousParticipants = [
  { name: 'Morgan Reed', email: 'morgan.reed@external-consulting.net' },
  { name: 'Taylor Chen', email: 'taylor.chen@vendor-services.com' },
  { name: 'Casey Morgan', email: 'casey.morgan@partner-group.io' },
  { name: 'Riley Johnson', email: 'riley.j@consulting-firm.net' },
  { name: 'Avery Williams', email: 'a.williams@external-audit.com' },
];

// Transcript templates for different meeting types
const normalTranscriptTemplates = [
  { text: "Good morning everyone, let's get started with our agenda.", riskScore: 3 },
  { text: "Can everyone see my screen? I'll share the quarterly numbers.", riskScore: 2 },
  { text: "Thanks for the update. Any questions from the team?", riskScore: 4 },
  { text: "Let's move on to the next item. Sarah, can you give us the status update?", riskScore: 3 },
  { text: "Great progress on the project. We're on track for the deadline.", riskScore: 2 },
  { text: "I'll send out the meeting notes after we wrap up.", riskScore: 3 },
  { text: "Any other business before we close?", riskScore: 2 },
  { text: "Thanks everyone, see you next week.", riskScore: 2 },
];

const suspiciousTranscriptTemplates = [
  {
    text: "I need access to the financial systems urgently. The CEO approved this but couldn't join the call.",
    riskScore: 82,
    riskIndicators: ['Authority bypass: "CEO approved"', 'Urgency tactic: "urgently"', 'Isolation tactic']
  },
  {
    text: "Can you share the admin credentials? We need to process this wire transfer before end of day.",
    riskScore: 91,
    riskIndicators: ['Credential request', 'Financial transaction', 'Urgency: "end of day"']
  },
  {
    text: "This is confidential - please don't mention this to anyone else on the team yet.",
    riskScore: 76,
    riskIndicators: ['Isolation tactic', 'Secrecy request', 'Social engineering pattern']
  },
  {
    text: "I've been authorized to request an emergency fund transfer. Can you process $150,000 to this account?",
    riskScore: 95,
    riskIndicators: ['Financial fraud attempt', 'Authority claim', 'Large sum request']
  },
  {
    text: "The usual process is too slow. Can you bypass the approval workflow just this once?",
    riskScore: 85,
    riskIndicators: ['Process bypass request', 'Urgency tactic', 'Social engineering']
  },
];

// Timeline generator function
function generateTimeline(
  meetingDate: Date,
  duration: number,
  riskScore: number,
  riskCategory: string,
  meetingId: string
): TimelineEvent[] {
  const events: TimelineEvent[] = [];
  const baseTime = new Date(meetingDate);

  // Meeting start
  events.push({
    id: `${meetingId}-tl-1`,
    timestamp: baseTime.toISOString(),
    type: 'meeting_start',
    title: 'Meeting started',
    description: 'DeepSafe bot joined automatically',
    severity: 'info',
  });

  if (riskCategory === 'low') {
    // Low risk: Simple meeting flow
    const endTime = new Date(baseTime.getTime() + duration * 60000);
    events.push({
      id: `${meetingId}-tl-2`,
      timestamp: endTime.toISOString(),
      type: 'meeting_end',
      title: 'Meeting ended normally',
      description: 'No security concerns detected',
      severity: 'success',
    });
  } else if (riskCategory === 'medium') {
    // Medium risk: Minor anomaly detected
    const anomalyTime = new Date(baseTime.getTime() + Math.floor(duration * 0.3) * 60000);
    events.push({
      id: `${meetingId}-tl-2`,
      timestamp: anomalyTime.toISOString(),
      type: 'anomaly_detected',
      title: 'Minor anomaly detected',
      description: `Video quality fluctuation detected (${Math.floor(riskScore * 0.5)}% confidence)`,
      riskScore: Math.floor(riskScore * 0.5),
      severity: 'warning',
    });

    const endTime = new Date(baseTime.getTime() + duration * 60000);
    events.push({
      id: `${meetingId}-tl-3`,
      timestamp: endTime.toISOString(),
      type: 'meeting_end',
      title: 'Meeting ended',
      description: 'Anomaly flagged for review',
      severity: 'info',
    });
  } else {
    // High/Critical risk: Full threat progression
    const anomalyTime = new Date(baseTime.getTime() + Math.floor(duration * 0.2) * 60000);
    events.push({
      id: `${meetingId}-tl-2`,
      timestamp: anomalyTime.toISOString(),
      type: 'anomaly_detected',
      title: 'Anomaly detected',
      description: `Video manipulation indicators detected (${Math.floor(riskScore * 0.6)}%)`,
      riskScore: Math.floor(riskScore * 0.6),
      severity: 'warning',
    });

    const escalationTime = new Date(baseTime.getTime() + Math.floor(duration * 0.4) * 60000);
    events.push({
      id: `${meetingId}-tl-3`,
      timestamp: escalationTime.toISOString(),
      type: 'risk_escalation',
      title: 'Risk escalation',
      description: `Deepfake confidence: ${riskScore}%, Social engineering patterns detected`,
      riskScore,
      severity: 'error',
    });

    const verificationTime = new Date(baseTime.getTime() + Math.floor(duration * 0.5) * 60000);
    events.push({
      id: `${meetingId}-tl-4`,
      timestamp: verificationTime.toISOString(),
      type: 'verification_triggered',
      title: 'Verification triggered',
      description: 'Identity verification initiated',
      severity: 'warning',
    });

    const fraudTime = new Date(baseTime.getTime() + Math.floor(duration * 0.6) * 60000);
    events.push({
      id: `${meetingId}-tl-5`,
      timestamp: fraudTime.toISOString(),
      type: 'fraud_confirmed',
      title: 'Threat confirmed',
      description: 'Suspicious participant removed from meeting',
      severity: 'error',
    });

    const resolvedTime = new Date(baseTime.getTime() + Math.floor(duration * 0.7) * 60000);
    events.push({
      id: `${meetingId}-tl-6`,
      timestamp: resolvedTime.toISOString(),
      type: 'incident_resolved',
      title: 'Incident resolved',
      description: 'Security team notified, forensic data preserved',
      severity: 'success',
    });
  }

  return events;
}

// Transcript generator function
function generateTranscript(
  meetingDate: Date,
  duration: number,
  _riskScore: number,
  riskCategory: string,
  hostName: string,
  hostId: string,
  meetingId: string
): TranscriptEntry[] {
  const entries: TranscriptEntry[] = [];
  const baseTime = new Date(meetingDate);

  if (riskCategory === 'low' || riskCategory === 'medium') {
    // Normal conversation
    normalTranscriptTemplates.slice(0, 5).forEach((template, i) => {
      const entryTime = new Date(baseTime.getTime() + (i * Math.floor(duration / 5)) * 60000);
      entries.push({
        id: `${meetingId}-tr-${i + 1}`,
        timestamp: entryTime.toISOString(),
        speaker: i % 2 === 0 ? hostName : 'Participant',
        speakerId: i % 2 === 0 ? hostId : `participant-${meetingId}-0`,
        text: template.text,
        riskScore: template.riskScore,
        isFlagged: false,
      });
    });
  } else {
    // High-risk conversation with suspicious entries
    const suspiciousParticipant = suspiciousParticipants[parseInt(meetingId) % suspiciousParticipants.length];

    // Opening normal message
    entries.push({
      id: `${meetingId}-tr-1`,
      timestamp: baseTime.toISOString(),
      speaker: hostName,
      speakerId: hostId,
      text: "Thanks for joining. Let's discuss the urgent matter you mentioned.",
      riskScore: 5,
      isFlagged: false,
    });

    // Suspicious messages
    const suspiciousTemplates = suspiciousTranscriptTemplates.slice(0, 2);
    suspiciousTemplates.forEach((template, i) => {
      const entryTime = new Date(baseTime.getTime() + ((i + 1) * Math.floor(duration / 4)) * 60000);
      entries.push({
        id: `${meetingId}-tr-${i + 2}`,
        timestamp: entryTime.toISOString(),
        speaker: suspiciousParticipant.name,
        speakerId: `suspicious-${meetingId}`,
        text: template.text,
        riskScore: template.riskScore,
        riskIndicators: template.riskIndicators,
        isFlagged: true,
      });
    });

    // Host questioning
    const questionTime = new Date(baseTime.getTime() + Math.floor(duration * 0.5) * 60000);
    entries.push({
      id: `${meetingId}-tr-4`,
      timestamp: questionTime.toISOString(),
      speaker: hostName,
      speakerId: hostId,
      text: "That's unusual. Let me verify this through our standard channels first.",
      riskScore: 8,
      isFlagged: false,
    });

    // System message about removal
    const systemTime = new Date(baseTime.getTime() + Math.floor(duration * 0.6) * 60000);
    entries.push({
      id: `${meetingId}-tr-5`,
      timestamp: systemTime.toISOString(),
      speaker: 'System Message',
      speakerId: 'system',
      text: `Participant '${suspiciousParticipant.name}' has been removed from the meeting due to security concerns.`,
      riskScore: 0,
      isFlagged: false,
    });
  }

  return entries;
}

// Forensics generator function
function generateForensics(
  _riskScore: number,
  riskCategory: string,
  meetingDate: Date
): ForensicEvidence | undefined {
  if (riskCategory === 'low') {
    return undefined; // No forensics needed for low-risk meetings
  }

  const isHighRisk = riskCategory === 'high' || riskCategory === 'critical';
  const deepfakeConfidence = isHighRisk ? 70 + Math.floor(Math.random() * 25) : 15 + Math.floor(Math.random() * 20);
  const voiceCloningConfidence = isHighRisk ? 50 + Math.floor(Math.random() * 30) : 5 + Math.floor(Math.random() * 15);

  const locations = ['Unknown Location', 'Eastern Europe', 'Southeast Asia', 'West Africa', 'South America'];
  const vpnProviders = ['NordVPN', 'ExpressVPN', 'Proton VPN', 'Private Internet Access', 'Unknown VPN'];

  return {
    videoAnalysis: {
      deepfakeConfidence,
      facialLandmarkInconsistencies: isHighRisk ? 8 + Math.floor(Math.random() * 10) : Math.floor(Math.random() * 3),
      microExpressionAnomalies: isHighRisk,
      lightingInconsistencies: isHighRisk ? 2 + Math.floor(Math.random() * 4) : 0,
      edgeArtifacts: isHighRisk,
      temporalInconsistencies: isHighRisk,
      evidenceSamples: isHighRisk ? [
        { frameNumber: 145 + Math.floor(Math.random() * 100), description: 'Facial landmark anomaly detected' },
        { frameNumber: 892 + Math.floor(Math.random() * 200), description: 'Lighting inconsistency in shadow regions' },
        { frameNumber: 1203 + Math.floor(Math.random() * 300), description: 'Digital edge artifacts detected' },
      ] : [],
    },
    audioAnalysis: {
      voiceCloningConfidence,
      spectralAnomalies: isHighRisk,
      prosodyAnomalies: isHighRisk,
      audioVideoDesync: isHighRisk ? 30 + Math.floor(Math.random() * 40) : Math.floor(Math.random() * 10),
      backgroundNoiseInconsistency: isHighRisk,
      voiceFingerprintMatch: !isHighRisk,
      evidenceSamples: isHighRisk ? [
        { timestamp: meetingDate.toISOString(), description: 'Suspicious segment with synthetic voice markers' },
      ] : [],
    },
    networkAnalysis: {
      ipAddress: isHighRisk ? `185.${Math.floor(Math.random() * 255)}.XXX.XXX` : `192.168.${Math.floor(Math.random() * 255)}.XXX`,
      location: isHighRisk ? locations[Math.floor(Math.random() * locations.length)] : 'San Francisco, CA',
      vpnDetected: isHighRisk,
      vpnProvider: isHighRisk ? vpnProviders[Math.floor(Math.random() * vpnProviders.length)] : undefined,
      deviceOS: isHighRisk ? 'Windows 11 Pro' : 'macOS Sonoma',
      browser: 'Chrome 120.0.6099.129',
      deviceFingerprint: isHighRisk ? `unknown-device-fp-${Math.floor(Math.random() * 1000)}` : `known-device-fp-${Math.floor(Math.random() * 100)}`,
      isKnownDevice: !isHighRisk,
      virtualCameraDetected: isHighRisk,
      virtualCameraName: isHighRisk ? 'OBS Virtual Camera' : undefined,
    },
    behavioralAnalysis: {
      socialEngineeringScore: isHighRisk ? 70 + Math.floor(Math.random() * 25) : 5 + Math.floor(Math.random() * 15),
      authorityBypass: isHighRisk ? 75 + Math.floor(Math.random() * 20) : Math.floor(Math.random() * 10),
      urgencyTactics: isHighRisk ? 65 + Math.floor(Math.random() * 30) : Math.floor(Math.random() * 10),
      isolationTactics: isHighRisk ? 60 + Math.floor(Math.random() * 30) : Math.floor(Math.random() * 5),
      credentialRequestRisk: isHighRisk ? 80 + Math.floor(Math.random() * 15) : Math.floor(Math.random() * 10),
      conversationPatternMatch: isHighRisk ? 85 + Math.floor(Math.random() * 12) : Math.floor(Math.random() * 15),
      knownAttackPatternSimilarity: isHighRisk
        ? `${85 + Math.floor(Math.random() * 12)}% similarity to known BEC/credential theft attacks`
        : 'No known attack patterns detected',
    },
  };
}

// Incident generator function
function generateIncident(
  meetingId: string,
  meetingDate: Date,
  duration: number,
  riskScore: number
): Meeting['incident'] {
  const incidentTypes: Array<'deepfake_impersonation' | 'social_engineering' | 'bec_attack' | 'credential_theft'> =
    ['deepfake_impersonation', 'social_engineering', 'bec_attack', 'credential_theft'];

  const incidentDescriptions: Record<string, string> = {
    deepfake_impersonation: 'Deepfake impersonation attempt detected and prevented',
    social_engineering: 'Social engineering attack blocked by DeepSafe',
    bec_attack: 'Business email compromise attempt intercepted',
    credential_theft: 'Credential theft attempt detected and blocked',
  };

  const type = incidentTypes[Math.floor(Math.random() * incidentTypes.length)];
  const detectionTime = new Date(meetingDate.getTime() + Math.floor(duration * 0.4) * 60000);
  const resolutionTime = new Date(meetingDate.getTime() + Math.floor(duration * 0.7) * 60000);
  const amountProtected = Math.floor(Math.random() * 450000) + 50000; // $50K - $500K

  return {
    id: `inc-${meetingId}`,
    type,
    description: incidentDescriptions[type],
    detectedAt: detectionTime.toISOString(),
    resolvedAt: resolutionTime.toISOString(),
    outcome: 'prevented',
    amountProtected,
    riskBreakdown: {
      audioRisk: Math.floor(riskScore * 0.6) + Math.floor(Math.random() * 20),
      videoRisk: Math.floor(riskScore * 0.8) + Math.floor(Math.random() * 15),
      credentialRisk: Math.floor(riskScore * 0.3) + Math.floor(Math.random() * 25),
    },
  };
}

function generateMeeting(index: number): Meeting {
  const date = new Date('2024-04-10');
  date.setDate(date.getDate() - Math.floor(index / 4)); // Spread across ~30 days
  date.setHours(9 + (index % 8), (index * 15) % 60, 0, 0);

  const host = hosts[index % hosts.length];
  const duration = Math.floor(Math.random() * 45) + 15;
  const meetingId = `${10000000 + index}`;

  // Use seeded randomness based on index for consistent risk scores
  const seedRandom = (seed: number) => {
    const x = Math.sin(seed * 9999) * 10000;
    return x - Math.floor(x);
  };

  const riskScore = seedRandom(index) > 0.85
    ? Math.floor(seedRandom(index + 1) * 40) + 60 // 15% high risk (60-100)
    : Math.floor(seedRandom(index + 2) * 30) + 5;  // 85% low risk (5-35)

  const riskCategory = riskScore >= 86 ? 'critical'
    : riskScore >= 61 ? 'high'
    : riskScore >= 31 ? 'medium'
    : 'low';

  const isCompromised = riskScore >= 70;
  const isHighRisk = riskCategory === 'high' || riskCategory === 'critical';

  // Generate timeline events
  const timeline = generateTimeline(date, duration, riskScore, riskCategory, meetingId);

  // Generate transcript
  const transcript = generateTranscript(date, duration, riskScore, riskCategory, host.name, host.id, meetingId);

  // Generate forensics for medium/high risk meetings
  const forensics = generateForensics(riskScore, riskCategory, date);

  // Generate incident for compromised meetings
  const incident = isCompromised ? generateIncident(meetingId, date, duration, riskScore) : undefined;

  // Build participants list
  const endTime = new Date(date.getTime() + duration * 60000);
  const participants: Meeting['participants'] = [
    {
      id: host.id,
      name: host.name,
      email: host.email,
      role: 'host',
      trustScore: 90 + Math.floor(seedRandom(index + 3) * 10),
      isFlagged: false,
      isVerified: true,
      joinTime: date.toISOString(),
      leaveTime: endTime.toISOString(),
      minutesInMeeting: duration,
    },
  ];

  // Add regular participants
  const numParticipants = Math.floor(seedRandom(index + 4) * 4) + 1;
  for (let i = 0; i < numParticipants; i++) {
    const participantJoinTime = new Date(date.getTime() + i * 60000);
    const participantLeaveTime = new Date(endTime.getTime() - (numParticipants - i) * 60000);
    participants.push({
      id: `participant-${index}-${i}`,
      name: `Participant ${i + 1}`,
      email: `participant${i + 1}@company.com`,
      role: 'participant',
      trustScore: 80 + Math.floor(seedRandom(index + 5 + i) * 20),
      isFlagged: false,
      isVerified: true,
      joinTime: participantJoinTime.toISOString(),
      leaveTime: participantLeaveTime.toISOString(),
      minutesInMeeting: Math.floor((participantLeaveTime.getTime() - participantJoinTime.getTime()) / 60000),
    });
  }

  // Add suspicious participant for high-risk meetings
  if (isHighRisk) {
    const suspiciousParticipant = suspiciousParticipants[index % suspiciousParticipants.length];
    const suspiciousJoinTime = new Date(date.getTime() + 2 * 60000);
    const suspiciousLeaveTime = new Date(date.getTime() + Math.floor(duration * 0.6) * 60000);
    participants.push({
      id: `suspicious-${meetingId}`,
      name: suspiciousParticipant.name,
      email: suspiciousParticipant.email,
      role: 'participant',
      trustScore: 10 + Math.floor(seedRandom(index + 10) * 15),
      isFlagged: true,
      isVerified: false,
      joinTime: suspiciousJoinTime.toISOString(),
      leaveTime: suspiciousLeaveTime.toISOString(),
      minutesInMeeting: Math.floor((suspiciousLeaveTime.getTime() - suspiciousJoinTime.getTime()) / 60000),
      riskBreakdown: incident?.riskBreakdown,
    });
  }

  return {
    id: meetingId,
    meetingName: meetingNames[index % meetingNames.length],
    meetingDate: date.toISOString(),
    duration,
    platform: ['zoom', 'teams', 'meet', 'webex'][index % 4] as Meeting['platform'],
    host: host.name,
    hostId: host.id,
    riskScore,
    riskCategory,
    isCompromised,
    status: 'completed',
    participants,
    timeline,
    transcript,
    forensics,
    incident,
  };
}

// Generate remaining meetings (126 total - 4 featured = 122 more)
const generatedMeetings = Array.from({ length: 122 }, (_, i) => generateMeeting(i));

export const allMeetings: Meeting[] = [...featuredMeetings, ...generatedMeetings];

// Get meeting by ID
export const getMeetingById = (id: string): Meeting | undefined => {
  return allMeetings.find(m => m.id === id);
};

// Filter meetings
export const filterMeetings = (
  meetings: Meeting[],
  filters: {
    startDate?: string;
    endDate?: string;
    riskCategory?: string;
    isCompromised?: boolean;
    searchQuery?: string;
  }
): Meeting[] => {
  return meetings.filter(meeting => {
    if (filters.startDate && new Date(meeting.meetingDate) < new Date(filters.startDate)) {
      return false;
    }
    if (filters.endDate && new Date(meeting.meetingDate) > new Date(filters.endDate)) {
      return false;
    }
    if (filters.riskCategory && filters.riskCategory !== 'all' && meeting.riskCategory !== filters.riskCategory) {
      return false;
    }
    if (filters.isCompromised !== undefined && meeting.isCompromised !== filters.isCompromised) {
      return false;
    }
    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase();
      return (
        meeting.meetingName.toLowerCase().includes(query) ||
        meeting.host.toLowerCase().includes(query) ||
        meeting.id.includes(query)
      );
    }
    return true;
  });
};
