import { useState, useEffect } from 'react';

/**
 * Hook to detect user's reduced motion preference
 * Respects the prefers-reduced-motion media query
 */
export const useReducedMotion = (): boolean => {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    // Check if we're in a browser environment
    if (typeof window === 'undefined') {
      return;
    }

    // Create media query
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    // Set initial value
    setReducedMotion(mediaQuery.matches);

    // Handler for changes
    const handler = (event: MediaQueryListEvent) => {
      setReducedMotion(event.matches);
    };

    // Listen for changes
    mediaQuery.addEventListener('change', handler);

    return () => {
      mediaQuery.removeEventListener('change', handler);
    };
  }, []);

  return reducedMotion;
};

/**
 * Get animation variants that respect reduced motion
 * Returns empty variants if reduced motion is preferred
 */
export const useMotionVariants = <T extends Record<string, unknown>>(
  variants: T,
  reducedVariants?: Partial<T>
): T => {
  const reducedMotion = useReducedMotion();

  if (reducedMotion) {
    // Return simplified variants or merge with reduced variants
    if (reducedVariants) {
      return { ...variants, ...reducedVariants } as T;
    }

    // Return variants with disabled animations
    const disabledVariants: Record<string, unknown> = {};
    for (const key of Object.keys(variants)) {
      disabledVariants[key] = {
        // Keep final state but remove animation
        ...(typeof variants[key] === 'object' ? variants[key] : {}),
        transition: { duration: 0 },
      };
    }
    return disabledVariants as T;
  }

  return variants;
};

export default useReducedMotion;
