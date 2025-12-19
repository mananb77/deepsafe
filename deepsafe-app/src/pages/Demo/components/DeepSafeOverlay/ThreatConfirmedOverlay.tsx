import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Stack, Chip, Divider } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Error as ErrorIcon,
  Person as PersonIcon,
  LocationOn as LocationIcon,
  Videocam as VideocamIcon,
  RecordVoiceOver as VoiceIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { useDemoContext } from '../../context/DemoContext';
import { demoParticipants } from '../../data/demoScenario';
import { demoForensicData } from '../../data/forensicData';
import { threatConfirmedVariants } from '../../constants/animations';

const MotionBox = motion(Box);
const MotionPaper = motion(Paper);

export const ThreatConfirmedOverlay: React.FC = () => {
  const { isDark } = useThemeMode();
  const { state, dispatch } = useDemoContext();
  const [showDetails, setShowDetails] = useState(false);
  const [removing, setRemoving] = useState(false);

  const attacker = demoParticipants.find((p) => p.isAttacker);

  // Auto-progress: show details, then remove participant
  useEffect(() => {
    if (!state.threatConfirmed) return;

    const timer1 = setTimeout(() => setShowDetails(true), 1000);
    const timer2 = setTimeout(() => setRemoving(true), 3500);
    const timer3 = setTimeout(() => {
      dispatch({ type: 'REMOVE_PARTICIPANT' });
    }, 4500);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [state.threatConfirmed, dispatch]);

  if (!state.threatConfirmed) return null;

  return (
    <AnimatePresence>
      <MotionBox
        variants={threatConfirmedVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        sx={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
          backgroundColor: 'rgba(0, 0, 0, 0.85)',
          backdropFilter: 'blur(8px)',
        }}
      >
        <Box sx={{ textAlign: 'center', maxWidth: 480, px: 3 }}>
          {/* Alert Icon */}
          <MotionBox
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            sx={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              backgroundColor: brandColors.statusDark.error,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              mb: 3,
              boxShadow: '0 0 40px rgba(214, 69, 69, 0.5)',
              animation: 'pulse 2s infinite',
              '@keyframes pulse': {
                '0%, 100%': {
                  boxShadow: '0 0 40px rgba(214, 69, 69, 0.5)',
                },
                '50%': {
                  boxShadow: '0 0 60px rgba(214, 69, 69, 0.7)',
                },
              },
            }}
          >
            <ErrorIcon sx={{ fontSize: 48, color: '#fff' }} />
          </MotionBox>

          {/* Title */}
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
              fontFamily: '"Space Grotesk", sans-serif',
              color: brandColors.statusDark.error,
              mb: 1,
              textShadow: '0 0 20px rgba(214, 69, 69, 0.5)',
            }}
          >
            THREAT CONFIRMED
          </Typography>

          <Typography
            variant="body1"
            sx={{
              color: 'rgba(255, 255, 255, 0.8)',
              mb: 3,
            }}
          >
            Deepfake impersonation detected with 92% confidence
          </Typography>

          {/* Forensic Summary Card */}
          <AnimatePresence>
            {showDetails && (
              <MotionPaper
                id="forensic-summary"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                elevation={0}
                sx={{
                  p: 2.5,
                  borderRadius: '16px',
                  backgroundColor: isDark
                    ? 'rgba(26, 32, 44, 0.95)'
                    : 'rgba(255, 255, 255, 0.95)',
                  border: `2px solid ${brandColors.statusDark.error}`,
                  textAlign: 'left',
                }}
              >
                {/* Attacker Info */}
                <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: '12px',
                      backgroundColor: 'rgba(214, 69, 69, 0.15)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <PersonIcon sx={{ color: brandColors.statusDark.error }} />
                  </Box>
                  <Box>
                    <Typography
                      variant="body2"
                      sx={{
                        color: isDark ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)',
                        fontSize: '0.75rem',
                      }}
                    >
                      Claimed Identity
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{
                        fontWeight: 600,
                        color: isDark ? '#fff' : '#333',
                        textDecoration: 'line-through',
                        textDecorationColor: brandColors.statusDark.error,
                      }}
                    >
                      {attacker?.name} (CEO)
                    </Typography>
                  </Box>
                </Stack>

                {/* Real Identity */}
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: '10px',
                    backgroundColor: 'rgba(214, 69, 69, 0.1)',
                    mb: 2,
                  }}
                >
                  <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
                    <LocationIcon
                      sx={{ fontSize: 16, color: brandColors.statusDark.error }}
                    />
                    <Typography
                      variant="caption"
                      sx={{ color: brandColors.statusDark.error, fontWeight: 600 }}
                    >
                      ACTUAL ORIGIN
                    </Typography>
                  </Stack>
                  <Typography
                    variant="body2"
                    sx={{ color: isDark ? 'rgba(255, 255, 255, 0.9)' : '#333' }}
                  >
                    {attacker?.realIdentity?.name} • {attacker?.realIdentity?.location}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      color: isDark ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)',
                    }}
                  >
                    VPN: {demoForensicData.networkAnalysis.vpnProvider} •{' '}
                    {demoForensicData.networkAnalysis.virtualCameraName}
                  </Typography>
                </Box>

                <Divider
                  sx={{
                    my: 2,
                    borderColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
                  }}
                />

                {/* Detection Scores */}
                <Stack direction="row" spacing={2}>
                  <Box sx={{ flex: 1 }}>
                    <Stack direction="row" alignItems="center" spacing={0.75} sx={{ mb: 0.5 }}>
                      <VideocamIcon
                        sx={{ fontSize: 14, color: brandColors.statusDark.error }}
                      />
                      <Typography
                        variant="caption"
                        sx={{ color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)' }}
                      >
                        Video
                      </Typography>
                    </Stack>
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 700, color: brandColors.statusDark.error }}
                    >
                      {demoForensicData.videoAnalysis.deepfakeConfidence}%
                    </Typography>
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Stack direction="row" alignItems="center" spacing={0.75} sx={{ mb: 0.5 }}>
                      <VoiceIcon
                        sx={{ fontSize: 14, color: brandColors.statusDark.warning }}
                      />
                      <Typography
                        variant="caption"
                        sx={{ color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)' }}
                      >
                        Audio
                      </Typography>
                    </Stack>
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 700, color: brandColors.statusDark.warning }}
                    >
                      {demoForensicData.audioAnalysis.voiceCloningConfidence}%
                    </Typography>
                  </Box>
                </Stack>
              </MotionPaper>
            )}
          </AnimatePresence>

          {/* Removing Status */}
          <AnimatePresence>
            {removing && (
              <MotionBox
                id="removal-notification"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                sx={{ mt: 3 }}
              >
                <Chip
                  label="Removing threat from meeting..."
                  sx={{
                    backgroundColor: brandColors.statusDark.error,
                    color: '#fff',
                    fontWeight: 600,
                    animation: 'pulse 1s infinite',
                  }}
                />
              </MotionBox>
            )}
          </AnimatePresence>
        </Box>
      </MotionBox>
    </AnimatePresence>
  );
};

export default ThreatConfirmedOverlay;
