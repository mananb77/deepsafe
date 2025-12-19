import React, { useEffect, useState, useCallback } from 'react';
import { Box, Typography, IconButton, Tooltip } from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ArrowForward as ArrowForwardIcon,
  Close as CloseIcon,
  Replay as ReplayIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { brandColors } from '../../../theme/colors';
import { useThemeMode } from '../../../context/ThemeContext';
import { useWalkthroughContext } from '../context/WalkthroughContext';
import { WelcomeModal } from './WelcomeModal';
import { CompletionScreen } from './CompletionScreen';
import { WalkthroughModal } from './WalkthroughModal';
import { Hotspot } from './Hotspots/Hotspot';
import { overlayVariants, instructionBannerVariants } from '../constants/animations';
import { SPEED_DURATIONS, SPEED_MULTIPLIERS } from '../types/walkthrough.types';
import type { WalkthroughHotspot } from '../types/walkthrough.types';

const MotionBox = motion.create(Box);

interface HotspotPosition {
  config: WalkthroughHotspot;
  position: { top: number; left: number } | null;
  placedOnLeft: boolean;
}

export const WalkthroughOverlay: React.FC = () => {
  const { isDark } = useThemeMode();
  const navigate = useNavigate();
  const {
    state,
    dispatch,
    currentStepConfig,
    canGoBack,
    canGoForward,
    activeHotspots,
    totalSteps,
    nextStep,
    prevStep,
    exitWalkthrough,
  } = useWalkthroughContext();

  const [hotspotPositions, setHotspotPositions] = useState<HotspotPosition[]>([]);
  const [progress, setProgress] = useState(0);

  // Calculate hotspot positions
  const calculatePositions = useCallback(() => {
    const screenWidth = window.innerWidth;
    const HOTSPOT_SIZE = 28;
    const HOTSPOT_MARGIN = 8;
    const SCREEN_EDGE_BUFFER = 60;

    const newPositions: HotspotPosition[] = activeHotspots.map((config) => {
      const anchorElement = document.querySelector(config.anchor);

      if (!anchorElement) {
        return { config, position: null, placedOnLeft: false };
      }

      const rect = anchorElement.getBoundingClientRect();
      const offsetX = config.offsetX || 0;
      const offsetY = config.offsetY || 0;

      let placeOnLeft = false;
      if (config.position === 'left') {
        placeOnLeft = true;
      } else if (config.position === 'right') {
        placeOnLeft = false;
      } else {
        const rightPosition = rect.right + HOTSPOT_MARGIN + HOTSPOT_SIZE;
        if (rightPosition > screenWidth - SCREEN_EDGE_BUFFER) {
          placeOnLeft = true;
        }
      }

      const left = placeOnLeft
        ? rect.left - HOTSPOT_SIZE - HOTSPOT_MARGIN + offsetX
        : rect.right + HOTSPOT_MARGIN + offsetX;

      return {
        config,
        position: {
          top: rect.top + rect.height / 2 - HOTSPOT_SIZE / 2 + offsetY,
          left: Math.max(HOTSPOT_MARGIN, Math.min(left, screenWidth - HOTSPOT_SIZE - HOTSPOT_MARGIN)),
        },
        placedOnLeft: placeOnLeft,
      };
    });

    setHotspotPositions(newPositions);
  }, [activeHotspots]);

  // Recalculate positions on step change
  useEffect(() => {
    if (!state.isActive || state.showWelcome || state.showCompletion) return;

    const timer = setTimeout(calculatePositions, 200);
    window.addEventListener('resize', calculatePositions);
    window.addEventListener('scroll', calculatePositions, true);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', calculatePositions);
      window.removeEventListener('scroll', calculatePositions, true);
    };
  }, [calculatePositions, state.isActive, state.showWelcome, state.showCompletion, state.currentStep]);

  // Auto-play progress
  useEffect(() => {
    if (!state.isPlaying || state.showWelcome || state.showCompletion) {
      setProgress(0);
      return;
    }

    const baseDuration = currentStepConfig.duration > 0
      ? currentStepConfig.duration * 1000
      : SPEED_DURATIONS[state.playbackSpeed];
    const stepDuration = baseDuration * SPEED_MULTIPLIERS[state.playbackSpeed];

    const startTime = Date.now();
    let animationFrame: number;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const newProgress = Math.min((elapsed / stepDuration) * 100, 100);
      setProgress(newProgress);

      if (newProgress >= 100) {
        nextStep();
      } else if (state.isPlaying) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [state.isPlaying, state.currentStep, state.playbackSpeed, currentStepConfig.duration, nextStep, state.showWelcome, state.showCompletion]);

  // Handle welcome modal
  const handleStartFromWelcome = () => {
    dispatch({ type: 'CLOSE_WELCOME' });
  };

  // Handle completion
  const handleCloseCompletion = () => {
    dispatch({ type: 'COMPLETE_WALKTHROUGH' });
    navigate('/app/dashboard');
  };

  const handleRestartFromCompletion = () => {
    dispatch({ type: 'RESET_WALKTHROUGH' });
  };

  // Handle exit
  const handleExit = () => {
    exitWalkthrough();
  };

  // Don't render if not active
  if (!state.isActive) return null;

  return (
    <>
      {/* Welcome Modal */}
      <WelcomeModal
        isOpen={state.showWelcome}
        onStart={handleStartFromWelcome}
      />

      {/* Completion Screen */}
      <CompletionScreen
        isOpen={state.showCompletion}
        onClose={handleCloseCompletion}
        onRestart={handleRestartFromCompletion}
      />

      {/* Hotspot Detail Modal */}
      <WalkthroughModal />

      {/* Main Overlay (when not showing modals) */}
      <AnimatePresence>
        {!state.showWelcome && !state.showCompletion && (
          <>
            {/* Instruction Banner */}
            {currentStepConfig.instruction && (
              <MotionBox
                variants={instructionBannerVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                sx={{
                  position: 'fixed',
                  top: 80,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  zIndex: 1300,
                  backgroundColor: isDark
                    ? 'rgba(31, 182, 166, 0.15)'
                    : 'rgba(31, 182, 166, 0.1)',
                  backdropFilter: 'blur(10px)',
                  border: `1px solid ${brandColors.primary.signalTeal}40`,
                  borderRadius: 2,
                  px: 3,
                  py: 1.5,
                  maxWidth: 500,
                }}
              >
                <Typography
                  sx={{
                    color: brandColors.primary.signalTeal,
                    fontWeight: 500,
                    textAlign: 'center',
                  }}
                >
                  {currentStepConfig.instruction}
                </Typography>
              </MotionBox>
            )}

            {/* Hotspots */}
            {hotspotPositions.map(({ config, position, placedOnLeft }) =>
              position ? (
                <Box
                  key={config.id}
                  sx={{
                    position: 'fixed',
                    top: position.top,
                    left: position.left,
                    zIndex: 1200,
                    pointerEvents: 'auto',
                  }}
                >
                  <Hotspot
                    config={config}
                    tooltipPosition={placedOnLeft ? 'left' : 'right'}
                  />
                </Box>
              ) : null
            )}

            {/* Bottom Navigation */}
            <MotionBox
              variants={overlayVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              sx={{
                position: 'fixed',
                bottom: 0,
                left: 0,
                right: 0,
                p: 2,
                background: isDark
                  ? 'linear-gradient(180deg, transparent 0%, rgba(5, 7, 12, 0.95) 30%)'
                  : 'linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.95) 30%)',
                backdropFilter: 'blur(10px)',
                zIndex: 1200,
              }}
            >
              <Box sx={{ maxWidth: 800, mx: 'auto' }}>
                {/* Step Info */}
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <Typography
                    variant="caption"
                    sx={{
                      color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                      textTransform: 'uppercase',
                      letterSpacing: 1,
                    }}
                  >
                    Step {state.currentStep} of {totalSteps} • {currentStepConfig.phase}
                  </Typography>
                  <Typography
                    variant="h6"
                    sx={{
                      fontFamily: '"Space Grotesk", sans-serif',
                      fontWeight: 600,
                      color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                    }}
                  >
                    {currentStepConfig.name}
                  </Typography>
                </Box>

                {/* Controls Row */}
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 2,
                  }}
                >
                  {/* Exit Button */}
                  <Tooltip title="Exit Walkthrough">
                    <IconButton
                      onClick={handleExit}
                      size="small"
                      sx={{
                        color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                        '&:hover': {
                          color: brandColors.primary.threatRed,
                          backgroundColor: 'rgba(214, 69, 69, 0.1)',
                        },
                      }}
                    >
                      <CloseIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>

                  {/* Replay Button */}
                  <Tooltip title="Restart Walkthrough">
                    <IconButton
                      onClick={() => dispatch({ type: 'RESET_WALKTHROUGH' })}
                      size="small"
                      sx={{
                        color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                        '&:hover': {
                          color: brandColors.primary.signalTeal,
                          backgroundColor: 'rgba(31, 182, 166, 0.1)',
                        },
                      }}
                    >
                      <ReplayIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>

                  {/* Back Button */}
                  <Tooltip title="Previous Step (←)">
                    <span>
                      <IconButton
                        onClick={prevStep}
                        disabled={!canGoBack}
                        sx={{
                          color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                          '&:disabled': {
                            color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                          },
                        }}
                      >
                        <ArrowBackIcon />
                      </IconButton>
                    </span>
                  </Tooltip>

                  {/* Progress Dots */}
                  <Box sx={{ display: 'flex', gap: 0.5, px: 2 }}>
                    {Array.from({ length: totalSteps }).map((_, index) => (
                      <Box
                        key={index}
                        onClick={() => dispatch({ type: 'GO_TO_STEP', step: index + 1 })}
                        sx={{
                          width: state.currentStep === index + 1 ? 24 : 8,
                          height: 8,
                          borderRadius: 4,
                          backgroundColor:
                            state.currentStep === index + 1
                              ? brandColors.primary.signalTeal
                              : state.visitedSteps.includes(index + 1)
                              ? isDark
                                ? 'rgba(255, 255, 255, 0.3)'
                                : 'rgba(0, 0, 0, 0.2)'
                              : isDark
                              ? 'rgba(255, 255, 255, 0.1)'
                              : 'rgba(0, 0, 0, 0.1)',
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            backgroundColor:
                              state.currentStep === index + 1
                                ? brandColors.primary.signalTeal
                                : brandColors.primary.signalTeal + '80',
                          },
                        }}
                      />
                    ))}
                  </Box>

                  {/* Next Button */}
                  <Tooltip title="Next Step (→)">
                    <span>
                      <IconButton
                        onClick={nextStep}
                        disabled={!canGoForward && state.currentStep === totalSteps}
                        sx={{
                          color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                          '&:disabled': {
                            color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                          },
                        }}
                      >
                        <ArrowForwardIcon />
                      </IconButton>
                    </span>
                  </Tooltip>

                  {/* Progress Bar */}
                  {state.isPlaying && (
                    <Box
                      sx={{
                        width: 80,
                        height: 4,
                        borderRadius: 2,
                        backgroundColor: isDark
                          ? 'rgba(255, 255, 255, 0.15)'
                          : 'rgba(0, 0, 0, 0.12)',
                        overflow: 'hidden',
                        ml: 2,
                      }}
                    >
                      <Box
                        sx={{
                          height: '100%',
                          width: `${progress}%`,
                          backgroundColor: brandColors.primary.signalTeal,
                          transition: 'width 0.1s linear',
                        }}
                      />
                    </Box>
                  )}
                </Box>
              </Box>
            </MotionBox>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default WalkthroughOverlay;
