import type { Participant } from '../types';

// Featured participants from mockups
export const featuredParticipants: Participant[] = [
  {
    id: 'jblake-1',
    name: 'Jordan Blake',
    email: 'jordan.blake@external.com',
    status: 'blacklisted',
    riskScore: 87,
    riskCategory: 'high',
    trustScore: 13,
    firstSeen: '2024-04-08T10:00:00Z',
    lastSeen: '2024-04-09T14:07:00Z',
    totalMeetings: 2,
    compromisedMeetings: 2,
    incidentRate: 100,
    threatIntelligence: {
      deepfakeTechnologyUsed: true,
      voiceCloningDetected: true,
      faceSwapDetected: true,
      socialEngineeringTactics: [
        'Authority impersonation',
        'Urgency creation',
        'Credential phishing',
      ],
      vpnUsage: true,
      vpnProvider: 'Proton VPN',
      originLocation: 'Bucharest, Romania',
      virtualCameraUsage: true,
      unknownDeviceFingerprint: true,
      multipleVerificationFailures: 3,
      knownThreatPatternMatch: 'BEC/CEO fraud attack patterns',
      threatMatchPercentage: 96,
    },
    blacklistDetails: {
      blacklistedAt: '2024-04-09T14:07:00Z',
      blacklistedBy: 'DeepSafe Automated Security System',
      reason: 'Multiple fraud attempts with deepfake technology',
      blockedAttributes: {
        email: 'nupur.agarwal@external.com',
        ipRange: '185.220.XXX.XXX/24',
        deviceFingerprint: 'unknown-device-fp-001',
      },
      actions: [
        'Cannot join any company meetings',
        'All invitations automatically declined',
        'IT Security notified of blacklist',
        'Reported to industry threat database',
      ],
      reportedToAuthorities: true,
      reportedToThreatDatabase: true,
    },
    meetingHistory: [
      {
        meetingId: '34190412',
        meetingName: 'CSO <> Employee Meeting',
        meetingDate: '2024-04-09T14:00:00Z',
        role: 'participant',
        riskScore: 87,
        minutesInMeeting: 16,
        riskBreakdown: {
          audioRisk: 67,
          videoRisk: 92,
          credentialRisk: 14,
        },
        incidentDetected: true,
        incidentType: 'Deepfake impersonation',
        outcome: 'Attack prevented',
      },
      {
        meetingId: '41930120',
        meetingName: 'FP&A Budget Review',
        meetingDate: '2024-04-08T10:00:00Z',
        role: 'participant',
        riskScore: 87,
        minutesInMeeting: 18,
        riskBreakdown: {
          audioRisk: 11,
          videoRisk: 3,
          credentialRisk: 2,
        },
        incidentDetected: true,
        incidentType: 'Social engineering',
        outcome: 'Attack prevented',
      },
    ],
  },
  {
    id: 'sarah-1',
    name: 'Sarah Chen',
    email: 'sarah.chen@company.com',
    status: 'verified',
    riskScore: 12,
    riskCategory: 'low',
    trustScore: 98,
    department: 'Finance',
    role: 'Finance Manager',
    firstSeen: '2024-01-15T09:00:00Z',
    lastSeen: '2024-04-10T16:00:00Z',
    totalMeetings: 47,
    compromisedMeetings: 0,
    incidentRate: 0,
    verification: {
      ssoVerified: true,
      ssoProvider: 'Okta',
      knownDevices: [
        { name: 'MacBook Pro', lastActive: '2024-04-10T16:00:00Z' },
        { name: 'iPhone 14', lastActive: '2024-04-10T12:00:00Z' },
      ],
      typicalLocations: ['San Francisco Office', 'Home (Verified)'],
      behavioralBiometricsConsistent: true,
      noDeepfakeIndicators: true,
    },
    meetingHistory: [
      {
        meetingId: '19308139',
        meetingName: 'Product Team Standup',
        meetingDate: '2024-04-08T09:00:00Z',
        role: 'host',
        riskScore: 13,
        minutesInMeeting: 15,
        riskBreakdown: {
          audioRisk: 5,
          videoRisk: 3,
          credentialRisk: 2,
        },
        incidentDetected: false,
      },
      {
        meetingId: '68419012',
        meetingName: 'Product Team Work Session',
        meetingDate: '2024-04-05T14:00:00Z',
        role: 'host',
        riskScore: 6,
        minutesInMeeting: 45,
        riskBreakdown: {
          audioRisk: 2,
          videoRisk: 1,
          credentialRisk: 1,
        },
        incidentDetected: false,
      },
    ],
  },
  {
    id: 'alex-1',
    name: 'Alex Thompson',
    email: 'alex.thompson@company.com',
    status: 'verified',
    riskScore: 8,
    riskCategory: 'low',
    trustScore: 95,
    department: 'Engineering',
    role: 'Senior Developer',
    firstSeen: '2023-06-01T09:00:00Z',
    lastSeen: '2024-04-10T17:30:00Z',
    totalMeetings: 89,
    compromisedMeetings: 0,
    incidentRate: 0,
    verification: {
      ssoVerified: true,
      ssoProvider: 'Okta',
      knownDevices: [
        { name: 'MacBook Pro M2', lastActive: '2024-04-10T17:30:00Z' },
        { name: 'iPhone 15 Pro', lastActive: '2024-04-10T15:00:00Z' },
      ],
      typicalLocations: ['San Francisco Office', 'Remote (Verified)'],
      behavioralBiometricsConsistent: true,
      noDeepfakeIndicators: true,
    },
  },
  {
    id: 'mike-1',
    name: 'Mike Williams',
    email: 'mike.williams@company.com',
    status: 'verified',
    riskScore: 10,
    riskCategory: 'low',
    trustScore: 96,
    department: 'Finance',
    role: 'CFO',
    firstSeen: '2022-03-15T09:00:00Z',
    lastSeen: '2024-04-10T18:00:00Z',
    totalMeetings: 156,
    compromisedMeetings: 0,
    incidentRate: 0,
    verification: {
      ssoVerified: true,
      ssoProvider: 'Okta',
      knownDevices: [
        { name: 'MacBook Pro', lastActive: '2024-04-10T18:00:00Z' },
        { name: 'iPad Pro', lastActive: '2024-04-10T10:00:00Z' },
        { name: 'iPhone 14 Pro Max', lastActive: '2024-04-10T17:00:00Z' },
      ],
      typicalLocations: ['San Francisco HQ', 'New York Office', 'Home'],
      behavioralBiometricsConsistent: true,
      noDeepfakeIndicators: true,
    },
  },
  {
    id: 'john-ext-1',
    name: 'John External',
    email: 'j.external@vendor.com',
    status: 'external',
    riskScore: 35,
    riskCategory: 'medium',
    trustScore: 65,
    department: 'External',
    role: 'Vendor Representative',
    firstSeen: '2024-03-01T10:00:00Z',
    lastSeen: '2024-04-09T11:00:00Z',
    totalMeetings: 5,
    compromisedMeetings: 0,
    incidentRate: 0,
  },
];

// Generate additional participants
const departments = ['Engineering', 'Sales', 'Marketing', 'Finance', 'HR', 'Operations', 'Legal', 'Product'];
const roles = ['Manager', 'Senior Analyst', 'Director', 'Associate', 'Lead', 'Specialist', 'Coordinator'];

function generateParticipant(index: number): Participant {
  const isVerified = Math.random() > 0.15; // 85% verified
  const isExternal = !isVerified && Math.random() > 0.5;
  const status = isVerified ? 'verified' : isExternal ? 'external' : 'guest';

  const riskScore = status === 'verified'
    ? Math.floor(Math.random() * 25) + 5  // 5-30 for verified
    : Math.floor(Math.random() * 40) + 20; // 20-60 for others

  const firstName = ['James', 'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'William', 'Sophia', 'Oliver', 'Isabella'][index % 10];
  const lastName = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'][Math.floor(index / 10) % 10];
  const name = `${firstName} ${lastName}`;

  return {
    id: `gen-participant-${index}`,
    name,
    email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${isExternal ? 'external.com' : 'company.com'}`,
    status,
    riskScore,
    riskCategory: riskScore >= 61 ? 'high' : riskScore >= 31 ? 'medium' : 'low',
    trustScore: 100 - riskScore,
    department: isExternal ? 'External' : departments[index % departments.length],
    role: isExternal ? 'Guest' : roles[index % roles.length],
    firstSeen: new Date(2024, 0, 1 + index).toISOString(),
    lastSeen: new Date(2024, 3, 10 - (index % 10)).toISOString(),
    totalMeetings: Math.floor(Math.random() * 50) + 5,
    compromisedMeetings: 0,
    incidentRate: 0,
    verification: isVerified ? {
      ssoVerified: true,
      ssoProvider: 'Okta',
      knownDevices: [{ name: 'Laptop', lastActive: new Date().toISOString() }],
      typicalLocations: ['Office'],
      behavioralBiometricsConsistent: true,
      noDeepfakeIndicators: true,
    } : undefined,
  };
}

// Generate more participants to reach ~1632 unique
const generatedParticipants = Array.from({ length: 1627 }, (_, i) => generateParticipant(i));

export const allParticipants: Participant[] = [...featuredParticipants, ...generatedParticipants];

// Get participant by ID
export const getParticipantById = (id: string): Participant | undefined => {
  return allParticipants.find(p => p.id === id);
};

// Filter participants
export const filterParticipants = (
  participants: Participant[],
  filters: {
    status?: string;
    riskCategory?: string;
    hasIncidents?: boolean;
    searchQuery?: string;
  }
): Participant[] => {
  return participants.filter(participant => {
    if (filters.status && filters.status !== 'all' && participant.status !== filters.status) {
      return false;
    }
    if (filters.riskCategory && filters.riskCategory !== 'all' && participant.riskCategory !== filters.riskCategory) {
      return false;
    }
    if (filters.hasIncidents !== undefined) {
      const hasIncidents = participant.compromisedMeetings > 0;
      if (hasIncidents !== filters.hasIncidents) {
        return false;
      }
    }
    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase();
      return (
        participant.name.toLowerCase().includes(query) ||
        participant.email.toLowerCase().includes(query) ||
        participant.id.includes(query)
      );
    }
    return true;
  });
};
