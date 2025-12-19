import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import { Warning as WarningIcon, Shield as ShieldIcon } from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { useDemoContext } from '../../context/DemoContext';
import { useRiskAnimation } from '../../hooks';

const MotionBox = motion(Box);

export const RiskMeter: React.FC = () => {
  const { isDark } = useThemeMode();
  const { state, riskLevel } = useDemoContext();
  const animatedScore = useRiskAnimation(state.currentRiskScore);

  // Get risk color based on current level
  const getRiskMeterColor = (): string => {
    switch (riskLevel) {
      case 'critical':
        return brandColors.statusDark.error;
      case 'high':
        return '#FF6B6B';
      case 'medium':
        return brandColors.statusDark.warning;
      default:
        return brandColors.statusDark.success;
    }
  };

  // Get label for risk level
  const getRiskLabel = (): string => {
    switch (riskLevel) {
      case 'critical':
        return 'CRITICAL';
      case 'high':
        return 'HIGH';
      case 'medium':
        return 'MEDIUM';
      default:
        return 'LOW';
    }
  };

  const riskColor = getRiskMeterColor();
  const showGlow = riskLevel === 'critical' || riskLevel === 'high';

  return (
    <Box
      id="risk-meter"
      sx={{
        position: 'absolute',
        top: 72,
        right: 16,
        zIndex: 20,
      }}
    >
      <MotionBox
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        sx={{
          backgroundColor: isDark ? 'rgba(0, 0, 0, 0.75)' : 'rgba(0, 0, 0, 0.8)',
          backdropFilter: 'blur(12px)',
          borderRadius: '16px',
          p: 2,
          minWidth: 160,
          border: `1px solid ${
            showGlow ? `${riskColor}50` : 'rgba(255, 255, 255, 0.1)'
          }`,
          boxShadow: showGlow
            ? `0 0 20px ${riskColor}30, 0 4px 20px rgba(0, 0, 0, 0.3)`
            : '0 4px 20px rgba(0, 0, 0, 0.3)',
          transition: 'box-shadow 0.5s ease, border-color 0.5s ease',
        }}
      >
        {/* Header */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            mb: 1.5,
          }}
        >
          <ShieldIcon
            sx={{
              fontSize: 18,
              color: brandColors.primary.signalTeal,
            }}
          />
          <Typography
            variant="caption"
            sx={{
              color: 'rgba(255, 255, 255, 0.7)',
              fontWeight: 500,
              fontSize: '0.7rem',
              letterSpacing: '0.5px',
            }}
          >
            THREAT LEVEL
          </Typography>
        </Box>

        {/* Score Display */}
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5, mb: 1.5 }}>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 700,
              fontFamily: '"Space Grotesk", sans-serif',
              color: riskColor,
              lineHeight: 1,
              transition: 'color 0.5s ease',
            }}
          >
            {Math.round(animatedScore)}
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: riskColor,
              fontWeight: 600,
              transition: 'color 0.5s ease',
            }}
          >
            %
          </Typography>
        </Box>

        {/* Risk Level Chip */}
        <Chip
          icon={
            riskLevel !== 'low' ? (
              <WarningIcon sx={{ fontSize: 14 }} />
            ) : undefined
          }
          label={getRiskLabel()}
          size="small"
          sx={{
            backgroundColor: `${riskColor}20`,
            color: riskColor,
            fontWeight: 700,
            fontSize: '0.65rem',
            height: 24,
            letterSpacing: '0.5px',
            '& .MuiChip-icon': {
              color: riskColor,
            },
            border: `1px solid ${riskColor}40`,
            transition: 'all 0.5s ease',
          }}
        />

        {/* Progress Bar */}
        <Box
          sx={{
            mt: 1.5,
            height: 4,
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: 2,
            overflow: 'hidden',
          }}
        >
          <MotionBox
            initial={{ width: 0 }}
            animate={{ width: `${animatedScore}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            sx={{
              height: '100%',
              backgroundColor: riskColor,
              borderRadius: 2,
              transition: 'background-color 0.5s ease',
            }}
          />
        </Box>

        {/* Indicator Dots */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            mt: 0.75,
            px: 0.25,
          }}
        >
          {[0, 30, 60, 85, 100].map((threshold) => (
            <Box
              key={threshold}
              sx={{
                width: 4,
                height: 4,
                borderRadius: '50%',
                backgroundColor:
                  animatedScore >= threshold
                    ? riskColor
                    : 'rgba(255, 255, 255, 0.2)',
                transition: 'background-color 0.3s ease',
              }}
            />
          ))}
        </Box>
      </MotionBox>
    </Box>
  );
};

export default RiskMeter;
