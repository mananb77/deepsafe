import type { WalkthroughStep } from '../types/walkthrough.types';

/**
 * Walkthrough Scenario - 15 Steps across 6 Phases
 * Guides users through all major DeepSafe dashboard features
 */
export const walkthroughScenario: WalkthroughStep[] = [
  // ============================================
  // Phase 1: Introduction (Steps 1-2)
  // ============================================
  {
    id: 1,
    name: 'Welcome to DeepSafe',
    phase: 'Introduction',
    type: 'modal',
    route: '/app/dashboard',
    duration: 0, // Manual advance only
    hotspots: [],
    modalContent: {
      title: 'Welcome to DeepSafe Dashboard',
      description: 'Learn how to monitor and protect your organization from deepfake attacks with this interactive walkthrough.',
      features: [
        'Interactive guided tour',
        'Hands-on exploration of features',
        'Takes approximately 5-7 minutes',
      ],
    },
  },
  {
    id: 2,
    name: 'Dashboard Overview',
    phase: 'Introduction',
    type: 'page',
    route: '/app/dashboard',
    duration: 15,
    highlight: 'full-page',
    instruction: 'This is your security command center. Click on the hotspots to learn more about each area.',
    hotspots: [
      {
        id: 'header-nav',
        type: 'info',
        anchor: '[data-walkthrough="header"]',
        tooltip: 'Navigate between dashboard sections',
        modalContent: {
          title: 'Navigation',
          description: 'Use the header navigation to switch between Overview, Meeting History, and Participant History. The theme toggle lets you switch between dark and light modes.',
        },
      },
      {
        id: 'metrics-area',
        type: 'data',
        anchor: '[data-walkthrough="metrics"]',
        tooltip: 'Key security metrics at a glance',
        modalContent: {
          title: 'Security Metrics',
          description: 'These cards show your organization\'s security posture at a glance - meetings monitored, compromised meetings detected, and money protected from fraud.',
        },
      },
      {
        id: 'chart-area',
        type: 'info',
        anchor: '[data-walkthrough="chart"]',
        tooltip: 'Track risk trends over time',
        modalContent: {
          title: 'Risk Trend Analysis',
          description: 'This chart shows your average risk score over time. Red markers indicate critical alerts. The threshold lines show warning (60%) and critical (85%) levels.',
        },
      },
    ],
  },

  // ============================================
  // Phase 2: Dashboard Metrics (Steps 3-5)
  // ============================================
  {
    id: 3,
    name: 'Security Metrics',
    phase: 'Dashboard Metrics',
    type: 'page',
    route: '/app/dashboard',
    duration: 18,
    focusElement: '[data-walkthrough="metrics"]',
    highlight: 'element',
    instruction: 'Click on any metric card to explore. Each card is interactive and shows trends.',
    hotspots: [
      {
        id: 'total-meetings',
        type: 'data',
        anchor: '[data-walkthrough="metric-total-meetings"]',
        tooltip: 'Total meetings monitored',
        modalContent: {
          title: 'Total Meetings',
          description: 'Shows the total number of video meetings analyzed by DeepSafe. Click to see the full meeting history. The trend indicator shows the change compared to the previous period.',
        },
      },
      {
        id: 'compromised',
        type: 'action',
        anchor: '[data-walkthrough="metric-compromised"]',
        tooltip: 'Compromised meetings detected',
        modalContent: {
          title: 'Compromised Meetings',
          description: 'Meetings where deepfake or social engineering attacks were detected. This is your most critical metric - any number above zero requires immediate attention.',
          features: ['Click to view all high-risk meetings', 'Filter by severity level'],
        },
      },
      {
        id: 'money-protected',
        type: 'info',
        anchor: '[data-walkthrough="metric-money"]',
        tooltip: 'Financial losses prevented',
        modalContent: {
          title: 'Money Protected',
          description: 'The total amount of financial losses prevented by detecting and stopping fraudulent requests during compromised meetings.',
        },
      },
    ],
  },
  {
    id: 4,
    name: 'Risk Trend Analysis',
    phase: 'Dashboard Metrics',
    type: 'page',
    route: '/app/dashboard',
    duration: 15,
    focusElement: '[data-walkthrough="chart"]',
    highlight: 'element',
    instruction: 'Hover over the chart to see daily risk scores and alert counts.',
    hotspots: [
      {
        id: 'chart-line',
        type: 'data',
        anchor: '[data-walkthrough="chart"]',
        tooltip: 'Interactive risk trend chart',
        modalContent: {
          title: 'Understanding Risk Trends',
          description: 'The blue line shows your average daily risk score. Higher scores indicate more suspicious activity detected.',
          features: [
            'Hover for detailed daily breakdown',
            'Red dots mark critical alerts',
            'Yellow threshold = Warning (60%)',
            'Red threshold = Critical (85%)',
          ],
        },
      },
    ],
  },
  {
    id: 5,
    name: 'Recent Incidents',
    phase: 'Dashboard Metrics',
    type: 'page',
    route: '/app/dashboard',
    duration: 12,
    focusElement: '[data-walkthrough="incidents"]',
    highlight: 'element',
    instruction: 'Click an incident to view full forensic details.',
    hotspots: [
      {
        id: 'incident-list',
        type: 'action',
        anchor: '[data-walkthrough="incidents"]',
        tooltip: 'Recent high-risk incidents',
        modalContent: {
          title: 'Recent Incidents',
          description: 'Shows the most recent security incidents detected across your meetings. Each incident includes the risk score, type of attack, and resolution status.',
          features: [
            'Click any incident to see full details',
            'View forensic evidence and timeline',
            'Track investigation status',
          ],
        },
      },
    ],
  },

  // ============================================
  // Phase 3: Meeting Analysis (Steps 6-8)
  // ============================================
  {
    id: 6,
    name: 'Meeting History',
    phase: 'Meeting Analysis',
    type: 'navigation',
    route: '/app/meetings',
    duration: 10,
    instruction: 'Click "Meeting History" in the navigation to explore all analyzed meetings.',
    triggerElement: '[data-walkthrough="nav-meetings"]',
    hotspots: [
      {
        id: 'meetings-nav',
        type: 'action',
        anchor: '[data-walkthrough="nav-meetings"]',
        tooltip: 'Go to Meeting History',
        modalContent: {
          title: 'Meeting History',
          description: 'The Meeting History page shows all meetings analyzed by DeepSafe. You can filter, sort, and search through your meeting records.',
        },
      },
    ],
  },
  {
    id: 7,
    name: 'Explore Meetings',
    phase: 'Meeting Analysis',
    type: 'page',
    route: '/app/meetings',
    duration: 18,
    focusElement: '[data-walkthrough="meetings-table"]',
    highlight: 'element',
    instruction: 'Try the filters to narrow down meetings. Click a high-risk meeting to see forensic details.',
    hotspots: [
      {
        id: 'filter-risk',
        type: 'info',
        anchor: '[data-walkthrough="filter-risk"]',
        tooltip: 'Filter by risk level',
        modalContent: {
          title: 'Risk Filters',
          description: 'Filter meetings by risk category: Critical (86-100%), High (61-85%), Medium (31-60%), or Low (0-30%). This helps prioritize your review of suspicious meetings.',
        },
      },
      {
        id: 'search-meetings',
        type: 'info',
        anchor: '[data-walkthrough="search-meetings"]',
        tooltip: 'Search by meeting name or ID',
        modalContent: {
          title: 'Search Meetings',
          description: 'Quickly find specific meetings by searching for meeting names, IDs, or participant names.',
        },
      },
      {
        id: 'meeting-row',
        type: 'action',
        anchor: '[data-walkthrough="meeting-row-0"]',
        tooltip: 'Click to view meeting details',
        modalContent: {
          title: 'Meeting Row',
          description: 'Each row shows a meeting\'s risk score, category, date, and status. Rows highlighted in red indicate high-risk meetings that need attention.',
          features: ['Click any row to see full details', 'View transcript and forensic evidence'],
        },
      },
    ],
  },
  {
    id: 8,
    name: 'Meeting Analysis',
    phase: 'Meeting Analysis',
    type: 'page',
    route: '/app/meetings/mtg-001', // Use first meeting as example
    duration: 25,
    instruction: 'Explore the tabs to see transcript, participants, and forensic evidence.',
    hotspots: [
      {
        id: 'meeting-tabs',
        type: 'info',
        anchor: '[data-walkthrough="meeting-tabs"]',
        tooltip: 'Navigate between meeting sections',
        modalContent: {
          title: 'Meeting Detail Tabs',
          description: 'Each meeting has 5 tabs: Overview, Transcript, Participants, Forensics, and Actions. Switch between them to explore different aspects of the meeting analysis.',
        },
      },
      {
        id: 'risk-score',
        type: 'data',
        anchor: '[data-walkthrough="risk-score"]',
        tooltip: 'Overall meeting risk assessment',
        modalContent: {
          title: 'Risk Assessment',
          description: 'The overall risk score combines video analysis (40%), audio analysis (30%), behavioral analysis (20%), and network analysis (10%) into a single metric.',
        },
      },
      {
        id: 'timeline',
        type: 'info',
        anchor: '[data-walkthrough="timeline"]',
        tooltip: 'Threat detection timeline',
        modalContent: {
          title: 'Detection Timeline',
          description: 'Shows the sequence of events from meeting start to incident resolution. Each event shows when anomalies were detected and how DeepSafe responded.',
        },
      },
      {
        id: 'forensics-tab',
        type: 'action',
        anchor: '[data-walkthrough="tab-forensics"]',
        tooltip: 'View forensic evidence',
        modalContent: {
          title: 'Forensic Analysis',
          description: 'The Forensics tab shows detailed evidence: deepfake confidence scores, voice cloning detection, network anomalies, and behavioral analysis.',
          features: [
            'Video: Facial landmarks, micro-expressions',
            'Audio: Voice fingerprinting, spectral analysis',
            'Network: VPN detection, virtual cameras',
            'Behavioral: Social engineering patterns',
          ],
        },
      },
    ],
  },

  // ============================================
  // Phase 4: Participant Intelligence (Steps 9-11)
  // ============================================
  {
    id: 9,
    name: 'Participants Page',
    phase: 'Participant Intelligence',
    type: 'navigation',
    route: '/app/participants',
    duration: 10,
    instruction: 'Click "Participant History" to view all meeting participants.',
    triggerElement: '[data-walkthrough="nav-participants"]',
    hotspots: [
      {
        id: 'participants-nav',
        type: 'action',
        anchor: '[data-walkthrough="nav-participants"]',
        tooltip: 'Go to Participant History',
        modalContent: {
          title: 'Participant History',
          description: 'Track all individuals who have joined your meetings. Monitor their risk scores, verify their identities, and flag suspicious participants.',
        },
      },
    ],
  },
  {
    id: 10,
    name: 'Participant Table',
    phase: 'Participant Intelligence',
    type: 'page',
    route: '/app/participants',
    duration: 18,
    focusElement: '[data-walkthrough="participants-table"]',
    highlight: 'element',
    instruction: 'Notice the status badges and risk scores. Click a participant for their full profile.',
    hotspots: [
      {
        id: 'status-filter',
        type: 'info',
        anchor: '[data-walkthrough="filter-status"]',
        tooltip: 'Filter by verification status',
        modalContent: {
          title: 'Participant Status',
          description: 'Participants can be: Verified (identity confirmed), Flagged (suspicious activity), Blacklisted (known threat), External (outside organization), or Guest (temporary access).',
        },
      },
      {
        id: 'participant-row',
        type: 'action',
        anchor: '[data-walkthrough="participant-row-0"]',
        tooltip: 'View participant profile',
        modalContent: {
          title: 'Participant Row',
          description: 'Each row shows the participant\'s risk score, number of meetings, incident count, and last seen date. Red highlighting indicates flagged or blacklisted participants.',
        },
      },
    ],
  },
  {
    id: 11,
    name: 'Participant Profile',
    phase: 'Participant Intelligence',
    type: 'page',
    route: '/app/participants/participant-002', // Use flagged participant
    duration: 20,
    instruction: 'Review threat intelligence and verification details.',
    hotspots: [
      {
        id: 'risk-panel',
        type: 'data',
        anchor: '[data-walkthrough="risk-panel"]',
        tooltip: 'Risk assessment summary',
        modalContent: {
          title: 'Risk Assessment',
          description: 'Shows the participant\'s overall risk score, total meetings attended, incident rate, and trust score. Higher risk and lower trust indicate potentially malicious actors.',
        },
      },
      {
        id: 'threat-intel',
        type: 'action',
        anchor: '[data-walkthrough="threat-intel"]',
        tooltip: 'Threat intelligence details',
        modalContent: {
          title: 'Threat Intelligence',
          description: 'For flagged or blacklisted participants, this panel shows detection indicators like deepfake technology usage, social engineering tactics, and known attack pattern matches.',
          features: [
            'Detection methods used',
            'VPN and virtual camera detection',
            'Social engineering tactics identified',
            'Attack pattern similarity score',
          ],
        },
      },
    ],
  },

  // ============================================
  // Phase 5: Customization (Steps 12-14)
  // ============================================
  {
    id: 12,
    name: 'Settings Tour',
    phase: 'Customization',
    type: 'navigation',
    route: '/app/settings',
    duration: 10,
    instruction: 'Open Settings to customize your DeepSafe experience.',
    triggerElement: '[data-walkthrough="nav-settings"]',
    hotspots: [
      {
        id: 'settings-nav',
        type: 'action',
        anchor: '[data-walkthrough="nav-settings"]',
        tooltip: 'Configure your preferences',
        modalContent: {
          title: 'Settings',
          description: 'Customize notification preferences, alert thresholds, integrations, and display preferences to match your workflow.',
        },
      },
    ],
  },
  {
    id: 13,
    name: 'Notification Preferences',
    phase: 'Customization',
    type: 'page',
    route: '/app/settings',
    duration: 15,
    focusElement: '[data-walkthrough="notifications"]',
    highlight: 'element',
    instruction: 'Configure how and when you receive security alerts.',
    hotspots: [
      {
        id: 'alert-threshold',
        type: 'data',
        anchor: '[data-walkthrough="alert-threshold"]',
        tooltip: 'Set alert sensitivity',
        modalContent: {
          title: 'Alert Threshold',
          description: 'Adjust the risk score threshold that triggers alerts. Lower values mean more sensitive detection (more alerts), higher values reduce alert noise.',
          features: [
            '40%: Alert on medium+ risk',
            '60%: Alert on high+ risk',
            '85%: Alert only on critical',
          ],
        },
      },
      {
        id: 'email-notifications',
        type: 'info',
        anchor: '[data-walkthrough="email-toggles"]',
        tooltip: 'Email notification settings',
        modalContent: {
          title: 'Email Notifications',
          description: 'Control which events trigger email notifications: critical incidents, daily summaries, weekly reports, and system updates.',
        },
      },
    ],
  },
  {
    id: 14,
    name: 'Integrations',
    phase: 'Customization',
    type: 'page',
    route: '/app/settings',
    duration: 15,
    focusElement: '[data-walkthrough="integrations"]',
    highlight: 'element',
    instruction: 'Connect your video platforms for automatic monitoring.',
    hotspots: [
      {
        id: 'platform-cards',
        type: 'action',
        anchor: '[data-walkthrough="integrations"]',
        tooltip: 'Connect video platforms',
        modalContent: {
          title: 'Platform Integrations',
          description: 'Connect Zoom, Microsoft Teams, Google Meet, and Slack for automatic meeting monitoring. DeepSafe analyzes meetings in real-time once connected.',
          features: [
            'One-click OAuth connection',
            'Automatic meeting import',
            'Real-time analysis during calls',
            'Webhook notifications to Slack',
          ],
        },
      },
    ],
  },

  // ============================================
  // Phase 6: Completion (Step 15)
  // ============================================
  {
    id: 15,
    name: 'Walkthrough Complete',
    phase: 'Completion',
    type: 'modal',
    route: '/app/dashboard',
    duration: 0, // Manual only
    hotspots: [],
    modalContent: {
      title: "You're Ready!",
      description: 'Congratulations! You\'ve completed the DeepSafe dashboard walkthrough. You now know how to monitor meetings, analyze threats, and configure your security settings.',
      metrics: { stepsCompleted: 14, featuresExplored: 25 },
      nextSteps: [
        'Review your first high-risk meeting',
        'Configure your alert thresholds',
        'Connect your video platforms',
        'Explore participant profiles',
      ],
      helpLink: '/app/support',
    },
  },
];

export const WALKTHROUGH_TOTAL_STEPS = walkthroughScenario.length;

// Get step by ID
export const getStepById = (id: number): WalkthroughStep | undefined => {
  return walkthroughScenario.find((step) => step.id === id);
};

// Get steps by phase
export const getStepsByPhase = (phase: string): WalkthroughStep[] => {
  return walkthroughScenario.filter((step) => step.phase === phase);
};

// Get all phase names
export const getPhases = (): string[] => {
  return [...new Set(walkthroughScenario.map((step) => step.phase))];
};
