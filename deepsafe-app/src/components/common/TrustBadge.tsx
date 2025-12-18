import React from 'react';
import { Tooltip, Box, Typography } from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Help as HelpIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../context/ThemeContext';
import { brandColors } from '../../theme/colors';
import type { ParticipantStatus } from '../../types';

type TrustLevel = 'verified' | 'partial' | 'high-risk' | 'external';

interface TrustBadgeProps {
  level?: TrustLevel;
  status?: ParticipantStatus;
  score?: number;
  showScore?: boolean;
  size?: 'small' | 'medium' | 'large';
  tooltip?: string;
}

const getConfigFromStatus = (status: ParticipantStatus) => {
  switch (status) {
    case 'verified':
      return { level: 'verified' as TrustLevel };
    case 'blacklisted':
    case 'flagged':
      return { level: 'high-risk' as TrustLevel };
    case 'external':
    case 'guest':
      return { level: 'external' as TrustLevel };
    default:
      return { level: 'partial' as TrustLevel };
  }
};

const getTrustConfig = (level: TrustLevel, isDark: boolean) => {
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  switch (level) {
    case 'verified':
      return {
        icon: CheckCircleIcon,
        color: statusColors.success,
        bgColor: isDark
          ? 'rgba(58, 214, 163, 0.15)'
          : 'rgba(45, 190, 139, 0.1)',
        label: 'Verified & Trusted',
      };
    case 'partial':
      return {
        icon: WarningIcon,
        color: statusColors.warning,
        bgColor: isDark
          ? 'rgba(255, 200, 87, 0.15)'
          : 'rgba(245, 166, 35, 0.1)',
        label: 'Partially Verified',
      };
    case 'high-risk':
      return {
        icon: ErrorIcon,
        color: statusColors.error,
        bgColor: isDark
          ? 'rgba(255, 107, 107, 0.15)'
          : 'rgba(214, 69, 69, 0.1)',
        label: 'High Risk / Flagged',
      };
    case 'external':
    default:
      return {
        icon: HelpIcon,
        color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
        bgColor: isDark
          ? 'rgba(127, 140, 168, 0.15)'
          : 'rgba(123, 140, 165, 0.1)',
        label: 'External / Guest',
      };
  }
};

const getSizeConfig = (size: 'small' | 'medium' | 'large') => {
  switch (size) {
    case 'small':
      return { iconSize: 18, fontSize: '0.75rem', padding: '4px 8px' };
    case 'large':
      return { iconSize: 28, fontSize: '0.9375rem', padding: '8px 12px' };
    case 'medium':
    default:
      return { iconSize: 22, fontSize: '0.8125rem', padding: '6px 10px' };
  }
};

export const TrustBadge: React.FC<TrustBadgeProps> = ({
  level,
  status,
  score,
  showScore = false,
  size = 'medium',
  tooltip,
}) => {
  const { isDark } = useThemeMode();

  const effectiveLevel =
    level || (status ? getConfigFromStatus(status).level : 'external');
  const config = getTrustConfig(effectiveLevel, isDark);
  const sizeConfig = getSizeConfig(size);
  const Icon = config.icon;

  return (
    <Tooltip title={tooltip || config.label} arrow>
      <Box
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 0.5,
          padding: showScore ? sizeConfig.padding : 0,
          borderRadius: showScore ? 2 : 0,
          background: showScore ? config.bgColor : 'transparent',
          border: showScore
            ? `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`
            : 'none',
          transition: 'all 0.2s ease',
          '&:hover': showScore
            ? {
                transform: 'scale(1.02)',
              }
            : {},
        }}
      >
        <Icon
          sx={{
            fontSize: sizeConfig.iconSize,
            color: config.color,
            filter:
              effectiveLevel === 'verified' || effectiveLevel === 'high-risk'
                ? `drop-shadow(0 0 4px ${config.color}40)`
                : 'none',
          }}
        />
        {showScore && score !== undefined && (
          <Typography
            component="span"
            sx={{
              fontSize: sizeConfig.fontSize,
              fontWeight: 600,
              color: config.color,
              fontFamily: '"JetBrains Mono", monospace',
            }}
          >
            {score}%
          </Typography>
        )}
      </Box>
    </Tooltip>
  );
};

export default TrustBadge;
