import type { ForensicEvidence } from '../../../types/meeting.types';

/**
 * Forensic Evidence Data for Demo Scenario
 * Matches the ForensicEvidence interface from src/types/meeting.types.ts
 * Based on PRD Appendix 15.2
 */

export const demoForensicData: ForensicEvidence = {
  videoAnalysis: {
    deepfakeConfidence: 92,
    facialLandmarkInconsistencies: 12,
    microExpressionAnomalies: true,
    lightingInconsistencies: 3,
    edgeArtifacts: true,
    temporalInconsistencies: true,
    evidenceSamples: [
      {
        frameNumber: 145,
        description: 'Facial landmark anomaly detected - unnatural eye movement pattern during speech',
      },
      {
        frameNumber: 892,
        description: 'Lighting inconsistency in shadow regions - left side of face shows impossible shadow angle',
      },
      {
        frameNumber: 1203,
        description: 'Digital edge artifacts detected around jawline - pixelation consistent with deepfake generation',
      },
      {
        frameNumber: 1567,
        description: 'Temporal inconsistency - frame interpolation artifacts detected during head turn',
      },
      {
        frameNumber: 2101,
        description: 'Micro-expression anomaly - emotional expression does not match vocal tone',
      },
    ],
  },

  audioAnalysis: {
    voiceCloningConfidence: 67,
    spectralAnomalies: true,
    prosodyAnomalies: true,
    audioVideoDesync: 42, // 42ms desync
    backgroundNoiseInconsistency: true,
    voiceFingerprintMatch: false,
    evidenceSamples: [
      {
        timestamp: '00:01:38',
        description: 'Synthetic voice markers detected in urgency phrase - spectral analysis shows unnatural formant transitions',
      },
      {
        timestamp: '00:02:28',
        description: 'Prosody pattern inconsistent with baseline - emphasis patterns do not match known speech patterns of David Mitchell',
      },
      {
        timestamp: '00:03:15',
        description: 'Background noise discontinuity - ambient noise signature changes mid-sentence',
      },
      {
        timestamp: '00:03:42',
        description: 'Voice fingerprint mismatch - spectral centroid deviation exceeds acceptable threshold',
      },
    ],
  },

  networkAnalysis: {
    ipAddress: '185.220.XXX.XXX',
    location: 'Bucharest, Romania',
    vpnDetected: true,
    vpnProvider: 'NordVPN',
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
    knownAttackPatternSimilarity: '96% similarity to known BEC/credential theft attacks targeting financial executives',
  },
};

/**
 * Risk Score Breakdown for Modal Display
 * Based on PRD Section 7.1 weights
 */
export const riskScoreBreakdown = {
  weights: {
    video: 0.40,
    audio: 0.30,
    behavioral: 0.20,
    network: 0.10,
  },
  scores: {
    video: 92,      // deepfakeConfidence
    audio: 67,      // voiceCloningConfidence
    behavioral: 89, // socialEngineeringScore
    network: 95,    // Derived from VPN + virtual camera + unknown device
  },
  calculated: {
    videoContribution: 92 * 0.40,    // 36.8
    audioContribution: 67 * 0.30,    // 20.1
    behavioralContribution: 89 * 0.20, // 17.8
    networkContribution: 95 * 0.10,   // 9.5
    total: 84.2, // Rounds to 84%
  },
};

/**
 * Evidence for each analysis category
 * Used for detailed forensic modal displays
 */
export const evidenceDetails = {
  video: {
    title: 'Video Analysis',
    weight: '40%',
    confidence: 92,
    summary: 'High confidence deepfake detected with multiple visual artifacts',
    findings: [
      {
        category: 'Facial Landmarks',
        severity: 'critical',
        description: '12 inconsistencies detected in facial landmark positions, particularly around eyes and mouth during speech',
      },
      {
        category: 'Micro-expressions',
        severity: 'high',
        description: 'Emotional expressions do not correlate with speech content - detected unnatural expression timing',
      },
      {
        category: 'Lighting',
        severity: 'medium',
        description: '3 lighting inconsistencies where shadow directions do not match the environment',
      },
      {
        category: 'Edge Artifacts',
        severity: 'high',
        description: 'Digital compression artifacts visible around face boundaries, consistent with face-swap technology',
      },
      {
        category: 'Temporal Consistency',
        severity: 'critical',
        description: 'Frame-to-frame inconsistencies detected during rapid movements, indicating generated frames',
      },
    ],
  },
  audio: {
    title: 'Audio Analysis',
    weight: '30%',
    confidence: 67,
    summary: 'Voice cloning detected with spectral and prosodic anomalies',
    findings: [
      {
        category: 'Voice Cloning',
        severity: 'high',
        description: '67% confidence of synthetic voice generation based on spectral analysis',
      },
      {
        category: 'Prosody',
        severity: 'medium',
        description: 'Speech rhythm and emphasis patterns deviate from known baseline samples of the claimed speaker',
      },
      {
        category: 'A/V Sync',
        severity: 'medium',
        description: '42ms audio-video desynchronization detected, exceeding normal latency variance',
      },
      {
        category: 'Background Noise',
        severity: 'low',
        description: 'Ambient noise signature shows discontinuities suggesting audio splicing or generation',
      },
    ],
  },
  network: {
    title: 'Network Analysis',
    weight: '10%',
    confidence: 95,
    summary: 'Multiple network red flags including VPN and virtual camera',
    findings: [
      {
        category: 'VPN Usage',
        severity: 'high',
        description: 'Connection routed through NordVPN exit node in Romania - not consistent with claimed location',
      },
      {
        category: 'Virtual Camera',
        severity: 'critical',
        description: 'OBS Virtual Camera detected instead of physical webcam - enables deepfake video injection',
      },
      {
        category: 'Device Recognition',
        severity: 'high',
        description: 'Device fingerprint not recognized - this device has never been used by David Mitchell',
      },
      {
        category: 'Geolocation',
        severity: 'medium',
        description: 'IP geolocation (Bucharest, Romania) inconsistent with user profile (San Francisco, CA)',
      },
    ],
  },
  behavioral: {
    title: 'Behavioral Analysis',
    weight: '20%',
    confidence: 89,
    summary: 'Strong match to known social engineering attack patterns',
    findings: [
      {
        category: 'Pattern Match',
        severity: 'critical',
        description: '96% similarity to known BEC (Business Email Compromise) attack patterns',
      },
      {
        category: 'Authority Bypass',
        severity: 'critical',
        description: 'Multiple attempts to bypass normal authorization procedures using claimed authority',
      },
      {
        category: 'Urgency Tactics',
        severity: 'high',
        description: 'Artificial urgency created through deadline pressure and fear of missed opportunity',
      },
      {
        category: 'Isolation',
        severity: 'high',
        description: 'Explicit requests for secrecy and to exclude normal oversight parties',
      },
      {
        category: 'Credential Request',
        severity: 'critical',
        description: 'Direct request for financial transaction authorization - $250,000 wire transfer',
      },
    ],
  },
};

/**
 * Get severity color for UI display
 */
export const getSeverityColor = (severity: 'critical' | 'high' | 'medium' | 'low'): string => {
  const colors = {
    critical: '#D64545',
    high: '#FF6B6B',
    medium: '#F5A623',
    low: '#FFC857',
  };
  return colors[severity];
};

/**
 * Get overall risk assessment summary
 */
export const getRiskAssessmentSummary = () => ({
  overallScore: 84,
  riskLevel: 'critical' as const,
  primaryThreat: 'Deepfake Impersonation',
  secondaryThreat: 'Social Engineering',
  confidenceLevel: 'High',
  recommendation: 'Immediate threat removal and incident documentation',
  amountAtRisk: 250000,
});
