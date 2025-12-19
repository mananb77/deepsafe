import React from 'react';
import { Box, Typography } from '@mui/material';
import { motion } from 'framer-motion';
import { brandColors } from '../../../../theme/colors';
import { useThemeMode } from '../../../../context/ThemeContext';
import { hotspotTooltipVariants } from '../../constants/animations';

const MotionBox = motion.create(Box);

interface HotspotTooltipProps {
  text: string;
  isVisible: boolean;
  position?: 'left' | 'right' | 'top' | 'bottom';
}

export const HotspotTooltip: React.FC<HotspotTooltipProps> = ({
  text,
  isVisible,
  position = 'right',
}) => {
  const { isDark } = useThemeMode();

  if (!isVisible) return null;

  // Position styles based on placement
  const getPositionStyles = () => {
    const base = {
      position: 'absolute' as const,
      whiteSpace: 'nowrap' as const,
    };

    switch (position) {
      case 'left':
        return {
          ...base,
          right: '100%',
          top: '50%',
          transform: 'translateY(-50%)',
          marginRight: 12,
        };
      case 'right':
        return {
          ...base,
          left: '100%',
          top: '50%',
          transform: 'translateY(-50%)',
          marginLeft: 12,
        };
      case 'top':
        return {
          ...base,
          bottom: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginBottom: 12,
        };
      case 'bottom':
        return {
          ...base,
          top: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginTop: 12,
        };
      default:
        return {
          ...base,
          left: '100%',
          top: '50%',
          transform: 'translateY(-50%)',
          marginLeft: 12,
        };
    }
  };

  // Arrow styles based on position
  const getArrowStyles = () => {
    const arrowSize = 6;
    const base = {
      position: 'absolute' as const,
      width: 0,
      height: 0,
    };

    switch (position) {
      case 'left':
        return {
          ...base,
          right: -arrowSize,
          top: '50%',
          transform: 'translateY(-50%)',
          borderTop: `${arrowSize}px solid transparent`,
          borderBottom: `${arrowSize}px solid transparent`,
          borderLeft: `${arrowSize}px solid ${isDark ? brandColors.dark.elevated : '#fff'}`,
        };
      case 'right':
        return {
          ...base,
          left: -arrowSize,
          top: '50%',
          transform: 'translateY(-50%)',
          borderTop: `${arrowSize}px solid transparent`,
          borderBottom: `${arrowSize}px solid transparent`,
          borderRight: `${arrowSize}px solid ${isDark ? brandColors.dark.elevated : '#fff'}`,
        };
      case 'top':
        return {
          ...base,
          bottom: -arrowSize,
          left: '50%',
          transform: 'translateX(-50%)',
          borderLeft: `${arrowSize}px solid transparent`,
          borderRight: `${arrowSize}px solid transparent`,
          borderTop: `${arrowSize}px solid ${isDark ? brandColors.dark.elevated : '#fff'}`,
        };
      case 'bottom':
        return {
          ...base,
          top: -arrowSize,
          left: '50%',
          transform: 'translateX(-50%)',
          borderLeft: `${arrowSize}px solid transparent`,
          borderRight: `${arrowSize}px solid transparent`,
          borderBottom: `${arrowSize}px solid ${isDark ? brandColors.dark.elevated : '#fff'}`,
        };
      default:
        return {
          ...base,
          left: -arrowSize,
          top: '50%',
          transform: 'translateY(-50%)',
          borderTop: `${arrowSize}px solid transparent`,
          borderBottom: `${arrowSize}px solid transparent`,
          borderRight: `${arrowSize}px solid ${isDark ? brandColors.dark.elevated : '#fff'}`,
        };
    }
  };

  return (
    <MotionBox
      variants={hotspotTooltipVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      sx={{
        ...getPositionStyles(),
        backgroundColor: isDark ? brandColors.dark.elevated : '#fff',
        borderRadius: 1.5,
        px: 2,
        py: 1,
        boxShadow: isDark
          ? '0 4px 20px rgba(0, 0, 0, 0.5)'
          : '0 4px 20px rgba(0, 0, 0, 0.15)',
        border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'}`,
        zIndex: 1300,
      }}
    >
      {/* Arrow */}
      <Box sx={getArrowStyles()} />

      <Typography
        variant="body2"
        sx={{
          color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
          fontWeight: 500,
          fontSize: '0.85rem',
        }}
      >
        {text}
      </Typography>
    </MotionBox>
  );
};

export default HotspotTooltip;
