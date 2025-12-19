import React from 'react';
import { Box, Typography, Stack, LinearProgress, Divider } from '@mui/material';
import {
  Videocam as VideocamIcon,
  RecordVoiceOver as AudioIcon,
  Psychology as BehavioralIcon,
  Wifi as NetworkIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { useDemoContext } from '../../context/DemoContext';
import { riskScoreBreakdown } from '../../data/forensicData';

interface RiskComponent {
  id: string;
  label: string;
  icon: React.ReactNode;
  weight: number;
  score: number;
  color: string;
}

export const RiskBreakdownModal: React.FC = () => {
  const { isDark } = useThemeMode();
  const { state } = useDemoContext();

  // Get current risk score, use breakdown data for detailed view
  const currentScore = state.currentRiskScore;

  const riskComponents: RiskComponent[] = [
    {
      id: 'video',
      label: 'Video Analysis',
      icon: <VideocamIcon sx={{ fontSize: 20 }} />,
      weight: riskScoreBreakdown.weights.video * 100,
      score: riskScoreBreakdown.scores.video,
      color: brandColors.statusDark.error,
    },
    {
      id: 'audio',
      label: 'Audio Analysis',
      icon: <AudioIcon sx={{ fontSize: 20 }} />,
      weight: riskScoreBreakdown.weights.audio * 100,
      score: riskScoreBreakdown.scores.audio,
      color: brandColors.statusDark.warning,
    },
    {
      id: 'behavioral',
      label: 'Behavioral Analysis',
      icon: <BehavioralIcon sx={{ fontSize: 20 }} />,
      weight: riskScoreBreakdown.weights.behavioral * 100,
      score: riskScoreBreakdown.scores.behavioral,
      color: brandColors.statusDark.error,
    },
    {
      id: 'network',
      label: 'Network Analysis',
      icon: <NetworkIcon sx={{ fontSize: 20 }} />,
      weight: riskScoreBreakdown.weights.network * 100,
      score: riskScoreBreakdown.scores.network,
      color: brandColors.statusDark.warning,
    },
  ];

  // Calculate scaled scores based on current overall risk
  const scaleFactor = currentScore / riskScoreBreakdown.calculated.total;
  const scaledComponents = riskComponents.map((comp) => ({
    ...comp,
    displayScore: Math.min(100, Math.round(comp.score * scaleFactor)),
  }));

  return (
    <Box>
      {/* Overall Score */}
      <Box
        sx={{
          p: 2.5,
          borderRadius: '16px',
          backgroundColor: isDark
            ? 'rgba(214, 69, 69, 0.1)'
            : 'rgba(214, 69, 69, 0.05)',
          border: `1px solid ${brandColors.statusDark.error}30`,
          mb: 3,
          textAlign: 'center',
        }}
      >
        <Typography
          variant="caption"
          sx={{
            color: isDark ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)',
            fontWeight: 500,
            display: 'block',
            mb: 1,
          }}
        >
          CURRENT THREAT LEVEL
        </Typography>
        <Typography
          variant="h2"
          sx={{
            fontWeight: 700,
            fontFamily: '"Space Grotesk", sans-serif',
            color: brandColors.statusDark.error,
          }}
        >
          {currentScore}%
        </Typography>
      </Box>

      <Divider
        sx={{
          my: 2,
          borderColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
        }}
      />

      {/* Component Breakdown */}
      <Typography
        variant="subtitle2"
        sx={{
          color: isDark ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)',
          fontWeight: 600,
          mb: 2,
          fontSize: '0.75rem',
          letterSpacing: '0.5px',
        }}
      >
        RISK COMPONENTS
      </Typography>

      <Stack spacing={2.5}>
        {scaledComponents.map((component) => (
          <Box key={component.id}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                mb: 1,
              }}
            >
              <Box
                sx={{
                  width: 36,
                  height: 36,
                  borderRadius: '10px',
                  backgroundColor: `${component.color}15`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: component.color,
                }}
              >
                {component.icon}
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 500,
                    color: isDark ? '#fff' : '#333',
                  }}
                >
                  {component.label}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    color: isDark
                      ? 'rgba(255, 255, 255, 0.4)'
                      : 'rgba(0, 0, 0, 0.4)',
                  }}
                >
                  Weight: {component.weight}%
                </Typography>
              </Box>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  color: component.color,
                  fontFamily: '"JetBrains Mono", monospace',
                }}
              >
                {component.displayScore}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={component.displayScore}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: isDark
                  ? 'rgba(255, 255, 255, 0.1)'
                  : 'rgba(0, 0, 0, 0.08)',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 3,
                  backgroundColor: component.color,
                },
              }}
            />
          </Box>
        ))}
      </Stack>

      <Divider
        sx={{
          my: 3,
          borderColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
        }}
      />

      {/* Explanation */}
      <Typography
        variant="caption"
        sx={{
          color: isDark ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)',
          display: 'block',
          lineHeight: 1.6,
        }}
      >
        Risk scores are calculated by combining weighted analysis from multiple
        detection systems. Video analysis (40%) detects deepfake artifacts, audio
        (30%) identifies voice cloning, behavioral (20%) spots social engineering
        patterns, and network (10%) flags suspicious connection sources.
      </Typography>
    </Box>
  );
};

export default RiskBreakdownModal;
