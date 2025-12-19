import type { Variants, Transition } from 'framer-motion';

// ============================================
// Animation Durations
// ============================================

export const ANIMATION_DURATIONS = {
  fast: 0.2,
  normal: 0.3,
  slow: 0.5,
  verySlow: 0.8,
  riskMeter: 1.5,
} as const;

// ============================================
// Easing Functions
// ============================================

export const EASINGS = {
  ease: [0.25, 0.1, 0.25, 1],
  easeIn: [0.42, 0, 1, 1],
  easeOut: [0, 0, 0.58, 1],
  easeInOut: [0.42, 0, 0.58, 1],
  spring: { type: 'spring', stiffness: 300, damping: 30 },
} as const;

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
// Screen Transitions
// ============================================

export const screenVariants: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: { duration: 0.3, ease: EASINGS.easeIn },
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
// Alert Banner Animations
// ============================================

export const alertBannerVariants: Variants = {
  initial: { opacity: 0, x: 100, scale: 0.9 },
  animate: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: { type: 'spring', stiffness: 400, damping: 30 },
  },
  exit: {
    opacity: 0,
    x: 100,
    transition: { duration: 0.2, ease: EASINGS.easeIn },
  },
};

// ============================================
// Participant Tile Animations
// ============================================

export const participantTileVariants: Variants = {
  initial: { opacity: 1, scale: 1 },
  animate: { opacity: 1, scale: 1 },
  exit: {
    opacity: 0,
    scale: 0.8,
    transition: { duration: 0.8, ease: EASINGS.easeIn },
  },
};

export const detectionOverlayVariants: Variants = {
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

// ============================================
// Risk Chip Animations
// ============================================

export const riskChipVariants: Variants = {
  initial: { opacity: 0, scale: 0.8, y: 10 },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 300, damping: 20 },
  },
  exit: {
    opacity: 0,
    scale: 0.8,
    transition: { duration: 0.15 },
  },
};

// ============================================
// Transcript Entry Animations
// ============================================

export const transcriptEntryVariants: Variants = {
  initial: { opacity: 0, x: 20 },
  animate: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3, ease: EASINGS.easeOut },
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: { duration: 0.2 },
  },
};

// ============================================
// Verification Step Animations
// ============================================

export const verificationStepVariants: Variants = {
  initial: { opacity: 0, x: -10 },
  animate: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3 },
  },
  complete: {
    opacity: 1,
    x: 0,
    color: '#3AD6A3', // success color
  },
};

// ============================================
// Threat Confirmed Overlay
// ============================================

export const threatConfirmedVariants: Variants = {
  initial: { opacity: 0, scale: 1.1 },
  animate: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.3 },
  },
  exit: {
    opacity: 0,
    transition: { duration: 0.5 },
  },
};

// ============================================
// Success Screen Animations
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
// Risk Meter Glow Animation (CSS Keyframes reference)
// ============================================

export const RISK_GLOW_KEYFRAMES = {
  critical: {
    boxShadow: [
      '0 0 20px rgba(214, 69, 69, 0.5)',
      '0 0 40px rgba(214, 69, 69, 0.7)',
      '0 0 20px rgba(214, 69, 69, 0.5)',
    ],
  },
  high: {
    boxShadow: [
      '0 0 15px rgba(255, 107, 107, 0.4)',
      '0 0 25px rgba(255, 107, 107, 0.6)',
      '0 0 15px rgba(255, 107, 107, 0.4)',
    ],
  },
};
