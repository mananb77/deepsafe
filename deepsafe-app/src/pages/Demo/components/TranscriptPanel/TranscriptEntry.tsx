import React from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';
import { motion } from 'framer-motion';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import type { DemoTranscriptEntry } from '../../types/demo.types';
import { RiskChips } from './RiskChips';
import { transcriptEntryVariants } from '../../constants/animations';

const MotionBox = motion(Box);

interface TranscriptEntryProps {
  entry: DemoTranscriptEntry;
  index: number;
  compact?: boolean;
}

export const TranscriptEntry: React.FC<TranscriptEntryProps> = ({
  entry,
  index,
  compact = false,
}) => {
  const { isDark } = useThemeMode();

  // Get speaker color
  const getSpeakerColor = (speakerId: string): string => {
    switch (speakerId) {
      case 'david-mitchell':
        return brandColors.primary.deepSafeBlue;
      case 'sarah-chen':
        return brandColors.primary.signalTeal;
      case 'deepsafe-bot':
        return brandColors.primary.signalTeal;
      default:
        return isDark ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.7)';
    }
  };

  // Get risk color for the border
  const getRiskBorderColor = (score: number): string => {
    if (score >= 86) return brandColors.statusDark.error;
    if (score >= 61) return '#FF6B6B';
    if (score >= 31) return brandColors.statusDark.warning;
    return 'transparent';
  };

  const isSystemMessage = entry.speakerId === 'deepsafe-bot';
  const showRiskBar = entry.riskScore > 20 && !isSystemMessage;
  const borderColor = getRiskBorderColor(entry.riskScore);

  return (
    <MotionBox
      id={entry.isFlagged ? 'flagged-transcript-entry' : undefined}
      variants={transcriptEntryVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      custom={index}
      sx={{
        position: 'relative',
        px: compact ? 1.5 : 2,
        py: compact ? 1 : 1.5,
        borderLeft: entry.isFlagged ? `3px solid ${borderColor}` : '3px solid transparent',
        backgroundColor: entry.isFlagged
          ? isDark
            ? 'rgba(214, 69, 69, 0.08)'
            : 'rgba(214, 69, 69, 0.05)'
          : isSystemMessage
            ? isDark
              ? 'rgba(31, 182, 166, 0.08)'
              : 'rgba(31, 182, 166, 0.05)'
            : 'transparent',
        transition: 'background-color 0.3s ease, border-color 0.3s ease',
        '&:hover': {
          backgroundColor: isDark
            ? 'rgba(255, 255, 255, 0.03)'
            : 'rgba(0, 0, 0, 0.02)',
        },
      }}
    >
      {/* Header: Speaker & Timestamp */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
        <Typography
          variant="body2"
          sx={{
            fontWeight: 600,
            color: getSpeakerColor(entry.speakerId),
            fontSize: compact ? '0.7rem' : '0.8rem',
          }}
        >
          {entry.speaker}
        </Typography>
        <Typography
          variant="caption"
          sx={{
            color: isDark ? 'rgba(255, 255, 255, 0.4)' : 'rgba(0, 0, 0, 0.4)',
            fontFamily: '"JetBrains Mono", monospace',
            fontSize: compact ? '0.55rem' : '0.65rem',
          }}
        >
          {entry.timestamp}
        </Typography>
        {showRiskBar && (
          <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center', gap: 0.75 }}>
            <Typography
              variant="caption"
              sx={{
                color: borderColor,
                fontWeight: 600,
                fontSize: '0.65rem',
              }}
            >
              {entry.riskScore}%
            </Typography>
            <Box sx={{ width: 40, height: 4 }}>
              <LinearProgress
                variant="determinate"
                value={entry.riskScore}
                sx={{
                  height: 4,
                  borderRadius: 2,
                  backgroundColor: isDark
                    ? 'rgba(255, 255, 255, 0.1)'
                    : 'rgba(0, 0, 0, 0.08)',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 2,
                    backgroundColor: borderColor,
                  },
                }}
              />
            </Box>
          </Box>
        )}
      </Box>

      {/* Message Text */}
      <Typography
        variant="body2"
        sx={{
          color: isSystemMessage
            ? brandColors.primary.signalTeal
            : isDark
              ? 'rgba(255, 255, 255, 0.85)'
              : 'rgba(0, 0, 0, 0.8)',
          fontSize: compact ? '0.75rem' : '0.85rem',
          lineHeight: compact ? 1.4 : 1.5,
          fontStyle: isSystemMessage ? 'italic' : 'normal',
        }}
      >
        {entry.text}
      </Typography>

      {/* Risk Indicator Chips */}
      {entry.isFlagged && entry.riskIndicators && (
        <RiskChips indicators={entry.riskIndicators} />
      )}
    </MotionBox>
  );
};

export default TranscriptEntry;
