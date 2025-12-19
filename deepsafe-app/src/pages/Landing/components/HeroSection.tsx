import React from 'react';
import { Box, Typography, Button, Container, useTheme, Grid } from '@mui/material';
import { motion } from 'framer-motion';
import { PlayArrow as PlayIcon, Dashboard as DashboardIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { brandColors } from '../../../theme/colors';

const MotionBox = motion.create(Box);
const MotionTypography = motion.create(Typography);

export const HeroSection: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const isDark = theme.palette.mode === 'dark';

  return (
    <Box
      component="section"
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        position: 'relative',
        overflow: 'hidden',
        pt: { xs: 10, md: 0 },
        background: isDark
          ? 'linear-gradient(180deg, #05070C 0%, #0B1220 50%, #121C2E 100%)'
          : 'linear-gradient(180deg, #F7F9FC 0%, #EEF2F7 50%, #E6ECF5 100%)',
      }}
    >
      {/* Animated grid background */}
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          backgroundImage: isDark
            ? `linear-gradient(rgba(31, 60, 136, 0.03) 1px, transparent 1px),
               linear-gradient(90deg, rgba(31, 60, 136, 0.03) 1px, transparent 1px)`
            : `linear-gradient(rgba(31, 60, 136, 0.05) 1px, transparent 1px),
               linear-gradient(90deg, rgba(31, 60, 136, 0.05) 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
          opacity: 0.5,
        }}
      />

      {/* Radial glow */}
      <Box
        sx={{
          position: 'absolute',
          top: '20%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '80%',
          height: '60%',
          background: isDark
            ? `radial-gradient(ellipse at center, ${brandColors.primary.deepSafeBlue}15 0%, transparent 70%)`
            : `radial-gradient(ellipse at center, ${brandColors.primary.deepSafeBlue}10 0%, transparent 70%)`,
          pointerEvents: 'none',
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        <Grid container spacing={4} alignItems="center">
          <Grid size={{ xs: 12, md: 7 }}>
            <MotionBox
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
            >
              {/* Badge */}
              <Box
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 1,
                  px: 2,
                  py: 0.75,
                  borderRadius: 6,
                  background: isDark
                    ? 'rgba(31, 182, 166, 0.1)'
                    : 'rgba(31, 182, 166, 0.15)',
                  border: `1px solid ${brandColors.primary.signalTeal}40`,
                  mb: 3,
                }}
              >
                <Box
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: brandColors.primary.signalTeal,
                    animation: 'pulse 2s infinite',
                    '@keyframes pulse': {
                      '0%, 100%': { opacity: 1 },
                      '50%': { opacity: 0.5 },
                    },
                  }}
                />
                <Typography
                  variant="caption"
                  sx={{
                    color: brandColors.primary.signalTeal,
                    fontWeight: 600,
                    fontSize: '0.75rem',
                    letterSpacing: '0.05em',
                  }}
                >
                  ENTERPRISE SECURITY
                </Typography>
              </Box>

              {/* Main Headline */}
              <MotionTypography
                variant="h1"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.1, ease: [0.4, 0, 0.2, 1] }}
                sx={{
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 700,
                  fontSize: { xs: '2.5rem', sm: '3rem', md: '3.5rem', lg: '4rem' },
                  lineHeight: 1.1,
                  mb: 3,
                  color: isDark ? '#E6ECF5' : '#0B1B3A',
                }}
              >
                AI-Powered Protection Against{' '}
                <Box
                  component="span"
                  sx={{
                    background: `linear-gradient(90deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  Deepfake Attacks
                </Box>
              </MotionTypography>

              {/* Subheadline */}
              <MotionTypography
                variant="h5"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2, ease: [0.4, 0, 0.2, 1] }}
                sx={{
                  color: isDark ? '#B8C3D9' : '#4A5D73',
                  fontWeight: 400,
                  fontSize: { xs: '1rem', md: '1.25rem' },
                  lineHeight: 1.6,
                  mb: 4,
                  maxWidth: 560,
                }}
              >
                Real-time detection and prevention for enterprise video communications.
                Protect your organization from sophisticated AI-generated impersonation.
              </MotionTypography>

              {/* CTAs */}
              <MotionBox
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.3, ease: [0.4, 0, 0.2, 1] }}
                sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}
              >
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<PlayIcon />}
                  onClick={() => navigate('/demo')}
                  sx={{
                    background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                    color: '#fff',
                    fontWeight: 600,
                    fontSize: '1rem',
                    textTransform: 'none',
                    borderRadius: 2,
                    px: 4,
                    py: 1.5,
                    boxShadow: `0 4px 20px ${brandColors.primary.deepSafeBlue}40`,
                    '&:hover': {
                      background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
                      transform: 'translateY(-2px)',
                      boxShadow: `0 8px 30px ${brandColors.primary.deepSafeBlue}50`,
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  Try Interactive Demo
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<DashboardIcon />}
                  onClick={() => navigate('/app/welcome')}
                  sx={{
                    borderColor: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
                    color: isDark ? '#E6ECF5' : '#0B1B3A',
                    fontWeight: 600,
                    fontSize: '1rem',
                    textTransform: 'none',
                    borderRadius: 2,
                    px: 4,
                    py: 1.5,
                    '&:hover': {
                      borderColor: brandColors.primary.signalTeal,
                      background: `${brandColors.primary.signalTeal}10`,
                    },
                  }}
                >
                  View Dashboard
                </Button>
              </MotionBox>

              {/* Stats row */}
              <MotionBox
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.5, ease: [0.4, 0, 0.2, 1] }}
                sx={{
                  display: 'flex',
                  gap: { xs: 3, md: 5 },
                  mt: 6,
                  pt: 4,
                  borderTop: `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
                }}
              >
                {[
                  { value: '99.2%', label: 'Accuracy' },
                  { value: '<2s', label: 'Response Time' },
                  { value: '4+', label: 'Platforms' },
                ].map((stat) => (
                  <Box key={stat.label}>
                    <Typography
                      sx={{
                        fontFamily: '"Space Grotesk", sans-serif',
                        fontWeight: 700,
                        fontSize: { xs: '1.5rem', md: '2rem' },
                        color: brandColors.primary.signalTeal,
                      }}
                    >
                      {stat.value}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        color: isDark ? '#7F8CA8' : '#7B8CA5',
                        fontSize: '0.75rem',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em',
                      }}
                    >
                      {stat.label}
                    </Typography>
                  </Box>
                ))}
              </MotionBox>
            </MotionBox>
          </Grid>

          {/* Visual/Illustration side */}
          <Grid size={{ xs: 12, md: 5 }} sx={{ display: { xs: 'none', md: 'block' } }}>
            <MotionBox
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.3, ease: [0.4, 0, 0.2, 1] }}
              sx={{
                position: 'relative',
                width: '100%',
                height: 400,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {/* Shield visualization */}
              <Box
                sx={{
                  width: 280,
                  height: 320,
                  position: 'relative',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    inset: 0,
                    background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}30 0%, ${brandColors.primary.signalTeal}30 100%)`,
                    borderRadius: '50% 50% 50% 50% / 60% 60% 40% 40%',
                    border: `2px solid ${brandColors.primary.signalTeal}50`,
                    animation: 'pulse-glow 3s infinite',
                  },
                  '@keyframes pulse-glow': {
                    '0%, 100%': { boxShadow: `0 0 30px ${brandColors.primary.signalTeal}30` },
                    '50%': { boxShadow: `0 0 60px ${brandColors.primary.signalTeal}50` },
                  },
                }}
              >
                {/* Inner rings */}
                {[0.8, 0.6, 0.4].map((scale, i) => (
                  <Box
                    key={i}
                    sx={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      width: `${scale * 100}%`,
                      height: `${scale * 100}%`,
                      transform: 'translate(-50%, -50%)',
                      borderRadius: '50%',
                      border: `1px solid ${brandColors.primary.signalTeal}${30 - i * 10}`,
                      animation: `orbit ${3 + i}s linear infinite`,
                      '@keyframes orbit': {
                        from: { transform: 'translate(-50%, -50%) rotate(0deg)' },
                        to: { transform: 'translate(-50%, -50%) rotate(360deg)' },
                      },
                    }}
                  />
                ))}
                {/* Center icon */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: 80,
                    height: 80,
                    borderRadius: '50%',
                    background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: `0 0 40px ${brandColors.primary.signalTeal}60`,
                  }}
                >
                  <Typography sx={{ fontSize: '2rem' }}>🛡️</Typography>
                </Box>
              </Box>
            </MotionBox>
          </Grid>
        </Grid>
      </Container>

      {/* Scroll indicator */}
      <MotionBox
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 0.5 }}
        sx={{
          position: 'absolute',
          bottom: 40,
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 1,
          cursor: 'pointer',
        }}
        onClick={() => document.getElementById('problem')?.scrollIntoView({ behavior: 'smooth' })}
      >
        <Typography
          variant="caption"
          sx={{
            color: isDark ? '#7F8CA8' : '#7B8CA5',
            fontSize: '0.7rem',
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
          }}
        >
          Scroll to explore
        </Typography>
        <Box
          sx={{
            width: 20,
            height: 32,
            borderRadius: 10,
            border: `2px solid ${isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)'}`,
            display: 'flex',
            justifyContent: 'center',
            pt: 1,
          }}
        >
          <Box
            sx={{
              width: 4,
              height: 8,
              borderRadius: 2,
              background: brandColors.primary.signalTeal,
              animation: 'scroll-bounce 1.5s infinite',
              '@keyframes scroll-bounce': {
                '0%, 100%': { transform: 'translateY(0)' },
                '50%': { transform: 'translateY(6px)' },
              },
            }}
          />
        </Box>
      </MotionBox>
    </Box>
  );
};

export default HeroSection;
