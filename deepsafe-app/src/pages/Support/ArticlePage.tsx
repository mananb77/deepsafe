import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Breadcrumbs,
  Link as MuiLink,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  ArrowForward as ArrowIcon,
  PlayCircle as GetStartedIcon,
  Psychology as RiskScoreIcon,
  BugReport as IncidentIcon,
  Code as ApiIcon,
  Schedule as TimeIcon,
  MenuBook as ReadIcon,
} from '@mui/icons-material';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useThemeMode } from '../../context/ThemeContext';
import { brandColors } from '../../theme/colors';

// Support article content
interface ArticleSection {
  title: string;
  content: string;
  bullets?: string[];
  code?: string;
}

interface SupportArticle {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  readTime: string;
  category: string;
  sections: ArticleSection[];
}

const supportArticles: Record<string, SupportArticle> = {
  'getting-started': {
    id: 'getting-started',
    title: 'Getting Started with DeepSafe',
    description: 'Learn the basics of DeepSafe and set up your first meeting protection.',
    icon: <GetStartedIcon />,
    readTime: '8 min read',
    category: 'Onboarding',
    sections: [
      {
        title: 'Welcome to DeepSafe',
        content: 'DeepSafe is an enterprise-grade AI security platform designed to protect your video conferences from deepfakes, impersonation attacks, and unauthorized participants. This guide will help you get up and running in minutes.',
      },
      {
        title: 'Step 1: Connect Your Platforms',
        content: 'Start by connecting your video conferencing platforms. DeepSafe supports the following integrations:',
        bullets: [
          'Zoom - Full integration with real-time monitoring and recording analysis',
          'Microsoft Teams - Enterprise SSO support with admin consent workflows',
          'Google Meet - Workspace integration with automatic meeting detection',
          'Slack - Huddles monitoring and alert notifications',
        ],
      },
      {
        title: 'Step 2: Configure Your Alert Preferences',
        content: 'Navigate to Settings > Notification Settings to customize how you receive alerts. We recommend:',
        bullets: [
          'Enable Critical Incidents for immediate email alerts on high-risk detections',
          'Set your Alert Threshold to 70% for balanced sensitivity',
          'Enable In-App Notifications to see real-time updates in the dashboard',
          'Configure Daily Summary emails for a comprehensive overview',
        ],
      },
      {
        title: 'Step 3: Schedule Your First Protected Meeting',
        content: 'Once your platforms are connected, DeepSafe automatically monitors all meetings. You can view monitored meetings in real-time from the Dashboard or review historical data in Meeting History.',
      },
      {
        title: 'Step 4: Review Your First Detection',
        content: 'When DeepSafe detects suspicious activity, you\'ll receive an alert with detailed forensic information. Click on any alert to see:',
        bullets: [
          'Risk score breakdown with confidence intervals',
          'Forensic timeline of detected anomalies',
          'Participant analysis with behavioral markers',
          'AI-generated recommendations for response',
        ],
      },
      {
        title: 'Best Practices',
        content: 'To get the most out of DeepSafe:',
        bullets: [
          'Review the Dashboard daily to understand your organization\'s risk trends',
          'Train your team on how to respond to deepfake alerts',
          'Regularly audit participant access and permissions',
          'Keep your integrations up to date for best detection accuracy',
        ],
      },
    ],
  },
  'risk-scores': {
    id: 'risk-scores',
    title: 'Understanding Risk Scores',
    description: 'Learn how our AI calculates and presents threat confidence levels.',
    icon: <RiskScoreIcon />,
    readTime: '6 min read',
    category: 'Technical',
    sections: [
      {
        title: 'How Risk Scores Work',
        content: 'DeepSafe\'s risk scoring system uses multiple AI models to analyze video, audio, and behavioral patterns in real-time. Each meeting and participant receives a risk score from 0-100%, representing our confidence in detecting synthetic or manipulated content.',
      },
      {
        title: 'Risk Score Breakdown',
        content: 'Risk scores are composed of several weighted factors:',
        bullets: [
          'Visual Analysis (40%) - Facial movement patterns, blinking frequency, micro-expressions',
          'Audio Analysis (30%) - Voice consistency, speech patterns, audio artifacts',
          'Behavioral Analysis (20%) - Interaction patterns, response timing, contextual awareness',
          'Environmental Signals (10%) - Background consistency, lighting changes, metadata analysis',
        ],
      },
      {
        title: 'Risk Levels Explained',
        content: 'We categorize risk scores into four levels:',
        bullets: [
          'Low (0-40%) - Normal meeting activity, no significant anomalies detected',
          'Medium (41-60%) - Minor anomalies detected, may warrant review but typically benign',
          'High (61-85%) - Significant anomalies detected, immediate review recommended',
          'Critical (86-100%) - High confidence of synthetic content, immediate action required',
        ],
      },
      {
        title: 'Confidence Intervals',
        content: 'Each risk score includes a confidence interval showing the statistical reliability of our detection. A narrow interval (±5%) indicates high certainty, while a wider interval (±15%) suggests more uncertainty in the detection.',
      },
      {
        title: 'False Positives',
        content: 'Our AI is trained to minimize false positives, but certain conditions can trigger elevated scores:',
        bullets: [
          'Poor video quality or low bandwidth connections',
          'Virtual backgrounds or heavy video filters',
          'Screen sharing with face-in-corner mode',
          'Unusual lighting conditions',
        ],
      },
      {
        title: 'Adjusting Sensitivity',
        content: 'You can adjust your alert threshold in Settings > Notification Settings. Lower thresholds increase sensitivity but may generate more alerts. We recommend starting at 70% and adjusting based on your organization\'s needs.',
      },
    ],
  },
  'incident-response': {
    id: 'incident-response',
    title: 'Incident Response Guide',
    description: 'Best practices for handling detected threats and false positives.',
    icon: <IncidentIcon />,
    readTime: '10 min read',
    category: 'Security',
    sections: [
      {
        title: 'When a Detection Occurs',
        content: 'When DeepSafe detects potential synthetic content, it\'s important to follow a structured response process. This guide outlines best practices for investigating and responding to alerts.',
      },
      {
        title: 'Immediate Actions (First 5 Minutes)',
        content: 'Upon receiving a critical alert:',
        bullets: [
          'Review the alert details in the DeepSafe dashboard',
          'Note the risk score, confidence interval, and detection type',
          'If the meeting is ongoing, consider enabling enhanced monitoring',
          'Do NOT immediately confront the suspected participant',
        ],
      },
      {
        title: 'Investigation Phase',
        content: 'Conduct a thorough investigation before taking action:',
        bullets: [
          'Review the forensic timeline for the full context of detections',
          'Compare the participant\'s behavior to their historical patterns',
          'Check if technical factors might explain the detection (poor connection, filters)',
          'Cross-reference with other security systems if available',
        ],
      },
      {
        title: 'Verification Steps',
        content: 'To verify a potential deepfake:',
        bullets: [
          'Request a secondary verification call with the participant',
          'Ask contextual questions only the real person would know',
          'Use out-of-band communication (phone call, text) to confirm identity',
          'Review meeting recording with enhanced forensic tools',
        ],
      },
      {
        title: 'Response Actions',
        content: 'Based on your investigation, take appropriate action:',
        bullets: [
          'False Positive: Mark as reviewed, update detection feedback',
          'Confirmed Threat: Remove participant, document incident, notify security team',
          'Uncertain: Escalate to security leadership for decision',
        ],
      },
      {
        title: 'Post-Incident Documentation',
        content: 'After resolving an incident:',
        bullets: [
          'Complete the incident report in DeepSafe',
          'Document all actions taken and their outcomes',
          'Share learnings with your security team',
          'Update response procedures if needed',
        ],
      },
      {
        title: 'Reporting to Authorities',
        content: 'For confirmed attacks, consider reporting to relevant authorities. DeepSafe can generate forensic reports suitable for legal proceedings. Contact our enterprise support team for assistance with law enforcement coordination.',
      },
    ],
  },
  'api-documentation': {
    id: 'api-documentation',
    title: 'API Documentation',
    description: 'Integrate DeepSafe with your existing security infrastructure.',
    icon: <ApiIcon />,
    readTime: '12 min read',
    category: 'Developer',
    sections: [
      {
        title: 'API Overview',
        content: 'The DeepSafe API allows you to integrate our detection capabilities into your existing security infrastructure. All API endpoints use REST architecture and return JSON responses.',
      },
      {
        title: 'Authentication',
        content: 'All API requests require authentication using your API key. Include the key in the Authorization header:',
        code: `curl -X GET "https://api.deepsafe.ai/v1/meetings" \\
  -H "Authorization: Bearer ds_live_sk_xxxxx" \\
  -H "Content-Type: application/json"`,
      },
      {
        title: 'Core Endpoints',
        content: 'The following endpoints are available:',
        bullets: [
          'GET /v1/meetings - List all monitored meetings',
          'GET /v1/meetings/{id} - Get meeting details and risk analysis',
          'GET /v1/participants - List all analyzed participants',
          'GET /v1/participants/{id} - Get participant risk profile',
          'GET /v1/alerts - List all alerts and detections',
          'POST /v1/alerts/{id}/feedback - Submit detection feedback',
        ],
      },
      {
        title: 'Webhook Integration',
        content: 'Configure webhooks to receive real-time notifications:',
        code: `POST /v1/webhooks
{
  "url": "https://your-server.com/deepsafe-webhook",
  "events": ["detection.critical", "detection.high", "meeting.ended"],
  "secret": "your-webhook-secret"
}`,
      },
      {
        title: 'Rate Limits',
        content: 'API rate limits vary by plan:',
        bullets: [
          'Starter: 100 requests/minute',
          'Professional: 500 requests/minute',
          'Enterprise: Custom limits available',
        ],
      },
      {
        title: 'SDKs and Libraries',
        content: 'Official SDKs are available for popular languages:',
        bullets: [
          'Python: pip install deepsafe',
          'Node.js: npm install @deepsafe/sdk',
          'Go: go get github.com/deepsafe/go-sdk',
          'Ruby: gem install deepsafe',
        ],
      },
      {
        title: 'Example: Real-time Monitoring',
        content: 'Subscribe to real-time detection events:',
        code: `import { DeepSafe } from '@deepsafe/sdk';

const client = new DeepSafe('ds_live_sk_xxxxx');

client.onDetection((event) => {
  if (event.riskScore >= 85) {
    console.log('Critical detection:', event);
    // Trigger your incident response workflow
  }
});

client.connect();`,
      },
    ],
  },
};

// Related articles mapping
const relatedArticles: Record<string, string[]> = {
  'getting-started': ['risk-scores', 'incident-response'],
  'risk-scores': ['getting-started', 'incident-response'],
  'incident-response': ['risk-scores', 'api-documentation'],
  'api-documentation': ['getting-started', 'incident-response'],
};

export const ArticlePage: React.FC = () => {
  const { isDark } = useThemeMode();
  const { articleId } = useParams<{ articleId: string }>();
  const navigate = useNavigate();

  const article = articleId ? supportArticles[articleId] : null;

  if (!article) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h5" sx={{ mb: 2 }}>Article not found</Typography>
        <Button
          variant="contained"
          startIcon={<BackIcon />}
          onClick={() => navigate('/support')}
        >
          Back to Support
        </Button>
      </Box>
    );
  }

  const related = relatedArticles[articleId || ''] || [];

  return (
    <Box
      sx={{
        p: { xs: 2, md: 4 },
        maxWidth: 900,
        mx: 'auto',
      }}
    >
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <MuiLink
          component={Link}
          to="/support"
          underline="hover"
          sx={{
            color: 'text.secondary',
            '&:hover': { color: brandColors.primary.signalTeal },
          }}
        >
          Support
        </MuiLink>
        <MuiLink
          component={Link}
          to="/support"
          underline="hover"
          sx={{
            color: 'text.secondary',
            '&:hover': { color: brandColors.primary.signalTeal },
          }}
        >
          Quick Help
        </MuiLink>
        <Typography color="text.primary">{article.title}</Typography>
      </Breadcrumbs>

      {/* Back Button */}
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate('/support')}
        sx={{
          mb: 3,
          color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
          '&:hover': {
            backgroundColor: isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.04)',
          },
        }}
      >
        Back to Support
      </Button>

      {/* Article Header */}
      <Paper
        sx={{
          p: 4,
          mb: 4,
          background: isDark
            ? 'linear-gradient(135deg, rgba(31, 60, 136, 0.3) 0%, rgba(31, 182, 166, 0.2) 100%)'
            : 'linear-gradient(135deg, rgba(31, 60, 136, 0.1) 0%, rgba(31, 182, 166, 0.08) 100%)',
          backdropFilter: 'blur(10px)',
          border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.06)'}`,
          borderRadius: 3,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 3 }}>
          <Box
            sx={{
              p: 2,
              borderRadius: 3,
              background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: 32,
              '& svg': { fontSize: 32 },
            }}
          >
            {article.icon}
          </Box>
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
              <Chip
                label={article.category}
                size="small"
                sx={{
                  backgroundColor: `${brandColors.primary.signalTeal}20`,
                  color: brandColors.primary.signalTeal,
                  fontWeight: 500,
                }}
              />
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <TimeIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary">
                  {article.readTime}
                </Typography>
              </Box>
            </Box>
            <Typography
              variant="h4"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 700,
                mb: 1,
              }}
            >
              {article.title}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {article.description}
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Article Content */}
      <Paper
        sx={{
          p: 4,
          mb: 4,
          background: isDark
            ? 'linear-gradient(180deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.6) 100%)'
            : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.8) 100%)',
          backdropFilter: 'blur(10px)',
          border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
          borderRadius: 3,
        }}
      >
        {article.sections.map((section, index) => (
          <Box key={index} sx={{ mb: index < article.sections.length - 1 ? 4 : 0 }}>
            <Typography
              variant="h5"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                mb: 2,
                color: brandColors.primary.signalTeal,
              }}
            >
              {section.title}
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                lineHeight: 1.8,
                mb: section.bullets || section.code ? 2 : 0,
              }}
            >
              {section.content}
            </Typography>
            {section.bullets && (
              <List sx={{ pl: 1 }}>
                {section.bullets.map((bullet, bulletIndex) => (
                  <ListItem key={bulletIndex} sx={{ py: 0.75, px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <ArrowIcon sx={{ fontSize: 18, color: brandColors.primary.signalTeal }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={bullet}
                      primaryTypographyProps={{
                        variant: 'body1',
                        sx: {
                          color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                          lineHeight: 1.6,
                        },
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            )}
            {section.code && (
              <Box
                sx={{
                  mt: 2,
                  p: 3,
                  borderRadius: 2,
                  backgroundColor: isDark ? 'rgba(0, 0, 0, 0.4)' : 'rgba(0, 0, 0, 0.05)',
                  border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
                  overflowX: 'auto',
                }}
              >
                <Typography
                  component="pre"
                  sx={{
                    fontFamily: '"JetBrains Mono", monospace',
                    fontSize: '0.9rem',
                    color: isDark ? brandColors.primary.signalTeal : brandColors.primary.deepSafeBlue,
                    m: 0,
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    lineHeight: 1.6,
                  }}
                >
                  {section.code}
                </Typography>
              </Box>
            )}
            {index < article.sections.length - 1 && (
              <Divider sx={{ mt: 4, borderColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)' }} />
            )}
          </Box>
        ))}
      </Paper>

      {/* Related Articles */}
      {related.length > 0 && (
        <Box>
          <Typography
            variant="h6"
            sx={{
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 600,
              mb: 2,
            }}
          >
            Related Articles
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {related.map((relatedId) => {
              const relatedArticle = supportArticles[relatedId];
              if (!relatedArticle) return null;
              return (
                <Paper
                  key={relatedId}
                  onClick={() => navigate(`/support/articles/${relatedId}`)}
                  sx={{
                    p: 2.5,
                    flex: '1 1 300px',
                    maxWidth: { xs: '100%', sm: 'calc(50% - 8px)' },
                    cursor: 'pointer',
                    background: isDark
                      ? 'linear-gradient(180deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.6) 100%)'
                      : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.8) 100%)',
                    border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
                    borderRadius: 2,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      borderColor: `${brandColors.primary.signalTeal}40`,
                      boxShadow: isDark
                        ? `0 8px 24px ${brandColors.primary.deepSafeBlue}20`
                        : '0 4px 16px rgba(0, 0, 0, 0.08)',
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box
                      sx={{
                        p: 1,
                        borderRadius: 1.5,
                        background: `${brandColors.primary.signalTeal}20`,
                        color: brandColors.primary.signalTeal,
                        display: 'flex',
                        '& svg': { fontSize: 20 },
                      }}
                    >
                      {relatedArticle.icon}
                    </Box>
                    <Box>
                      <Typography variant="subtitle2" fontWeight={600}>
                        {relatedArticle.title}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                        <ReadIcon sx={{ fontSize: 12, color: 'text.secondary' }} />
                        <Typography variant="caption" color="text.secondary">
                          {relatedArticle.readTime}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Paper>
              );
            })}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default ArticlePage;
