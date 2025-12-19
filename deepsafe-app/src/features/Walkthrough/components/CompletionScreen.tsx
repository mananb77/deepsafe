import React from 'react';
import { Box, Typography, Button, IconButton } from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Close as CloseIcon,
  Replay as ReplayIcon,
  ArrowForward as ArrowIcon,
  Help as HelpIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { brandColors } from '../../../theme/colors';
import { useThemeMode } from '../../../context/ThemeContext';
import { useWalkthroughContext } from '../context/WalkthroughContext';
import {
  modalBackdropVariants,
  welcomeModalVariants,
  successIconVariants,
  successMetricVariants,
} from '../constants/animations';

const MotionBox = motion.create(Box);

interface CompletionScreenProps {
  isOpen: boolean;
  onClose: () => void;
  onRestart: () => void;
}

export const CompletionScreen: React.FC<CompletionScreenProps> = ({
  isOpen,
  onClose,
  onRestart,
}) => {
  const { isDark } = useThemeMode();
  const { state, currentStepConfig } = useWalkthroughContext();
  const navigate = useNavigate();

  const metrics = currentStepConfig.modalContent?.metrics || {
    stepsCompleted: state.visitedSteps.length,
    featuresExplored: state.visitedHotspots.size,
  };

  const nextSteps = currentStepConfig.modalContent?.nextSteps || [
    'Review your first high-risk meeting',
    'Configure your alert thresholds',
    'Connect your video platforms',
  ];

  const handleGoToSupport = () => {
    onClose();
    navigate('/app/support');
  };

  const handleContinueToDashboard = () => {
    onClose();
  };

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
          onClick={handleContinueToDashboard}
        >
          <MotionBox
            variants={welcomeModalVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            onClick={(e) => e.stopPropagation()}
            sx={{
              width: '100%',
              maxWidth: 560,
              backgroundColor: isDark ? brandColors.dark.elevated : '#fff',
              borderRadius: 3,
              overflow: 'hidden',
              boxShadow: isDark
                ? '0 24px 48px rgba(0, 0, 0, 0.5)'
                : '0 24px 48px rgba(0, 0, 0, 0.2)',
            }}
          >
            {/* Header with success gradient */}
            <Box
              sx={{
                background: `linear-gradient(135deg, ${brandColors.statusDark.success} 0%, ${brandColors.primary.signalTeal} 100%)`,
                p: 4,
                textAlign: 'center',
                position: 'relative',
              }}
            >
              <IconButton
                onClick={handleContinueToDashboard}
                sx={{
                  position: 'absolute',
                  top: 12,
                  right: 12,
                  color: 'rgba(255, 255, 255, 0.7)',
                  '&:hover': {
                    color: '#fff',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  },
                }}
              >
                <CloseIcon />
              </IconButton>

              {/* Animated success icon */}
              <MotionBox
                variants={successIconVariants}
                initial="initial"
                animate="animate"
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 2,
                }}
              >
                <CheckIcon sx={{ fontSize: 48, color: '#fff' }} />
              </MotionBox>

              <Typography
                variant="h4"
                sx={{
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 700,
                  color: '#fff',
                  mb: 1,
                }}
              >
                You're Ready!
              </Typography>
              <Typography
                sx={{
                  color: 'rgba(255, 255, 255, 0.9)',
                }}
              >
                You've completed the DeepSafe dashboard walkthrough
              </Typography>
            </Box>

            {/* Metrics */}
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                gap: 4,
                py: 3,
                px: 4,
                borderBottom: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
              }}
            >
              <MotionBox
                variants={successMetricVariants}
                initial="initial"
                animate="animate"
                custom={0}
                sx={{ textAlign: 'center' }}
              >
                <Typography
                  variant="h3"
                  sx={{
                    fontFamily: '"JetBrains Mono", monospace',
                    fontWeight: 700,
                    background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  {metrics.stepsCompleted}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                  }}
                >
                  Steps Completed
                </Typography>
              </MotionBox>

              <MotionBox
                variants={successMetricVariants}
                initial="initial"
                animate="animate"
                custom={1}
                sx={{ textAlign: 'center' }}
              >
                <Typography
                  variant="h3"
                  sx={{
                    fontFamily: '"JetBrains Mono", monospace',
                    fontWeight: 700,
                    background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.statusDark.success} 100%)`,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  {metrics.featuresExplored}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                  }}
                >
                  Features Explored
                </Typography>
              </MotionBox>
            </Box>

            {/* Next steps */}
            <Box sx={{ p: 4 }}>
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 600,
                  color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                  mb: 2,
                }}
              >
                Recommended Next Steps
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, mb: 4 }}>
                {nextSteps.map((step, index) => (
                  <MotionBox
                    key={index}
                    variants={successMetricVariants}
                    initial="initial"
                    animate="animate"
                    custom={index + 2}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 2,
                      p: 1.5,
                      borderRadius: 1.5,
                      backgroundColor: isDark
                        ? 'rgba(255, 255, 255, 0.03)'
                        : 'rgba(0, 0, 0, 0.02)',
                    }}
                  >
                    <ArrowIcon
                      sx={{
                        fontSize: 18,
                        color: brandColors.primary.signalTeal,
                      }}
                    />
                    <Typography
                      sx={{
                        color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                      }}
                    >
                      {step}
                    </Typography>
                  </MotionBox>
                ))}
              </Box>

              {/* Action buttons */}
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  onClick={onRestart}
                  startIcon={<ReplayIcon />}
                  sx={{
                    borderColor: isDark ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)',
                    color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                    '&:hover': {
                      borderColor: isDark ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.3)',
                    },
                  }}
                >
                  Take Tour Again
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleGoToSupport}
                  startIcon={<HelpIcon />}
                  sx={{
                    borderColor: isDark ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)',
                    color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                    '&:hover': {
                      borderColor: isDark ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.3)',
                    },
                  }}
                >
                  Help Center
                </Button>
                <Button
                  variant="contained"
                  onClick={handleContinueToDashboard}
                  startIcon={<ArrowIcon />}
                  sx={{
                    flex: 1,
                    background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                    color: '#fff',
                    fontWeight: 600,
                    '&:hover': {
                      background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 20%, ${brandColors.primary.signalTeal} 100%)`,
                    },
                  }}
                >
                  Continue to Dashboard
                </Button>
              </Box>
            </Box>
          </MotionBox>
        </MotionBox>
      )}
    </AnimatePresence>
  );
};

export default CompletionScreen;
