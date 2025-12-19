import React from 'react';
import { Box, Typography, useTheme, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import {
  Videocam as VideoIcon,
  GraphicEq as AudioIcon,
  Psychology as BehaviorIcon,
  Lan as NetworkIcon,
} from '@mui/icons-material';
import { useScrollAnimation } from '../hooks/useScrollAnimation';
import { brandColors } from '../../../theme/colors';
import type { DetectionPillar } from '../data/features';

interface FeatureCardProps {
  pillar: DetectionPillar;
  delay?: number;
}

const iconMap = {
  video: VideoIcon,
  audio: AudioIcon,
  behavior: BehaviorIcon,
  network: NetworkIcon,
};

const MotionBox = motion.create(Box);

export const FeatureCard: React.FC<FeatureCardProps> = ({ pillar, delay = 0 }) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const { ref, isVisible } = useScrollAnimation({ threshold: 0.2 });

  const Icon = iconMap[pillar.icon];

  return (
    <MotionBox
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{ duration: 0.6, delay, ease: [0.4, 0, 0.2, 1] }}
      sx={{
        p: 3,
        borderRadius: 3,
        background: isDark
          ? 'linear-gradient(135deg, rgba(18, 28, 46, 0.6) 0%, rgba(26, 39, 64, 0.6) 100%)'
          : 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.9) 100%)',
        border: `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
        backdropFilter: 'blur(10px)',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.3s ease',
        position: 'relative',
        overflow: 'hidden',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: isDark
            ? `0 12px 40px rgba(0, 0, 0, 0.4)`
            : `0 12px 40px rgba(0, 0, 0, 0.1)`,
          '& .feature-icon': {
            transform: 'scale(1.1)',
          },
        },
      }}
    >
      {/* Weight badge */}
      <Chip
        label={`${pillar.weight}%`}
        size="small"
        sx={{
          position: 'absolute',
          top: 16,
          right: 16,
          background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}30 0%, ${brandColors.primary.signalTeal}30 100%)`,
          color: brandColors.primary.signalTeal,
          fontWeight: 600,
          fontSize: '0.75rem',
          border: `1px solid ${brandColors.primary.signalTeal}40`,
        }}
      />

      {/* Icon */}
      <Box
        className="feature-icon"
        sx={{
          width: 56,
          height: 56,
          borderRadius: 2,
          background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}20 0%, ${brandColors.primary.signalTeal}20 100%)`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 2,
          transition: 'transform 0.3s ease',
        }}
      >
        <Icon sx={{ fontSize: 28, color: brandColors.primary.signalTeal }} />
      </Box>

      {/* Title */}
      <Typography
        variant="h6"
        sx={{
          fontFamily: '"Space Grotesk", sans-serif',
          fontWeight: 600,
          fontSize: '1.125rem',
          color: isDark ? '#E6ECF5' : '#0B1B3A',
          mb: 1,
        }}
      >
        {pillar.title}
      </Typography>

      {/* Description */}
      <Typography
        variant="body2"
        sx={{
          color: isDark ? '#B8C3D9' : '#4A5D73',
          mb: 2,
          lineHeight: 1.6,
        }}
      >
        {pillar.description}
      </Typography>

      {/* Capabilities */}
      <Box sx={{ mt: 'auto' }}>
        {pillar.capabilities.map((capability, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              py: 0.5,
            }}
          >
            <Box
              sx={{
                width: 4,
                height: 4,
                borderRadius: '50%',
                background: brandColors.primary.signalTeal,
              }}
            />
            <Typography
              variant="caption"
              sx={{
                color: isDark ? '#7F8CA8' : '#7B8CA5',
                fontSize: '0.75rem',
              }}
            >
              {capability}
            </Typography>
          </Box>
        ))}
      </Box>
    </MotionBox>
  );
};

export default FeatureCard;
