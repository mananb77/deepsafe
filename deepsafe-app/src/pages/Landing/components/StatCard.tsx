import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { motion } from 'framer-motion';
import { useScrollAnimation, useCountUp } from '../hooks/useScrollAnimation';
import { brandColors } from '../../../theme/colors';

interface StatCardProps {
  label: string;
  value: string;
  numericValue: number;
  prefix?: string;
  suffix?: string;
  source: string;
  description: string;
  delay?: number;
}

const MotionBox = motion.create(Box);

export const StatCard: React.FC<StatCardProps> = ({
  label,
  numericValue,
  prefix = '',
  suffix = '',
  source,
  delay = 0,
}) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const { ref, isVisible } = useScrollAnimation({ threshold: 0.3 });
  const { value: animatedValue } = useCountUp(numericValue, 2000, 0, isVisible);

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
          ? 'linear-gradient(135deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.8) 100%)'
          : 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.9) 100%)',
        border: `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
        backdropFilter: 'blur(10px)',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: isDark
            ? `0 12px 40px rgba(0, 0, 0, 0.4), 0 0 0 1px ${brandColors.primary.signalTeal}30`
            : `0 12px 40px rgba(0, 0, 0, 0.1), 0 0 0 1px ${brandColors.primary.signalTeal}30`,
        },
      }}
    >
      <Typography
        variant="overline"
        sx={{
          color: isDark ? '#7F8CA8' : '#7B8CA5',
          fontSize: '0.7rem',
          letterSpacing: '0.1em',
          mb: 1,
        }}
      >
        {label}
      </Typography>
      <Typography
        sx={{
          fontFamily: '"Space Grotesk", sans-serif',
          fontWeight: 700,
          fontSize: { xs: '2rem', md: '2.5rem' },
          lineHeight: 1,
          mb: 1,
          background: `linear-gradient(90deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}
      >
        {prefix}{animatedValue.toLocaleString()}{suffix}
      </Typography>
      <Typography
        variant="caption"
        sx={{
          color: isDark ? '#7F8CA8' : '#7B8CA5',
          fontSize: '0.7rem',
          mt: 'auto',
        }}
      >
        Source: {source}
      </Typography>
    </MotionBox>
  );
};

export default StatCard;
