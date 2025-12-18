import React from 'react';
import { Chip } from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';
import { useThemeMode } from '../../context/ThemeContext';
import { brandColors } from '../../theme/colors';
import { functionalGradients } from '../../theme/gradients';
import type { RiskCategory } from '../../types';

interface RiskBadgeProps {
  category: RiskCategory;
  size?: 'small' | 'medium';
  showIcon?: boolean;
}

const getRiskConfig = (category: RiskCategory, isDark: boolean) => {
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  switch (category) {
    case 'critical':
      return {
        label: 'CRITICAL',
        background: isDark
          ? functionalGradients.critical
          : 'linear-gradient(135deg, rgba(214, 69, 69, 0.15) 0%, rgba(214, 69, 69, 0.25) 100%)',
        color: isDark ? '#FFFFFF' : brandColors.primary.threatRed,
        borderColor: isDark ? 'transparent' : `rgba(214, 69, 69, 0.3)`,
      };
    case 'high':
      return {
        label: 'HIGH',
        background: isDark
          ? 'linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(214, 69, 69, 0.3) 100%)'
          : 'linear-gradient(135deg, rgba(214, 69, 69, 0.1) 0%, rgba(214, 69, 69, 0.15) 100%)',
        color: statusColors.error,
        borderColor: isDark ? 'rgba(255, 107, 107, 0.3)' : 'rgba(214, 69, 69, 0.2)',
      };
    case 'medium':
      return {
        label: 'MEDIUM',
        background: isDark
          ? 'linear-gradient(135deg, rgba(255, 200, 87, 0.15) 0%, rgba(245, 166, 35, 0.25) 100%)'
          : 'linear-gradient(135deg, rgba(245, 166, 35, 0.1) 0%, rgba(245, 166, 35, 0.15) 100%)',
        color: statusColors.warning,
        borderColor: isDark ? 'rgba(255, 200, 87, 0.3)' : 'rgba(245, 166, 35, 0.2)',
      };
    case 'low':
    default:
      return {
        label: 'LOW',
        background: isDark
          ? 'linear-gradient(135deg, rgba(58, 214, 163, 0.15) 0%, rgba(45, 190, 139, 0.25) 100%)'
          : 'linear-gradient(135deg, rgba(45, 190, 139, 0.1) 0%, rgba(45, 190, 139, 0.15) 100%)',
        color: statusColors.success,
        borderColor: isDark ? 'rgba(58, 214, 163, 0.3)' : 'rgba(45, 190, 139, 0.2)',
      };
  }
};

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  category,
  size = 'medium',
  showIcon = false,
}) => {
  const { isDark } = useThemeMode();
  const config = getRiskConfig(category, isDark);

  return (
    <Chip
      label={config.label}
      size={size}
      icon={
        showIcon && (category === 'high' || category === 'critical') ? (
          <WarningIcon sx={{ fontSize: size === 'small' ? 14 : 16 }} />
        ) : undefined
      }
      sx={{
        background: config.background,
        color: config.color,
        fontWeight: 600,
        fontSize: size === 'small' ? '0.6875rem' : '0.75rem',
        letterSpacing: '0.05em',
        height: size === 'small' ? 24 : 28,
        border: `1px solid ${config.borderColor}`,
        '& .MuiChip-icon': {
          color: config.color,
        },
        transition: 'all 0.2s ease',
        '&:hover': {
          transform: 'scale(1.02)',
        },
      }}
    />
  );
};

export default RiskBadge;
