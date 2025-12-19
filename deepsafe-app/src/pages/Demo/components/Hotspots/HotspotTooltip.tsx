import React from 'react';
import { Box, Typography } from '@mui/material';
import { motion } from 'framer-motion';
import { useThemeMode } from '../../../../context/ThemeContext';
import { hotspotTooltipVariants } from '../../constants/animations';

const MotionBox = motion(Box);

interface HotspotTooltipProps {
  text: string;
  isVisible: boolean;
  position?: 'left' | 'right';
}

export const HotspotTooltip: React.FC<HotspotTooltipProps> = ({
  text,
  isVisible,
  position = 'right',
}) => {
  const { isDark } = useThemeMode();

  if (!isVisible) return null;

  // Tooltip appears above the hotspot
  // Arrow points down to the hotspot
  return (
    <MotionBox
      variants={hotspotTooltipVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      sx={{
        position: 'absolute',
        bottom: 'calc(100% + 8px)',
        // Position tooltip based on hotspot placement
        ...(position === 'left'
          ? { right: '50%', transform: 'translateX(50%)' }
          : { left: '50%', transform: 'translateX(-50%)' }),
        px: 1.5,
        py: 0.75,
        borderRadius: '8px',
        backgroundColor: isDark
          ? 'rgba(26, 32, 44, 0.95)'
          : 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(8px)',
        border: `1px solid ${
          isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)'
        }`,
        boxShadow: isDark
          ? '0 4px 12px rgba(0, 0, 0, 0.4)'
          : '0 4px 12px rgba(0, 0, 0, 0.15)',
        whiteSpace: 'nowrap',
        zIndex: 1000,
        pointerEvents: 'none',
        // Arrow pointing down
        '&::after': {
          content: '""',
          position: 'absolute',
          top: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          border: '6px solid transparent',
          borderTopColor: isDark
            ? 'rgba(26, 32, 44, 0.95)'
            : 'rgba(255, 255, 255, 0.95)',
        },
      }}
    >
      <Typography
        variant="caption"
        sx={{
          color: isDark ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.8)',
          fontWeight: 500,
          fontSize: '0.75rem',
        }}
      >
        {text}
      </Typography>
    </MotionBox>
  );
};

export default HotspotTooltip;
