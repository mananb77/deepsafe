import React, { useState, useCallback } from 'react';
import { Box, IconButton, useMediaQuery, useTheme } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Info as InfoIcon,
  BarChart as DataIcon,
  TouchApp as ActionIcon,
} from '@mui/icons-material';
import { brandColors } from '../../../../theme/colors';
import { useWalkthroughContext } from '../../context/WalkthroughContext';
import type { WalkthroughHotspot } from '../../types/walkthrough.types';
import { HotspotTooltip } from './HotspotTooltip';
import { hotspotPulseVariants } from '../../constants/animations';

const MotionBox = motion.create(Box);

interface HotspotProps {
  config: WalkthroughHotspot;
  style?: React.CSSProperties;
  tooltipPosition?: 'left' | 'right' | 'top' | 'bottom';
}

export const Hotspot: React.FC<HotspotProps> = ({ config, style, tooltipPosition = 'right' }) => {
  const { dispatch, state } = useWalkthroughContext();
  const [isHovered, setIsHovered] = useState(false);
  const [showTooltipOnTouch, setShowTooltipOnTouch] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const isVisited = state.visitedHotspots.has(config.id);

  // Get hotspot color by type
  const getHotspotColor = () => {
    switch (config.type) {
      case 'info':
        return brandColors.primary.signalTeal;
      case 'data':
        return brandColors.primary.deepSafeBlue;
      case 'action':
        return brandColors.primary.alertAmber;
      default:
        return brandColors.primary.signalTeal;
    }
  };

  // Get icon by type
  const getIcon = () => {
    const iconSize = isMobile ? 18 : 14;
    const iconSx = { fontSize: iconSize, color: '#fff' };
    switch (config.type) {
      case 'info':
        return <InfoIcon sx={iconSx} />;
      case 'data':
        return <DataIcon sx={iconSx} />;
      case 'action':
        return <ActionIcon sx={iconSx} />;
      default:
        return <InfoIcon sx={iconSx} />;
    }
  };

  const handleClick = useCallback(() => {
    dispatch({ type: 'MARK_HOTSPOT_VISITED', id: config.id });

    if (config.modalContent) {
      dispatch({
        type: 'OPEN_MODAL',
        modal: config.modalContent,
      });
    }
    // Hide tooltip after clicking on mobile
    if (isMobile) {
      setShowTooltipOnTouch(false);
    }
  }, [config.id, config.modalContent, dispatch, isMobile]);

  // Handle touch start for mobile - show tooltip briefly
  const handleTouchStart = useCallback(() => {
    if (isMobile && !isVisited) {
      setShowTooltipOnTouch(true);
      // Auto-hide after 2 seconds
      setTimeout(() => setShowTooltipOnTouch(false), 2000);
    }
  }, [isMobile, isVisited]);

  const color = getHotspotColor();

  // Button sizes - larger on mobile for better touch targets
  const buttonSize = isMobile ? 40 : 28;
  const pulseRingSize = isMobile ? 48 : 36;

  return (
    <MotionBox
      variants={hotspotPulseVariants}
      initial="initial"
      animate={isVisited ? 'initial' : 'animate'}
      style={style}
      onMouseEnter={() => !isMobile && setIsHovered(true)}
      onMouseLeave={() => !isMobile && setIsHovered(false)}
      onTouchStart={handleTouchStart}
      sx={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        // Ensure touch target is at least 44px on mobile
        minWidth: { xs: 44, sm: 'auto' },
        minHeight: { xs: 44, sm: 'auto' },
      }}
    >
      {/* Pulse Ring */}
      {!isVisited && (
        <Box
          sx={{
            position: 'absolute',
            width: pulseRingSize,
            height: pulseRingSize,
            borderRadius: '50%',
            border: `2px solid ${color}`,
            opacity: 0.5,
            animation: 'pulseRing 2s ease-out infinite',
            '@keyframes pulseRing': {
              '0%': {
                transform: 'scale(1)',
                opacity: 0.5,
              },
              '100%': {
                transform: 'scale(1.8)',
                opacity: 0,
              },
            },
          }}
        />
      )}

      {/* Hotspot Button */}
      <IconButton
        onClick={handleClick}
        size="small"
        sx={{
          width: buttonSize,
          height: buttonSize,
          backgroundColor: color,
          opacity: isVisited ? 0.6 : 1,
          boxShadow: isVisited ? 'none' : `0 0 12px ${color}80`,
          '&:hover': {
            backgroundColor: color,
            opacity: 1,
            transform: 'scale(1.1)',
          },
          // Better touch feedback
          '&:active': {
            transform: 'scale(0.95)',
          },
          transition: 'all 0.2s ease',
          // Ensure the button itself is easy to tap
          touchAction: 'manipulation',
        }}
      >
        {getIcon()}
      </IconButton>

      {/* Tooltip - show on hover (desktop) or touch (mobile) */}
      <AnimatePresence>
        {(isHovered || showTooltipOnTouch) && (
          <HotspotTooltip
            text={config.tooltip}
            isVisible
            position={tooltipPosition}
          />
        )}
      </AnimatePresence>
    </MotionBox>
  );
};

export default Hotspot;
