import React from 'react';
import { Box, Typography, useTheme, Grid } from '@mui/material';
import { motion } from 'framer-motion';
import { Section } from './Section';
import { FeatureCard } from './FeatureCard';
import { useScrollAnimation } from '../hooks/useScrollAnimation';
import { detectionPillars, riskThresholds } from '../data/features';
import { brandColors } from '../../../theme/colors';

const MotionBox = motion.create(Box);

export const SolutionSection: React.FC = () => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const { ref: meterRef, isVisible: meterVisible } = useScrollAnimation({ threshold: 0.3 });

  return (
    <Section
      id="solution"
      title="How DeepSafe Works"
      subtitle="Multi-layered AI analysis combining video, audio, behavioral, and network signals"
      background="default"
    >
      {/* Detection Pillars Grid */}
      <Grid container spacing={3} sx={{ mb: 8 }}>
        {detectionPillars.map((pillar, index) => (
          <Grid key={pillar.id} size={{ xs: 12, sm: 6, md: 3 }}>
            <FeatureCard pillar={pillar} delay={index * 0.1} />
          </Grid>
        ))}
      </Grid>

      {/* Risk Scoring Visualization */}
      <Box
        ref={meterRef}
        sx={{
          p: { xs: 3, md: 4 },
          borderRadius: 3,
          background: isDark
            ? 'linear-gradient(135deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.8) 100%)'
            : 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.9) 100%)',
          border: `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
          maxWidth: 800,
          mx: 'auto',
        }}
      >
        <Typography
          variant="h6"
          sx={{
            fontFamily: '"Space Grotesk", sans-serif',
            fontWeight: 600,
            fontSize: '1.125rem',
            color: isDark ? '#E6ECF5' : '#0B1B3A',
            mb: 3,
            textAlign: 'center',
          }}
        >
          Risk Scoring System
        </Typography>

        {/* Risk meter bar */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ position: 'relative', height: 40 }}>
            {/* Background gradient bar */}
            <Box
              sx={{
                position: 'absolute',
                inset: 0,
                borderRadius: 2,
                background: `linear-gradient(90deg,
                  ${brandColors.statusDark.success} 0%,
                  ${brandColors.statusDark.success} 40%,
                  ${brandColors.primary.alertAmber} 40%,
                  ${brandColors.primary.alertAmber} 65%,
                  #FF8C00 65%,
                  #FF8C00 85%,
                  ${brandColors.primary.threatRed} 85%,
                  ${brandColors.primary.threatRed} 100%)`,
                opacity: 0.3,
              }}
            />

            {/* Animated progress indicator */}
            <MotionBox
              initial={{ width: 0 }}
              animate={meterVisible ? { width: '72%' } : { width: 0 }}
              transition={{ duration: 2, ease: [0.4, 0, 0.2, 1], delay: 0.3 }}
              sx={{
                position: 'absolute',
                left: 0,
                top: 0,
                bottom: 0,
                borderRadius: 2,
                background: `linear-gradient(90deg,
                  ${brandColors.statusDark.success} 0%,
                  ${brandColors.primary.alertAmber} 55%,
                  #FF8C00 100%)`,
                boxShadow: `0 0 20px ${brandColors.primary.alertAmber}60`,
              }}
            />

            {/* Threshold markers */}
            {riskThresholds.map((threshold) => (
              <Box
                key={threshold.level}
                sx={{
                  position: 'absolute',
                  left: `${threshold.threshold}%`,
                  top: -8,
                  bottom: -8,
                  width: 2,
                  background: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.2)',
                  '&::before': {
                    content: `"${threshold.threshold}%"`,
                    position: 'absolute',
                    top: -20,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    fontSize: '0.65rem',
                    color: isDark ? '#7F8CA8' : '#7B8CA5',
                    whiteSpace: 'nowrap',
                  },
                }}
              />
            ))}
          </Box>

          {/* Percentage labels */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              mt: 1,
            }}
          >
            <Typography variant="caption" sx={{ color: isDark ? '#7F8CA8' : '#7B8CA5' }}>
              0%
            </Typography>
            <Typography variant="caption" sx={{ color: isDark ? '#7F8CA8' : '#7B8CA5' }}>
              100%
            </Typography>
          </Box>
        </Box>

        {/* Threshold Legend */}
        <Grid container spacing={2}>
          {riskThresholds.map((threshold, index) => (
            <Grid key={threshold.level} size={{ xs: 12, sm: 4 }}>
              <MotionBox
                initial={{ opacity: 0, y: 10 }}
                animate={meterVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
                transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
                sx={{
                  p: 2,
                  borderRadius: 2,
                  background: isDark
                    ? 'rgba(11, 18, 32, 0.5)'
                    : 'rgba(238, 242, 247, 0.8)',
                  border: `1px solid ${threshold.color}30`,
                  textAlign: 'center',
                }}
              >
                <Box
                  sx={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 1,
                    mb: 1,
                  }}
                >
                  <Box
                    sx={{
                      width: 10,
                      height: 10,
                      borderRadius: '50%',
                      background: threshold.color,
                    }}
                  />
                  <Typography
                    sx={{
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      color: threshold.color,
                    }}
                  >
                    {threshold.label} ({threshold.threshold}%)
                  </Typography>
                </Box>
                <Typography
                  variant="caption"
                  sx={{
                    color: isDark ? '#7F8CA8' : '#7B8CA5',
                    display: 'block',
                    fontSize: '0.7rem',
                  }}
                >
                  {threshold.description}
                </Typography>
              </MotionBox>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Section>
  );
};

export default SolutionSection;
