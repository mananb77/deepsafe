import { useEffect, useRef, useCallback } from 'react';
import type { PlaybackSpeed } from '../types/demo.types';
import { SPEED_DURATIONS } from '../types/demo.types';
import { useDemoContext } from '../context/DemoContext';
import { DEMO_TOTAL_STEPS } from '../data/demoScenario';

// Speed multipliers for playback
const SPEED_MULTIPLIERS: Record<PlaybackSpeed, number> = {
  slow: 2,      // 0.5x = takes 2x longer
  normal: 1,    // 1x = normal speed
  fast: 0.5,    // 2x = takes half the time
};

/**
 * Hook for managing auto-play functionality
 * Automatically advances to the next step based on playback speed
 */
export const useAutoPlay = () => {
  const { state, dispatch, currentStepConfig } = useDemoContext();
  const { isPlaying, playbackSpeed, currentStep } = state;
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Clear timer on unmount or when dependencies change
  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  useEffect(() => {
    // Clear existing timer
    clearTimer();

    // Don't start timer if not playing or at last step
    if (!isPlaying || currentStep >= DEMO_TOTAL_STEPS) {
      return;
    }

    // Get base duration: step-specific (in seconds) or default from SPEED_DURATIONS (in ms)
    const baseDuration = currentStepConfig.duration > 0
      ? currentStepConfig.duration * 1000
      : SPEED_DURATIONS[playbackSpeed];

    // Apply speed multiplier
    const stepDuration = baseDuration * SPEED_MULTIPLIERS[playbackSpeed];

    // Start new timer
    timerRef.current = setTimeout(() => {
      dispatch({ type: 'NEXT_STEP' });
    }, stepDuration);

    return clearTimer;
  }, [isPlaying, playbackSpeed, currentStep, currentStepConfig.duration, dispatch, clearTimer]);

  // Return controls for manual override
  return {
    isPlaying,
    playbackSpeed,
    play: () => dispatch({ type: 'TOGGLE_PLAY' }),
    pause: () => {
      if (isPlaying) dispatch({ type: 'TOGGLE_PLAY' });
    },
    setSpeed: (speed: PlaybackSpeed) => dispatch({ type: 'SET_SPEED', speed }),
    clearTimer,
  };
};

export default useAutoPlay;
