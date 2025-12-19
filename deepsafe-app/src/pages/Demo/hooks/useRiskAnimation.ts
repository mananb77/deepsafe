import { useState, useEffect, useRef } from 'react';

/**
 * Easing function for smooth animations
 */
const easeOutCubic = (x: number): number => {
  return 1 - Math.pow(1 - x, 3);
};

interface UseRiskAnimationOptions {
  duration?: number;
  enabled?: boolean;
  onComplete?: () => void;
}

/**
 * Hook for animating risk score changes
 * Provides smooth transitions between score values
 */
export const useRiskAnimation = (
  targetScore: number,
  options: UseRiskAnimationOptions = {}
) => {
  const { duration = 1500, enabled = true, onComplete } = options;
  const [displayScore, setDisplayScore] = useState(targetScore);
  const prevScore = useRef(targetScore);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    // If animation is disabled, just set the score directly
    if (!enabled) {
      setDisplayScore(targetScore);
      prevScore.current = targetScore;
      return;
    }

    // Cancel any existing animation
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }

    const startScore = prevScore.current;
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutCubic(progress);
      const current = Math.round(startScore + (targetScore - startScore) * eased);

      setDisplayScore(current);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        prevScore.current = targetScore;
        onComplete?.();
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [targetScore, duration, enabled, onComplete]);

  return displayScore;
};

/**
 * Hook for animating multiple risk scores simultaneously
 */
export const useMultipleRiskAnimations = (
  scores: Record<string, number>,
  options: UseRiskAnimationOptions = {}
) => {
  const { duration = 1500, enabled = true } = options;
  const [displayScores, setDisplayScores] = useState(scores);
  const prevScores = useRef(scores);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    if (!enabled) {
      setDisplayScores(scores);
      prevScores.current = scores;
      return;
    }

    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }

    const startScores = { ...prevScores.current };
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutCubic(progress);

      const currentScores: Record<string, number> = {};
      for (const key of Object.keys(scores)) {
        const startValue = startScores[key] ?? 0;
        const targetValue = scores[key];
        currentScores[key] = Math.round(startValue + (targetValue - startValue) * eased);
      }

      setDisplayScores(currentScores);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        prevScores.current = scores;
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [scores, duration, enabled]);

  return displayScores;
};

/**
 * Hook for counting up to a number (for success screen metrics)
 */
export const useCountUp = (
  targetValue: number,
  options: {
    duration?: number;
    delay?: number;
    prefix?: string;
    suffix?: string;
    formatter?: (value: number) => string;
  } = {}
) => {
  const {
    duration = 2000,
    delay = 0,
    prefix = '',
    suffix = '',
    formatter = (v) => v.toLocaleString(),
  } = options;
  const [displayValue, setDisplayValue] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    const delayTimeout = setTimeout(() => {
      setIsAnimating(true);
      const startTime = Date.now();

      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = easeOutCubic(progress);
        const current = Math.round(targetValue * eased);

        setDisplayValue(current);

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          setIsAnimating(false);
        }
      };

      requestAnimationFrame(animate);
    }, delay);

    return () => clearTimeout(delayTimeout);
  }, [targetValue, duration, delay]);

  return {
    value: displayValue,
    formattedValue: `${prefix}${formatter(displayValue)}${suffix}`,
    isAnimating,
  };
};

export default useRiskAnimation;
