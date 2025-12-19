// DeepSafe detection features and capabilities

export interface DetectionPillar {
  id: string;
  title: string;
  weight: number;
  description: string;
  capabilities: string[];
  icon: 'video' | 'audio' | 'behavior' | 'network';
}

export interface RiskThreshold {
  level: 'alert' | 'verify' | 'intervene';
  threshold: number;
  label: string;
  description: string;
  color: string;
}

export const detectionPillars: DetectionPillar[] = [
  {
    id: 'video',
    title: 'Video Analysis',
    weight: 40,
    description: 'AI-powered detection of synthetic video and manipulated footage',
    capabilities: [
      'Deepfake confidence scoring',
      'Facial landmark inconsistency detection',
      'Micro-expression anomaly detection',
      'Lighting and edge artifact analysis',
    ],
    icon: 'video',
  },
  {
    id: 'audio',
    title: 'Audio Analysis',
    weight: 30,
    description: 'Voice authentication and synthetic audio detection',
    capabilities: [
      'Voice cloning detection',
      'Spectral anomaly identification',
      'Audio-video sync verification',
      'Voice fingerprint matching',
    ],
    icon: 'audio',
  },
  {
    id: 'behavioral',
    title: 'Behavioral Analysis',
    weight: 20,
    description: 'Pattern recognition for social engineering tactics',
    capabilities: [
      'Social engineering pattern detection',
      'Authority bypass recognition',
      'Urgency tactic identification',
      'Isolation behavior flagging',
    ],
    icon: 'behavior',
  },
  {
    id: 'network',
    title: 'Network Analysis',
    weight: 10,
    description: 'Environmental and device verification',
    capabilities: [
      'VPN/proxy detection',
      'Virtual camera identification',
      'Device fingerprinting',
      'Geolocation verification',
    ],
    icon: 'network',
  },
];

export const riskThresholds: RiskThreshold[] = [
  {
    level: 'alert',
    threshold: 40,
    label: 'Alert',
    description: 'Initial anomaly detected, monitoring increased',
    color: '#F5A623',
  },
  {
    level: 'verify',
    threshold: 65,
    label: 'Verify',
    description: 'Secondary authentication triggered',
    color: '#FF8C00',
  },
  {
    level: 'intervene',
    threshold: 85,
    label: 'Intervene',
    description: 'Active threat response initiated',
    color: '#D64545',
  },
];

export const protectionMetrics = {
  responseTime: '< 2 seconds',
  accuracy: '99.2%',
  falsePositiveRate: '< 0.1%',
  platformsSupported: ['Zoom', 'Microsoft Teams', 'Google Meet', 'Slack'],
};
