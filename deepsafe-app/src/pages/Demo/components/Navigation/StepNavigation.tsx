import React, { useState, useEffect, useRef } from 'react';
import { Box, IconButton, Typography, Tooltip } from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ArrowForward as ArrowForwardIcon,
  Replay as ReplayIcon,
} from '@mui/icons-material';
import { useDemoContext } from '../../context/DemoContext';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { DEMO_TOTAL_STEPS } from '../../data/demoScenario';
import { SPEED_DURATIONS } from '../../types/demo.types';
import ProgressIndicator from './ProgressIndicator';
import AutoPlayControls from './AutoPlayControls';

// Speed multipliers for playback (must match useAutoPlay)
const SPEED_MULTIPLIERS: Record<'slow' | 'normal' | 'fast', number> = {
  slow: 2,      // 0.5x = takes 2x longer
  normal: 1,    // 1x = normal speed
  fast: 0.5,    // 2x = takes half the time
};

const StepNavigation: React.FC = () => {
  const { state, dispatch, canGoBack, canGoForward, currentStepConfig } = useDemoContext();
  const { isDark } = useThemeMode();
  const [progress, setProgress] = useState(0);
  const startTimeRef = useRef<number>(Date.now());
  const animationRef = useRef<number | null>(null);

  // Calculate step duration in ms (must match useAutoPlay calculation)
  const baseDuration = currentStepConfig.duration > 0
    ? currentStepConfig.duration * 1000
    : SPEED_DURATIONS[state.playbackSpeed];
  const stepDuration = baseDuration * SPEED_MULTIPLIERS[state.playbackSpeed];

  // Progress bar animation
  useEffect(() => {
    // Reset progress when step changes
    setProgress(0);
    startTimeRef.current = Date.now();

    if (!state.isPlaying || state.currentStep >= DEMO_TOTAL_STEPS) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
      return;
    }

    const animate = () => {
      const elapsed = Date.now() - startTimeRef.current;
      const newProgress = Math.min((elapsed / stepDuration) * 100, 100);
      setProgress(newProgress);

      if (newProgress < 100 && state.isPlaying) {
        animationRef.current = requestAnimationFrame(animate);
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [state.isPlaying, state.currentStep, stepDuration, state.playbackSpeed]);

  const handleReset = () => {
    dispatch({ type: 'RESET_DEMO' });
  };

  return (
    <Box
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
        zIndex: 100,
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
            Step {state.currentStep} of {DEMO_TOTAL_STEPS}
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
          {/* Replay Button */}
          <Tooltip title="Replay Demo (R)">
            <IconButton
              onClick={handleReset}
              size="small"
              sx={{
                color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                '&:hover': {
                  color: brandColors.primary.signalTeal,
                  backgroundColor: isDark
                    ? 'rgba(31, 182, 166, 0.1)'
                    : 'rgba(31, 182, 166, 0.08)',
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
                onClick={() => dispatch({ type: 'PREV_STEP' })}
                disabled={!canGoBack}
                sx={{
                  color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                  '&:disabled': {
                    color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                  },
                  '&:hover:not(:disabled)': {
                    backgroundColor: isDark
                      ? 'rgba(255, 255, 255, 0.08)'
                      : 'rgba(0, 0, 0, 0.04)',
                  },
                }}
              >
                <ArrowBackIcon />
              </IconButton>
            </span>
          </Tooltip>

          {/* Progress Indicator */}
          <ProgressIndicator
            currentStep={state.currentStep}
            totalSteps={DEMO_TOTAL_STEPS}
            onStepClick={(step) => dispatch({ type: 'GO_TO_STEP', step })}
          />

          {/* Next Button */}
          <Tooltip title="Next Step (→)">
            <span>
              <IconButton
                onClick={() => dispatch({ type: 'NEXT_STEP' })}
                disabled={!canGoForward}
                sx={{
                  color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                  '&:disabled': {
                    color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                  },
                  '&:hover:not(:disabled)': {
                    backgroundColor: isDark
                      ? 'rgba(255, 255, 255, 0.08)'
                      : 'rgba(0, 0, 0, 0.04)',
                  },
                }}
              >
                <ArrowForwardIcon />
              </IconButton>
            </span>
          </Tooltip>

          {/* Horizontal Progress Bar / Divider with Countdown */}
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              mx: 2,
              gap: 0.5,
            }}
          >
            <Box
              sx={{
                width: 80,
                height: 4,
                borderRadius: 2,
                backgroundColor: isDark
                  ? 'rgba(255, 255, 255, 0.15)'
                  : 'rgba(0, 0, 0, 0.12)',
                overflow: 'hidden',
                position: 'relative',
              }}
            >
              {/* Animated progress fill when autoplay is active */}
              {state.isPlaying && state.currentStep < DEMO_TOTAL_STEPS && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    bottom: 0,
                    width: `${progress}%`,
                    backgroundColor: brandColors.primary.signalTeal,
                    borderRadius: 2,
                    transition: 'width 0.1s linear',
                    boxShadow: `0 0 8px ${brandColors.primary.signalTeal}60`,
                  }}
                />
              )}
            </Box>
            {/* Countdown text */}
            {state.isPlaying && state.currentStep < DEMO_TOTAL_STEPS && (
              <Typography
                variant="caption"
                sx={{
                  color: brandColors.primary.signalTeal,
                  fontSize: '0.6rem',
                  fontWeight: 500,
                  whiteSpace: 'nowrap',
                }}
              >
                {Math.max(0, Math.ceil((stepDuration - (progress / 100) * stepDuration) / 1000))}s
              </Typography>
            )}
          </Box>

          {/* Auto-play Controls */}
          <AutoPlayControls />
        </Box>
      </Box>
    </Box>
  );
};

export default StepNavigation;
