import React from 'react';
import { Box, Typography, Button, Avatar, Chip, IconButton } from '@mui/material';
import { motion } from 'framer-motion';
import {
  Videocam as VideoIcon,
  Mic as MicIcon,
  Security as SecurityIcon,
  MoreVert as MoreIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { darkGradients, lightGradients, glassMorphism } from '../../../../theme/gradients';
import { useDemoContext } from '../../context/DemoContext';
import { screenVariants, staggerContainerVariants, staggerItemVariants } from '../../constants/animations';
import { demoParticipants } from '../../data/demoScenario';

const MotionBox = motion.create(Box);

export const LobbyScreen: React.FC = () => {
  const { isDark } = useThemeMode();
  const { dispatch } = useDemoContext();
  const gradients = isDark ? darkGradients : lightGradients;
  const glass = glassMorphism(isDark ? 'dark' : 'light');

  // Get CFO (the user's perspective)
  const user = demoParticipants.find((p) => p.id === 'sarah-chen')!;

  const handleJoin = () => {
    dispatch({ type: 'NEXT_STEP' });
  };

  return (
    <MotionBox
      variants={screenVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: gradients.signature,
        px: 3,
        py: 6,
      }}
    >
      <MotionBox
        variants={staggerContainerVariants}
        initial="initial"
        animate="animate"
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          gap: 4,
          alignItems: 'center',
          maxWidth: 900,
          width: '100%',
        }}
      >
        {/* Camera Preview */}
        <MotionBox
          variants={staggerItemVariants}
          sx={{
            flex: 1,
            maxWidth: 500,
            width: '100%',
          }}
        >
          <Box
            sx={{
              position: 'relative',
              aspectRatio: '16/9',
              borderRadius: 3,
              overflow: 'hidden',
              ...glass,
              border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'}`,
            }}
          >
            {/* Simulated camera preview - dark with avatar */}
            <Box
              sx={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: isDark ? '#0B1220' : '#1A2740',
              }}
            >
              <Avatar
                sx={{
                  width: 80,
                  height: 80,
                  mb: 2,
                  fontSize: '2rem',
                  backgroundColor: brandColors.primary.deepSafeBlue,
                }}
              >
                {user.name.charAt(0)}
              </Avatar>
              <Typography
                variant="body1"
                sx={{ color: '#FFFFFF', fontWeight: 500 }}
              >
                {user.name}
              </Typography>
            </Box>

            {/* Camera/Mic controls */}
            <Box
              sx={{
                position: 'absolute',
                bottom: 16,
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                gap: 2,
              }}
            >
              <IconButton
                sx={{
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: '#FFFFFF',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  },
                }}
              >
                <MicIcon />
              </IconButton>
              <IconButton
                sx={{
                  backgroundColor: brandColors.primary.threatRed,
                  color: '#FFFFFF',
                  '&:hover': {
                    backgroundColor: '#B83A3A',
                  },
                }}
              >
                <VideoIcon />
              </IconButton>
            </Box>

            {/* DeepSafe Badge */}
            <Box
              id="deepsafe-badge"
              sx={{
                position: 'absolute',
                top: 12,
                right: 12,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                px: 1.5,
                py: 0.75,
                borderRadius: 2,
                backgroundColor: 'rgba(31, 182, 166, 0.15)',
                border: `1px solid ${brandColors.primary.signalTeal}40`,
              }}
            >
              <SecurityIcon
                sx={{ fontSize: 16, color: brandColors.primary.signalTeal }}
              />
              <Typography
                variant="caption"
                sx={{
                  color: brandColors.primary.signalTeal,
                  fontWeight: 600,
                  fontSize: '0.7rem',
                }}
              >
                Protected
              </Typography>
            </Box>
          </Box>
        </MotionBox>

        {/* Meeting Info & Join */}
        <MotionBox
          variants={staggerItemVariants}
          sx={{
            flex: 1,
            maxWidth: 350,
            width: '100%',
          }}
        >
          <Box
            sx={{
              p: 4,
              borderRadius: 3,
              ...glass,
              border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'}`,
            }}
          >
            {/* Meeting Title */}
            <Typography
              variant="h5"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                mb: 1,
              }}
            >
              Q4 Budget Review
            </Typography>

            <Typography
              variant="body2"
              sx={{
                color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                mb: 3,
              }}
            >
              with David Mitchell (CEO)
            </Typography>

            {/* Meeting Meta */}
            <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
              <Chip
                label="1 participant"
                size="small"
                sx={{
                  backgroundColor: isDark
                    ? 'rgba(255, 255, 255, 0.08)'
                    : 'rgba(0, 0, 0, 0.06)',
                  color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                }}
              />
              <Chip
                icon={<SecurityIcon sx={{ fontSize: 14 }} />}
                label="DeepSafe Active"
                size="small"
                sx={{
                  backgroundColor: 'rgba(31, 182, 166, 0.1)',
                  color: brandColors.primary.signalTeal,
                  '& .MuiChip-icon': {
                    color: brandColors.primary.signalTeal,
                  },
                }}
              />
            </Box>

            {/* Waiting Participants */}
            <Box sx={{ mb: 3 }}>
              <Typography
                variant="caption"
                sx={{
                  color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  fontWeight: 500,
                }}
              >
                In this meeting
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    fontSize: '0.875rem',
                    backgroundColor: brandColors.primary.deepSafeBlue,
                  }}
                >
                  DM
                </Avatar>
                <Typography
                  variant="body2"
                  sx={{
                    color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                    fontWeight: 500,
                  }}
                >
                  David Mitchell
                </Typography>
                <Chip
                  label="CEO"
                  size="small"
                  sx={{
                    height: 20,
                    fontSize: '0.65rem',
                    backgroundColor: isDark
                      ? 'rgba(255, 255, 255, 0.08)'
                      : 'rgba(0, 0, 0, 0.06)',
                    color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                  }}
                />
              </Box>
            </Box>

            {/* Join Button */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleJoin}
                sx={{
                  py: 1.5,
                  borderRadius: 2,
                  fontSize: '1rem',
                  fontWeight: 600,
                  textTransform: 'none',
                  backgroundColor: brandColors.primary.signalTeal,
                  '&:hover': {
                    backgroundColor: '#1AA396',
                  },
                }}
              >
                Join now
              </Button>
            </motion.div>

            {/* Additional options */}
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                mt: 2,
              }}
            >
              <Button
                size="small"
                startIcon={<MoreIcon />}
                sx={{
                  color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                  textTransform: 'none',
                  fontSize: '0.875rem',
                }}
              >
                Present to meeting
              </Button>
            </Box>
          </Box>
        </MotionBox>
      </MotionBox>

      {/* Step hint */}
      <MotionBox
        variants={staggerItemVariants}
        initial="initial"
        animate="animate"
        sx={{ mt: 4 }}
      >
        <Typography
          variant="caption"
          sx={{
            color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
          }}
        >
          Step 2 of 9 • Click &quot;Join now&quot; or press → to continue
        </Typography>
      </MotionBox>
    </MotionBox>
  );
};

export default LobbyScreen;
