import React from 'react';
import {
  Box,
  Typography,
  Button,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Timer as TimerIcon,
  TouchApp as TouchIcon,
  Lightbulb as TipIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { brandColors } from '../../../theme/colors';
import { useThemeMode } from '../../../context/ThemeContext';
import { modalBackdropVariants, welcomeModalVariants, staggerItemVariants } from '../constants/animations';

const MotionBox = motion.create(Box);

interface WelcomeModalProps {
  isOpen: boolean;
  onStart: () => void;
}

export const WelcomeModal: React.FC<WelcomeModalProps> = ({ isOpen, onStart }) => {
  const { isDark } = useThemeMode();

  const features = [
    { icon: <TouchIcon />, text: 'Interactive guided tour' },
    { icon: <TipIcon />, text: 'Hands-on feature exploration' },
    { icon: <TimerIcon />, text: 'Takes approximately 5-7 minutes' },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <MotionBox
          variants={modalBackdropVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          sx={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1400,
            p: 2,
          }}
        >
          <MotionBox
            variants={welcomeModalVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            onClick={(e) => e.stopPropagation()}
            sx={{
              width: '100%',
              maxWidth: 520,
              backgroundColor: isDark ? brandColors.dark.elevated : '#fff',
              borderRadius: 3,
              overflow: 'hidden',
              boxShadow: isDark
                ? '0 24px 48px rgba(0, 0, 0, 0.5)'
                : '0 24px 48px rgba(0, 0, 0, 0.2)',
            }}
          >
            {/* Header with gradient */}
            <Box
              sx={{
                background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                p: 4,
                pb: 5,
                position: 'relative',
              }}
            >
              <Typography
                variant="h4"
                sx={{
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 700,
                  color: '#fff',
                  mb: 1,
                }}
              >
                Welcome to DeepSafe
              </Typography>
              <Typography
                sx={{
                  color: 'rgba(255, 255, 255, 0.85)',
                  fontSize: '1.1rem',
                }}
              >
                Learn how to monitor and protect your organization from deepfake attacks
              </Typography>
            </Box>

            {/* Content */}
            <Box sx={{ p: 4 }}>
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 600,
                  color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                  mb: 2,
                }}
              >
                This interactive walkthrough will guide you through:
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 4 }}>
                {features.map((feature, index) => (
                  <MotionBox
                    key={index}
                    variants={staggerItemVariants}
                    initial="initial"
                    animate="animate"
                    custom={index}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 2,
                      p: 2,
                      borderRadius: 2,
                      backgroundColor: isDark
                        ? 'rgba(31, 182, 166, 0.1)'
                        : 'rgba(31, 182, 166, 0.08)',
                      border: `1px solid ${isDark ? 'rgba(31, 182, 166, 0.2)' : 'rgba(31, 182, 166, 0.15)'}`,
                    }}
                  >
                    <Box
                      sx={{
                        color: brandColors.primary.signalTeal,
                        display: 'flex',
                        alignItems: 'center',
                      }}
                    >
                      {feature.icon}
                    </Box>
                    <Typography
                      sx={{
                        color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                      }}
                    >
                      {feature.text}
                    </Typography>
                  </MotionBox>
                ))}
              </Box>

              {/* Single Start Tour button */}
              <Button
                variant="contained"
                onClick={onStart}
                startIcon={<PlayIcon />}
                fullWidth
                sx={{
                  py: 1.5,
                  background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                  color: '#fff',
                  fontWeight: 600,
                  fontSize: '1rem',
                  '&:hover': {
                    background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 20%, ${brandColors.primary.signalTeal} 100%)`,
                  },
                }}
              >
                Start Tour
              </Button>
            </Box>
          </MotionBox>
        </MotionBox>
      )}
    </AnimatePresence>
  );
};

export default WelcomeModal;
