import React from 'react';
import { Box, LinearProgress, Typography } from '@mui/material';
import { useThemeMode } from '../../context/ThemeContext';
import { brandColors, getRiskCategory } from '../../theme/colors';
import type { RiskCategory } from '../../types';

interface RiskIndicatorProps {
  score: number;
  category?: RiskCategory;
  showLabel?: boolean;
  showPercentage?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const getColorForScore = (score: number, isDark: boolean): string => {
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  if (score >= 86) return brandColors.primary.threatRed;
  if (score >= 61) return statusColors.error;
  if (score >= 31) return statusColors.warning;
  return statusColors.success;
};

const getGradientForScore = (score: number): string => {
  if (score >= 86) return 'linear-gradient(90deg, #D64545 0%, #FF6B6B 100%)';
  if (score >= 61) return 'linear-gradient(90deg, #FF6B6B 0%, #F5A623 100%)';
  if (score >= 31) return 'linear-gradient(90deg, #F5A623 0%, #FFC857 100%)';
  return 'linear-gradient(90deg, #2DBE8B 0%, #3AD6A3 100%)';
};

const getCategoryLabel = (category: RiskCategory): string => {
  switch (category) {
    case 'critical':
      return 'Critical';
    case 'high':
      return 'High';
    case 'medium':
      return 'Medium';
    case 'low':
    default:
      return 'Low';
  }
};

const getSizeConfig = (size: 'small' | 'medium' | 'large') => {
  switch (size) {
    case 'small':
      return { height: 6, minWidth: 100 };
    case 'large':
      return { height: 12, minWidth: 200 };
    case 'medium':
    default:
      return { height: 8, minWidth: 150 };
  }
};

export const RiskIndicator: React.FC<RiskIndicatorProps> = ({
  score,
  category,
  showLabel = true,
  showPercentage = true,
  size = 'medium',
}) => {
  const { isDark } = useThemeMode();
  const effectiveCategory = category || getRiskCategory(score);
  const color = getColorForScore(score, isDark);
  const gradient = getGradientForScore(score);
  const sizeConfig = getSizeConfig(size);

  return (
    <Box sx={{ width: '100%', minWidth: sizeConfig.minWidth }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 0.75,
        }}
      >
        {showLabel && (
          <Typography
            variant={size === 'small' ? 'caption' : 'body2'}
            sx={{
              fontWeight: 500,
              color: 'text.secondary',
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
            }}
          >
            Risk Level:
            <Box
              component="span"
              sx={{
                color,
                fontWeight: 600,
              }}
            >
              {getCategoryLabel(effectiveCategory)}
            </Box>
          </Typography>
        )}
        {showPercentage && (
          <Typography
            variant={size === 'small' ? 'caption' : 'body2'}
            sx={{
              fontWeight: 700,
              color,
              fontFamily: '"JetBrains Mono", monospace',
            }}
          >
            {score}%
          </Typography>
        )}
      </Box>
      <Box
        sx={{
          position: 'relative',
          borderRadius: 2,
          overflow: 'hidden',
        }}
      >
        <LinearProgress
          variant="determinate"
          value={score}
          sx={{
            height: sizeConfig.height,
            borderRadius: 2,
            backgroundColor: isDark
              ? 'rgba(255, 255, 255, 0.08)'
              : 'rgba(0, 0, 0, 0.08)',
            '& .MuiLinearProgress-bar': {
              background: gradient,
              borderRadius: 2,
              transition: 'transform 0.4s ease',
            },
          }}
        />
        {/* Glow effect for high scores */}
        {score >= 61 && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: `${score}%`,
              height: '100%',
              borderRadius: 2,
              background: gradient,
              opacity: 0.3,
              filter: 'blur(4px)',
              pointerEvents: 'none',
            }}
          />
        )}
      </Box>
      {size !== 'small' && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            mt: 0.75,
          }}
        >
          <Typography
            variant="caption"
            sx={{
              color: brandColors.statusDark.success,
              opacity: isDark ? 1 : 0.8,
            }}
          >
            Safe
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: brandColors.primary.threatRed,
              opacity: isDark ? 1 : 0.8,
            }}
          >
            Critical
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default RiskIndicator;
