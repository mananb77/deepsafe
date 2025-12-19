import React, { useState } from 'react';
import { Box, IconButton } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Info as InfoIcon,
  BarChart as DataIcon,
  TouchApp as ActionIcon,
} from '@mui/icons-material';
import { brandColors } from '../../../../theme/colors';
import { useDemoContext } from '../../context/DemoContext';
import type { HotspotConfig } from '../../types/demo.types';
import { HotspotTooltip } from './HotspotTooltip';
import { hotspotPulseVariants } from '../../constants/animations';

const MotionBox = motion(Box);

interface HotspotProps {
  config: HotspotConfig;
  style?: React.CSSProperties;
  tooltipPosition?: 'left' | 'right';
}

export const Hotspot: React.FC<HotspotProps> = ({ config, style, tooltipPosition = 'right' }) => {
  const { dispatch, state } = useDemoContext();
  const [isHovered, setIsHovered] = useState(false);

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
    const iconSx = { fontSize: 14, color: '#fff' };
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

  const handleClick = () => {
    dispatch({ type: 'MARK_HOTSPOT_VISITED', hotspotId: config.id });
    dispatch({
      type: 'OPEN_MODAL',
      modal: config.modalConfig,
    });
  };

  const color = getHotspotColor();

  return (
    <MotionBox
      variants={hotspotPulseVariants}
      initial="initial"
      animate={isVisited ? 'initial' : 'animate'}
      style={style}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      sx={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Pulse Ring */}
      {!isVisited && (
        <Box
          sx={{
            position: 'absolute',
            width: 36,
            height: 36,
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
          width: 28,
          height: 28,
          backgroundColor: color,
          opacity: isVisited ? 0.6 : 1,
          boxShadow: isVisited ? 'none' : `0 0 12px ${color}80`,
          '&:hover': {
            backgroundColor: color,
            opacity: 1,
            transform: 'scale(1.1)',
          },
          transition: 'all 0.2s ease',
        }}
      >
        {getIcon()}
      </IconButton>

      {/* Tooltip */}
      <AnimatePresence>
        {isHovered && <HotspotTooltip text={config.tooltip} isVisible position={tooltipPosition} />}
      </AnimatePresence>
    </MotionBox>
  );
};

export default Hotspot;
