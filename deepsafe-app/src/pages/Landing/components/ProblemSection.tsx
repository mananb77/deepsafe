import React from 'react';
import { Box, Typography, useTheme, Grid, Paper } from '@mui/material';
import { motion } from 'framer-motion';
import { Warning as WarningIcon, CheckCircle as PreventedIcon, Cancel as FailedIcon } from '@mui/icons-material';
import { Section } from './Section';
import { StatCard } from './StatCard';
import { useScrollAnimation } from '../hooks/useScrollAnimation';
import { statistics, attackCases, keyInsight } from '../data/statistics';
import { brandColors } from '../../../theme/colors';

const MotionBox = motion.create(Box);

export const ProblemSection: React.FC = () => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const { ref: timelineRef, isVisible: timelineVisible } = useScrollAnimation({ threshold: 0.2 });
  const { ref: quoteRef, isVisible: quoteVisible } = useScrollAnimation({ threshold: 0.3 });

  const getOutcomeIcon = (outcome: string) => {
    switch (outcome) {
      case 'prevented':
        return <PreventedIcon sx={{ fontSize: 16, color: brandColors.statusDark.success }} />;
      case 'successful':
        return <FailedIcon sx={{ fontSize: 16, color: brandColors.primary.threatRed }} />;
      default:
        return <WarningIcon sx={{ fontSize: 16, color: brandColors.primary.alertAmber }} />;
    }
  };

  const getOutcomeColor = (outcome: string) => {
    switch (outcome) {
      case 'prevented':
        return brandColors.statusDark.success;
      case 'successful':
        return brandColors.primary.threatRed;
      default:
        return brandColors.primary.alertAmber;
    }
  };

  return (
    <Section
      id="problem"
      title="The Growing Threat"
      subtitle="Deepfake technology has evolved from a novelty to a serious enterprise security threat"
      background="alternate"
    >
      {/* Statistics Grid */}
      <Grid container spacing={3} sx={{ mb: 8 }}>
        {statistics.map((stat, index) => (
          <Grid key={stat.id} size={{ xs: 6, md: 3 }}>
            <StatCard {...stat} delay={index * 0.1} />
          </Grid>
        ))}
      </Grid>

      {/* Attack Cases Timeline */}
      <Box sx={{ mb: 8 }}>
        <Typography
          variant="h5"
          sx={{
            fontFamily: '"Space Grotesk", sans-serif',
            fontWeight: 600,
            fontSize: '1.25rem',
            color: isDark ? '#E6ECF5' : '#0B1B3A',
            mb: 4,
            textAlign: 'center',
          }}
        >
          Notable Attack Cases
        </Typography>

        <Box ref={timelineRef}>
          <Grid container spacing={2}>
            {attackCases.map((attack, index) => (
              <Grid key={attack.id} size={{ xs: 12, sm: 6, md: 3 }}>
                <MotionBox
                  initial={{ opacity: 0, y: 20 }}
                  animate={timelineVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                  transition={{ duration: 0.5, delay: index * 0.1, ease: [0.4, 0, 0.2, 1] }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2.5,
                      borderRadius: 2,
                      background: isDark
                        ? 'rgba(18, 28, 46, 0.6)'
                        : 'rgba(255, 255, 255, 0.8)',
                      border: `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      position: 'relative',
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        left: 0,
                        top: 0,
                        bottom: 0,
                        width: 3,
                        borderRadius: '3px 0 0 3px',
                        background: getOutcomeColor(attack.outcome),
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      {getOutcomeIcon(attack.outcome)}
                      <Typography
                        variant="caption"
                        sx={{
                          color: isDark ? '#7F8CA8' : '#7B8CA5',
                          fontSize: '0.7rem',
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        {attack.date}
                      </Typography>
                    </Box>
                    <Typography
                      sx={{
                        fontFamily: '"Space Grotesk", sans-serif',
                        fontWeight: 600,
                        fontSize: '0.95rem',
                        color: isDark ? '#E6ECF5' : '#0B1B3A',
                        mb: 0.5,
                      }}
                    >
                      {attack.company}
                    </Typography>
                    {attack.amount && (
                      <Typography
                        sx={{
                          fontWeight: 700,
                          fontSize: '1.25rem',
                          color: brandColors.primary.threatRed,
                          mb: 1,
                        }}
                      >
                        {attack.amount}
                      </Typography>
                    )}
                    <Typography
                      variant="body2"
                      sx={{
                        color: isDark ? '#B8C3D9' : '#4A5D73',
                        fontSize: '0.8rem',
                        lineHeight: 1.5,
                        mt: 'auto',
                      }}
                    >
                      {attack.description}
                    </Typography>
                  </Paper>
                </MotionBox>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Box>

      {/* Key Insight Quote */}
      <MotionBox
        ref={quoteRef}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={quoteVisible ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        sx={{
          p: { xs: 3, md: 4 },
          borderRadius: 3,
          background: isDark
            ? `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}20 0%, ${brandColors.primary.signalTeal}10 100%)`
            : `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}10 0%, ${brandColors.primary.signalTeal}05 100%)`,
          border: `1px solid ${brandColors.primary.signalTeal}30`,
          position: 'relative',
          textAlign: 'center',
          maxWidth: 800,
          mx: 'auto',
        }}
      >
        <Typography
          sx={{
            fontSize: '1.5rem',
            lineHeight: 1.8,
            color: brandColors.primary.signalTeal,
            position: 'absolute',
            top: -10,
            left: 20,
          }}
        >
          "
        </Typography>
        <Typography
          variant="body1"
          sx={{
            fontStyle: 'italic',
            color: isDark ? '#E6ECF5' : '#0B1B3A',
            fontSize: { xs: '1rem', md: '1.125rem' },
            lineHeight: 1.8,
          }}
        >
          {keyInsight.quote}
        </Typography>
        <Typography
          sx={{
            fontSize: '1.5rem',
            lineHeight: 1.8,
            color: brandColors.primary.signalTeal,
            position: 'absolute',
            bottom: -30,
            right: 20,
          }}
        >
          "
        </Typography>
      </MotionBox>
    </Section>
  );
};

export default ProblemSection;
