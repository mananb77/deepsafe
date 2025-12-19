import type { Variants, Transition } from 'framer-motion';

// ============================================
// Animation Durations
// ============================================

export const ANIMATION_DURATIONS = {
  fast: 0.2,
  normal: 0.3,
  slow: 0.5,
  verySlow: 0.8,
} as const;

// ============================================
// Easing Functions
// ============================================

export const EASINGS = {
  ease: [0.25, 0.1, 0.25, 1] as const,
  easeIn: [0.42, 0, 1, 1] as const,
  easeOut: [0, 0, 0.58, 1] as const,
  easeInOut: [0.42, 0, 0.58, 1] as const,
};

// ============================================
// Default Transitions
// ============================================

export const TRANSITIONS: Record<string, Transition> = {
  default: { duration: ANIMATION_DURATIONS.normal, ease: EASINGS.easeOut },
  spring: { type: 'spring', stiffness: 300, damping: 30 },
  slow: { duration: ANIMATION_DURATIONS.slow, ease: EASINGS.easeInOut },
  fast: { duration: ANIMATION_DURATIONS.fast, ease: EASINGS.ease },
};

// ============================================
// Overlay & Backdrop Animations
// ============================================

export const overlayVariants: Variants = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: { duration: 0.3 },
  },
  exit: {
    opacity: 0,
    transition: { duration: 0.2 },
  },
};

export const spotlightVariants: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.4, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.2 },
  },
};

// ============================================
// Modal Animations
// ============================================

export const modalBackdropVariants: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

export const modalContentVariants: Variants = {
  initial: { opacity: 0, scale: 0.95, y: 10 },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: 0.2, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 10,
    transition: { duration: 0.15, ease: EASINGS.easeIn },
  },
};

export const welcomeModalVariants: Variants = {
  initial: { opacity: 0, scale: 0.9, y: 20 },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: EASINGS.easeOut,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    transition: { duration: 0.2 },
  },
};

// ============================================
// Hotspot Animations
// ============================================

export const hotspotPulseVariants: Variants = {
  initial: { scale: 1, opacity: 0.8 },
  animate: {
    scale: [1, 1.2, 1],
    opacity: [0.8, 1, 0.8],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

export const hotspotTooltipVariants: Variants = {
  initial: { opacity: 0, y: 5, scale: 0.95 },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.15, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    y: 5,
    scale: 0.95,
    transition: { duration: 0.1, ease: EASINGS.easeIn },
  },
};

// ============================================
// Instruction Banner Animations
// ============================================

export const instructionBannerVariants: Variants = {
  initial: { opacity: 0, y: -20 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: { duration: 0.2 },
  },
};

// ============================================
// Success/Completion Animations
// ============================================

export const successIconVariants: Variants = {
  initial: { scale: 0, rotate: -180 },
  animate: {
    scale: 1,
    rotate: 0,
    transition: { type: 'spring', stiffness: 200, damping: 15, delay: 0.2 },
  },
};

export const successMetricVariants: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: (custom: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.3 + custom * 0.1, duration: 0.4 },
  }),
};

export const confettiVariants: Variants = {
  initial: { opacity: 0, y: -50 },
  animate: {
    opacity: [0, 1, 1, 0],
    y: [0, 100, 200, 300],
    rotate: [0, 180, 360, 540],
    transition: { duration: 2, ease: 'easeOut' },
  },
};

// ============================================
// Stagger Children
// ============================================

export const staggerContainerVariants: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const staggerItemVariants: Variants = {
  initial: { opacity: 0, y: 10 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3 },
  },
};

// ============================================
// Progress Indicator
// ============================================

export const progressDotVariants: Variants = {
  initial: { scale: 1 },
  active: {
    scale: 1.2,
    transition: { type: 'spring', stiffness: 300 },
  },
  visited: { scale: 1 },
};

// ============================================
// Step Highlight Animations
// ============================================

export const highlightBorderVariants: Variants = {
  initial: { opacity: 0, pathLength: 0 },
  animate: {
    opacity: 1,
    pathLength: 1,
    transition: { duration: 0.8, ease: EASINGS.easeInOut },
  },
};

export const highlightGlowVariants: Variants = {
  initial: { opacity: 0 },
  animate: {
    opacity: [0.3, 0.6, 0.3],
    transition: { duration: 2, repeat: Infinity },
  },
};
