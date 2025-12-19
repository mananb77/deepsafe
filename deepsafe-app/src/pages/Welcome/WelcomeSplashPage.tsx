import React from 'react';
import { Box, Typography, Container, useMediaQuery, useTheme } from '@mui/material';
import {
  Dashboard as DashboardIcon,
  PlayCircleOutline as PlayIcon,
  Security as SecurityIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useThemeMode } from '../../context/ThemeContext';
import { useWalkthroughContext } from '../../features/Walkthrough';
import { brandColors } from '../../theme/colors';

const MotionBox = motion.create(Box);

export const WelcomeSplashPage: React.FC = () => {
  const navigate = useNavigate();
  const { isDark } = useThemeMode();
  const { startWalkthrough } = useWalkthroughContext();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleGoDashboard = () => {
    navigate('/app/dashboard');
  };

  const handleStartTour = () => {
    startWalkthrough();
    navigate('/app/dashboard');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: isDark
          ? `radial-gradient(ellipse at top, ${brandColors.dark.surface} 0%, ${brandColors.dark.deepest} 100%)`
          : `radial-gradient(ellipse at top, ${brandColors.light.primary} 0%, ${brandColors.light.surface} 100%)`,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background decoration */}
      <Box
        sx={{
          position: 'absolute',
          top: '20%',
          left: '10%',
          width: 400,
          height: 400,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${brandColors.primary.deepSafeBlue}15 0%, transparent 70%)`,
          filter: 'blur(60px)',
          pointerEvents: 'none',
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: '20%',
          right: '10%',
          width: 300,
          height: 300,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${brandColors.primary.signalTeal}15 0%, transparent 70%)`,
          filter: 'blur(60px)',
          pointerEvents: 'none',
        }}
      />

      <Container maxWidth="md">
        <MotionBox
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] as const }}
          sx={{
            textAlign: 'center',
            position: 'relative',
            zIndex: 1,
          }}
        >
          {/* Logo */}
          <MotionBox
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: { xs: 1.5, sm: 2 },
              mb: { xs: 3, sm: 4 },
            }}
          >
            <Box
              sx={{
                width: { xs: 48, sm: 64 },
                height: { xs: 48, sm: 64 },
                borderRadius: { xs: '12px', sm: '16px' },
                background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: `0 8px 32px ${brandColors.primary.deepSafeBlue}40`,
              }}
            >
              <SecurityIcon sx={{ color: '#FFFFFF', fontSize: { xs: 24, sm: 32 } }} />
            </Box>
            <Typography
              variant="h3"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 700,
                fontSize: { xs: '1.75rem', sm: '2.5rem', md: '3rem' },
                background: isDark
                  ? `linear-gradient(90deg, ${brandColors.darkText.primary} 0%, ${brandColors.primary.signalTeal} 100%)`
                  : `linear-gradient(90deg, ${brandColors.lightText.primary} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              DeepSafe
            </Typography>
          </MotionBox>

          {/* Welcome Text */}
          <MotionBox
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
          >
            <Typography
              variant="h4"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2rem' },
                color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                mb: 2,
              }}
            >
              Welcome to the Dashboard
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                maxWidth: 500,
                mx: 'auto',
                mb: { xs: 4, sm: 6 },
                px: { xs: 2, sm: 0 },
                lineHeight: 1.7,
                fontSize: { xs: '0.9rem', sm: '1rem' },
              }}
            >
              Monitor your organization's security posture, detect deepfake threats in real-time,
              and protect your team from AI-powered attacks.
            </Typography>
          </MotionBox>

          {/* Action Cards */}
          <MotionBox
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              gap: { xs: 2, sm: 3 },
              justifyContent: 'center',
              alignItems: { xs: 'center', sm: 'stretch' },
              px: { xs: 2, sm: 0 },
            }}
          >
            {/* Guided Tour Option */}
            <Box
              onClick={handleStartTour}
              sx={{
                flex: 1,
                width: { xs: '100%', sm: 'auto' },
                maxWidth: { xs: '100%', sm: 320 },
                p: { xs: 3, sm: 4 },
                borderRadius: { xs: 3, sm: 4 },
                background: isDark
                  ? `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}20 0%, ${brandColors.primary.signalTeal}10 100%)`
                  : `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}10 0%, ${brandColors.primary.signalTeal}05 100%)`,
                border: `2px solid ${brandColors.primary.signalTeal}40`,
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                // Better touch feedback
                WebkitTapHighlightColor: 'transparent',
                '&:hover': {
                  transform: isMobile ? 'none' : 'translateY(-4px)',
                  boxShadow: `0 12px 40px ${brandColors.primary.signalTeal}30`,
                  borderColor: brandColors.primary.signalTeal,
                },
                '&:active': {
                  transform: 'scale(0.98)',
                },
              }}
            >
              <Box
                sx={{
                  width: { xs: 48, sm: 56 },
                  height: { xs: 48, sm: 56 },
                  borderRadius: { xs: '12px', sm: '14px' },
                  background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: { xs: 2, sm: 3 },
                }}
              >
                <PlayIcon sx={{ color: '#FFFFFF', fontSize: { xs: 24, sm: 28 } }} />
              </Box>
              <Typography
                variant="h6"
                sx={{
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 600,
                  fontSize: { xs: '1rem', sm: '1.25rem' },
                  color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                  mb: 1.5,
                }}
              >
                Take a Guided Tour
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                  mb: 2,
                  lineHeight: 1.6,
                  fontSize: { xs: '0.85rem', sm: '0.875rem' },
                }}
              >
                New here? Let us walk you through all the features in about 5 minutes.
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: brandColors.primary.signalTeal,
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 0.5,
                  fontSize: { xs: '0.7rem', sm: '0.75rem' },
                }}
              >
                Recommended for first-time users
              </Typography>
            </Box>

            {/* Go to Dashboard Option */}
            <Box
              onClick={handleGoDashboard}
              sx={{
                flex: 1,
                width: { xs: '100%', sm: 'auto' },
                maxWidth: { xs: '100%', sm: 320 },
                p: { xs: 3, sm: 4 },
                borderRadius: { xs: 3, sm: 4 },
                background: isDark
                  ? brandColors.dark.elevated
                  : brandColors.light.surface,
                border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)'}`,
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                WebkitTapHighlightColor: 'transparent',
                '&:hover': {
                  transform: isMobile ? 'none' : 'translateY(-4px)',
                  boxShadow: isDark
                    ? '0 12px 40px rgba(0,0,0,0.4)'
                    : '0 12px 40px rgba(0,0,0,0.1)',
                  borderColor: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.15)',
                },
                '&:active': {
                  transform: 'scale(0.98)',
                },
              }}
            >
              <Box
                sx={{
                  width: { xs: 48, sm: 56 },
                  height: { xs: 48, sm: 56 },
                  borderRadius: { xs: '12px', sm: '14px' },
                  background: isDark
                    ? 'rgba(255,255,255,0.1)'
                    : 'rgba(0,0,0,0.05)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: { xs: 2, sm: 3 },
                }}
              >
                <DashboardIcon
                  sx={{
                    color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                    fontSize: { xs: 24, sm: 28 },
                  }}
                />
              </Box>
              <Typography
                variant="h6"
                sx={{
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 600,
                  fontSize: { xs: '1rem', sm: '1.25rem' },
                  color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                  mb: 1.5,
                }}
              >
                Go to Dashboard
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                  mb: 2,
                  lineHeight: 1.6,
                  fontSize: { xs: '0.85rem', sm: '0.875rem' },
                }}
              >
                Jump straight into the dashboard and explore on your own.
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 0.5,
                  fontSize: { xs: '0.7rem', sm: '0.75rem' },
                }}
              >
                <ArrowForwardIcon sx={{ fontSize: { xs: 12, sm: 14 } }} />
                Skip the tour
              </Typography>
            </Box>
          </MotionBox>

          {/* Footer note */}
          <MotionBox
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.5 }}
            sx={{ mt: { xs: 4, sm: 6 } }}
          >
            <Typography
              variant="caption"
              sx={{
                color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                fontSize: { xs: '0.7rem', sm: '0.75rem' },
              }}
            >
              You can always access the tour later from the Support page
            </Typography>
          </MotionBox>
        </MotionBox>
      </Container>
    </Box>
  );
};

export default WelcomeSplashPage;
