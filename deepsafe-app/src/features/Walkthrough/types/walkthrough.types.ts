import type { ReactNode } from 'react';

// ============================================
// Walkthrough State Types
// ============================================

export type PlaybackSpeed = 'slow' | 'normal' | 'fast';
export type WalkthroughStepType = 'modal' | 'page' | 'navigation';
export type HotspotType = 'info' | 'data' | 'action';
export type SkipPreference = 'always_show' | 'never_show' | 'ask';

// ============================================
// Step Configuration
// ============================================

export interface WalkthroughHotspot {
  id: string;
  type: HotspotType;
  anchor: string; // CSS selector for data-walkthrough attribute
  offsetX?: number;
  offsetY?: number;
  position?: 'left' | 'right' | 'top' | 'bottom' | 'auto';
  tooltip: string;
  modalContent?: WalkthroughModalContent;
}

export interface WalkthroughModalContent {
  title: string;
  description: string;
  features?: string[];
  icon?: ReactNode;
}

export interface WalkthroughStep {
  id: number;
  name: string;
  phase: string; // Phase name for grouping
  type: WalkthroughStepType;
  route: string; // Route to navigate to
  duration: number; // seconds for auto-advance (0 = manual only)
  instruction?: string; // User instruction text
  focusElement?: string; // CSS selector for spotlight focus
  highlight?: 'full-page' | 'element' | 'none';
  hotspots: WalkthroughHotspot[];
  // Modal-specific content (for welcome/completion steps)
  modalContent?: {
    title: string;
    description: string;
    features?: string[];
    metrics?: { stepsCompleted: number; featuresExplored: number };
    nextSteps?: string[];
    helpLink?: string;
  };
  // Navigation-specific
  triggerElement?: string; // Element user should click to proceed
}

// ============================================
// Walkthrough State
// ============================================

export interface WalkthroughState {
  // Core state
  isActive: boolean;
  currentStep: number;
  visitedSteps: number[];
  visitedHotspots: Set<string>;

  // Playback
  isPlaying: boolean;
  playbackSpeed: PlaybackSpeed;

  // UI state
  activeModal: WalkthroughModalContent | null;
  showWelcome: boolean;
  showCompletion: boolean;

  // Persistence
  hasCompletedBefore: boolean;
  skipPreference: SkipPreference;
}

// ============================================
// Walkthrough Actions
// ============================================

export type WalkthroughAction =
  | { type: 'START_WALKTHROUGH' }
  | { type: 'SKIP_WALKTHROUGH' }
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' }
  | { type: 'GO_TO_STEP'; step: number }
  | { type: 'TOGGLE_PLAY' }
  | { type: 'SET_SPEED'; speed: PlaybackSpeed }
  | { type: 'OPEN_MODAL'; modal: WalkthroughModalContent }
  | { type: 'CLOSE_MODAL' }
  | { type: 'CLOSE_WELCOME' }
  | { type: 'SHOW_COMPLETION' }
  | { type: 'CLOSE_COMPLETION' }
  | { type: 'MARK_HOTSPOT_VISITED'; id: string }
  | { type: 'MARK_STEP_VISITED'; step: number }
  | { type: 'COMPLETE_WALKTHROUGH' }
  | { type: 'RESET_WALKTHROUGH' }
  | { type: 'SET_SKIP_PREFERENCE'; pref: SkipPreference }
  | { type: 'SET_ACTIVE'; isActive: boolean };

// ============================================
// Context Value
// ============================================

export interface WalkthroughContextValue {
  state: WalkthroughState;
  dispatch: React.Dispatch<WalkthroughAction>;
  // Derived state
  currentStepConfig: WalkthroughStep;
  canGoBack: boolean;
  canGoForward: boolean;
  activeHotspots: WalkthroughHotspot[];
  progressPercentage: number;
  totalSteps: number;
  // Actions
  startWalkthrough: () => void;
  skipWalkthrough: () => void;
  nextStep: () => void;
  prevStep: () => void;
  goToStep: (step: number) => void;
  exitWalkthrough: () => void;
}

// ============================================
// Constants
// ============================================

export const TOTAL_WALKTHROUGH_STEPS = 15;

export const SPEED_DURATIONS: Record<PlaybackSpeed, number> = {
  slow: 20000,    // 20 seconds per step
  normal: 12000,  // 12 seconds per step
  fast: 6000,     // 6 seconds per step
};

export const SPEED_MULTIPLIERS: Record<PlaybackSpeed, number> = {
  slow: 2,      // 0.5x = takes 2x longer
  normal: 1,    // 1x = normal speed
  fast: 0.5,    // 2x = takes half the time
};

// ============================================
// Storage Keys
// ============================================

export const STORAGE_KEYS = {
  completed: 'deepsafe-walkthrough-completed',
  progress: 'deepsafe-walkthrough-progress',
  preference: 'deepsafe-walkthrough-preference',
} as const;

export interface StoredProgress {
  step: number;
  visitedHotspots: string[];
  visitedSteps: number[];
}
