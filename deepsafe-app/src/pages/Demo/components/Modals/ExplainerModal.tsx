import React from 'react';
import { Box, Typography, Stack, Divider } from '@mui/material';
import {
  Shield as ShieldIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';

interface ExplainerContent {
  title: string;
  description: string;
  features?: string[];
  icon?: React.ReactNode;
}

// Content map for different explainer topics
const getExplainerContent = (title: string): ExplainerContent => {
  const contentMap: Record<string, ExplainerContent> = {
    'Meeting Protection': {
      title: 'Meeting Protection',
      description:
        'DeepSafe provides real-time protection for your video meetings by continuously monitoring all participants for signs of deepfake manipulation, voice cloning, and social engineering attacks.',
      features: [
        'Real-time video authenticity analysis',
        'Voice fingerprint verification',
        'Behavioral pattern detection',
        'Automated threat response',
      ],
      icon: <ShieldIcon sx={{ fontSize: 32, color: brandColors.primary.signalTeal }} />,
    },
    'Trust Scores Explained': {
      title: 'Participant Trust Scores',
      description:
        'Trust scores represent the confidence level that a participant is who they claim to be, based on multiple verification signals analyzed in real-time.',
      features: [
        'Video authenticity (deepfake detection)',
        'Voice fingerprint matching',
        'Device and network verification',
        'Behavioral consistency analysis',
      ],
      icon: <ShieldIcon sx={{ fontSize: 32, color: brandColors.statusDark.success }} />,
    },
    'DeepSafe Bot': {
      title: 'DeepSafe Meeting Guardian',
      description:
        'The DeepSafe bot joins your meetings as a silent guardian, monitoring all participants and conversations for potential threats without disrupting the meeting flow.',
      features: [
        'Automatic meeting join via calendar integration',
        'Silent background monitoring',
        'Real-time risk alerting',
        'Evidence preservation for investigations',
      ],
      icon: <ShieldIcon sx={{ fontSize: 32, color: brandColors.primary.signalTeal }} />,
    },
    'Automated Actions': {
      title: 'Automated Threat Response',
      description:
        'When DeepSafe detects a confirmed threat, it can automatically take protective actions to prevent harm while preserving evidence for investigation.',
      features: [
        'Identity verification triggers',
        'Meeting host alerts',
        'Participant removal capabilities',
        'Forensic evidence preservation',
      ],
      icon: <ShieldIcon sx={{ fontSize: 32, color: brandColors.statusDark.warning }} />,
    },
    'Multi-Factor Verification': {
      title: 'Identity Verification Process',
      description:
        'When suspicious activity is detected, DeepSafe initiates a multi-factor verification process to confirm the true identity of participants through out-of-band channels.',
      features: [
        'SMS verification to registered number',
        'Voice fingerprint comparison',
        'Device authentication check',
        'Calendar invite verification',
      ],
      icon: <ShieldIcon sx={{ fontSize: 32, color: brandColors.primary.signalTeal }} />,
    },
    default: {
      title: 'DeepSafe Feature',
      description:
        'This feature helps protect your organization from deepfake attacks and social engineering threats during video meetings.',
      features: ['Real-time monitoring', 'AI-powered detection', 'Automated response'],
      icon: <InfoIcon sx={{ fontSize: 32, color: brandColors.primary.signalTeal }} />,
    },
  };

  return contentMap[title] || contentMap.default;
};

interface ExplainerModalProps {
  title: string;
}

export const ExplainerModal: React.FC<ExplainerModalProps> = ({ title }) => {
  const { isDark } = useThemeMode();
  const content = getExplainerContent(title);

  return (
    <Box>
      {/* Icon */}
      <Box
        sx={{
          width: 64,
          height: 64,
          borderRadius: '16px',
          backgroundColor: 'rgba(31, 182, 166, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 2,
        }}
      >
        {content.icon}
      </Box>

      {/* Description */}
      <Typography
        variant="body1"
        sx={{
          color: isDark ? 'rgba(255, 255, 255, 0.85)' : 'rgba(0, 0, 0, 0.8)',
          lineHeight: 1.7,
          mb: 3,
        }}
      >
        {content.description}
      </Typography>

      <Divider
        sx={{
          my: 2,
          borderColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
        }}
      />

      {/* Features */}
      {content.features && (
        <>
          <Typography
            variant="subtitle2"
            sx={{
              color: isDark ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)',
              fontWeight: 600,
              mb: 1.5,
              fontSize: '0.75rem',
              letterSpacing: '0.5px',
            }}
          >
            KEY CAPABILITIES
          </Typography>
          <Stack spacing={1.5}>
            {content.features.map((feature, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                }}
              >
                <CheckCircleIcon
                  sx={{
                    fontSize: 18,
                    color: brandColors.statusDark.success,
                  }}
                />
                <Typography
                  variant="body2"
                  sx={{
                    color: isDark
                      ? 'rgba(255, 255, 255, 0.8)'
                      : 'rgba(0, 0, 0, 0.7)',
                  }}
                >
                  {feature}
                </Typography>
              </Box>
            ))}
          </Stack>
        </>
      )}
    </Box>
  );
};

export default ExplainerModal;
