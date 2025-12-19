import React, { createContext, useContext, useReducer, useMemo, useCallback, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import type {
  WalkthroughState,
  WalkthroughAction,
  WalkthroughContextValue,
  WalkthroughStep,
  WalkthroughHotspot,
  SkipPreference,
} from '../types/walkthrough.types';
import { STORAGE_KEYS } from '../types/walkthrough.types';
import { walkthroughScenario, WALKTHROUGH_TOTAL_STEPS } from '../data/walkthroughScenario';

// ============================================
// Initial State
// ============================================

const getStoredPreference = (): SkipPreference => {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.preference);
    if (stored && ['always_show', 'never_show', 'ask'].includes(stored)) {
      return stored as SkipPreference;
    }
  } catch {
    // localStorage not available
  }
  return 'ask';
};

const getStoredCompleted = (): boolean => {
  try {
    return localStorage.getItem(STORAGE_KEYS.completed) === 'true';
  } catch {
    return false;
  }
};

const getInitialState = (): WalkthroughState => ({
  isActive: false,
  currentStep: 1,
  visitedSteps: [],
  visitedHotspots: new Set<string>(),
  isPlaying: false,
  playbackSpeed: 'normal',
  activeModal: null,
  showWelcome: false,
  showCompletion: false,
  hasCompletedBefore: getStoredCompleted(),
  skipPreference: getStoredPreference(),
});

// ============================================
// Reducer
// ============================================

const walkthroughReducer = (state: WalkthroughState, action: WalkthroughAction): WalkthroughState => {
  switch (action.type) {
    case 'START_WALKTHROUGH':
      return {
        ...state,
        isActive: true,
        currentStep: 1,
        showWelcome: true,
        showCompletion: false,
        visitedSteps: [1],
        visitedHotspots: new Set<string>(),
      };

    case 'SKIP_WALKTHROUGH':
      return {
        ...state,
        isActive: false,
        showWelcome: false,
        showCompletion: false,
      };

    case 'NEXT_STEP': {
      if (state.currentStep >= WALKTHROUGH_TOTAL_STEPS) {
        return {
          ...state,
          showCompletion: true,
        };
      }
      const nextStep = state.currentStep + 1;
      // Show completion screen when reaching the final step
      if (nextStep === WALKTHROUGH_TOTAL_STEPS) {
        return {
          ...state,
          currentStep: nextStep,
          visitedSteps: state.visitedSteps.includes(nextStep)
            ? state.visitedSteps
            : [...state.visitedSteps, nextStep],
          showCompletion: true,
          activeModal: null,
        };
      }
      return {
        ...state,
        currentStep: nextStep,
        visitedSteps: state.visitedSteps.includes(nextStep)
          ? state.visitedSteps
          : [...state.visitedSteps, nextStep],
        activeModal: null,
      };
    }

    case 'PREV_STEP': {
      if (state.currentStep <= 1) return state;
      return {
        ...state,
        currentStep: state.currentStep - 1,
        activeModal: null,
      };
    }

    case 'GO_TO_STEP': {
      if (action.step < 1 || action.step > WALKTHROUGH_TOTAL_STEPS) return state;
      return {
        ...state,
        currentStep: action.step,
        visitedSteps: state.visitedSteps.includes(action.step)
          ? state.visitedSteps
          : [...state.visitedSteps, action.step],
        activeModal: null,
      };
    }

    case 'TOGGLE_PLAY':
      return { ...state, isPlaying: !state.isPlaying };

    case 'SET_SPEED':
      return { ...state, playbackSpeed: action.speed };

    case 'OPEN_MODAL':
      return { ...state, activeModal: action.modal, isPlaying: false };

    case 'CLOSE_MODAL':
      return { ...state, activeModal: null };

    case 'CLOSE_WELCOME':
      return { ...state, showWelcome: false };

    case 'SHOW_COMPLETION':
      return { ...state, showCompletion: true, isPlaying: false };

    case 'CLOSE_COMPLETION':
      return { ...state, showCompletion: false };

    case 'MARK_HOTSPOT_VISITED':
      return {
        ...state,
        visitedHotspots: new Set([...state.visitedHotspots, action.id]),
      };

    case 'MARK_STEP_VISITED':
      return {
        ...state,
        visitedSteps: state.visitedSteps.includes(action.step)
          ? state.visitedSteps
          : [...state.visitedSteps, action.step],
      };

    case 'COMPLETE_WALKTHROUGH':
      try {
        localStorage.setItem(STORAGE_KEYS.completed, 'true');
      } catch {
        // localStorage not available
      }
      return {
        ...state,
        isActive: false,
        showCompletion: false,
        hasCompletedBefore: true,
      };

    case 'RESET_WALKTHROUGH':
      return {
        ...getInitialState(),
        isActive: true,
        showWelcome: true,
        visitedSteps: [1],
      };

    case 'SET_SKIP_PREFERENCE':
      try {
        localStorage.setItem(STORAGE_KEYS.preference, action.pref);
      } catch {
        // localStorage not available
      }
      return { ...state, skipPreference: action.pref };

    case 'SET_ACTIVE':
      return { ...state, isActive: action.isActive };

    default:
      return state;
  }
};

// ============================================
// Context
// ============================================

const WalkthroughContext = createContext<WalkthroughContextValue | null>(null);

// ============================================
// Provider
// ============================================

interface WalkthroughProviderProps {
  children: React.ReactNode;
}

export const WalkthroughProvider: React.FC<WalkthroughProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(walkthroughReducer, getInitialState());
  const navigate = useNavigate();
  const location = useLocation();

  // Computed: Current step config
  const currentStepConfig = useMemo<WalkthroughStep>(
    () => walkthroughScenario[state.currentStep - 1] || walkthroughScenario[0],
    [state.currentStep]
  );

  // Computed: Navigation state
  const canGoBack = state.currentStep > 1;
  const canGoForward = state.currentStep < WALKTHROUGH_TOTAL_STEPS;

  // Computed: Active hotspots for current step
  const activeHotspots = useMemo<WalkthroughHotspot[]>(
    () => currentStepConfig.hotspots || [],
    [currentStepConfig]
  );

  // Computed: Progress percentage
  const progressPercentage = (state.currentStep / WALKTHROUGH_TOTAL_STEPS) * 100;

  // Navigate to step route when step changes
  useEffect(() => {
    if (state.isActive && currentStepConfig.route && location.pathname !== currentStepConfig.route) {
      // Skip navigation for steps with dynamic routes (contains :)
      if (currentStepConfig.route.includes(':')) {
        return;
      }

      // For meeting detail step (8), allow any meeting detail page
      if (state.currentStep === 8 && location.pathname.match(/^\/app\/meetings\/[^/]+$/)) {
        return;
      }

      // For participant profile step (11), allow any participant profile page
      if (state.currentStep === 11 && location.pathname.match(/^\/app\/participants\/[^/]+$/)) {
        return;
      }

      // Navigate to the step's route
      navigate(currentStepConfig.route);
    }
  }, [state.isActive, state.currentStep, currentStepConfig.route, location.pathname, navigate]);

  // Auto-advance when user navigates to detail pages during relevant steps
  useEffect(() => {
    if (!state.isActive || state.showWelcome || state.showCompletion) return;

    const pathname = location.pathname;

    // Step 7 (Meetings list) -> Step 8 (Meeting detail): User clicked a meeting row
    if (state.currentStep === 7 && pathname.match(/^\/app\/meetings\/[^/]+$/)) {
      dispatch({ type: 'GO_TO_STEP', step: 8 });
      return;
    }

    // Step 10 (Participants list) -> Step 11 (Participant profile): User clicked a participant row
    if (state.currentStep === 10 && pathname.match(/^\/app\/participants\/[^/]+$/)) {
      dispatch({ type: 'GO_TO_STEP', step: 11 });
      return;
    }
  }, [state.isActive, state.currentStep, state.showWelcome, state.showCompletion, location.pathname]);

  // Scroll to focus element when step changes
  useEffect(() => {
    if (!state.isActive || state.showWelcome || state.showCompletion) return;

    const focusElement = currentStepConfig.focusElement;
    if (!focusElement) return;

    // Wait for the page to render
    const timer = setTimeout(() => {
      const element = document.querySelector(focusElement);
      if (element) {
        element.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        });
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [state.isActive, state.currentStep, state.showWelcome, state.showCompletion, currentStepConfig.focusElement]);

  // Action helpers
  const startWalkthrough = useCallback(() => {
    dispatch({ type: 'START_WALKTHROUGH' });
  }, []);

  const skipWalkthrough = useCallback(() => {
    dispatch({ type: 'SKIP_WALKTHROUGH' });
  }, []);

  const nextStep = useCallback(() => {
    dispatch({ type: 'NEXT_STEP' });
  }, []);

  const prevStep = useCallback(() => {
    dispatch({ type: 'PREV_STEP' });
  }, []);

  const goToStep = useCallback((step: number) => {
    dispatch({ type: 'GO_TO_STEP', step });
  }, []);

  const exitWalkthrough = useCallback(() => {
    dispatch({ type: 'COMPLETE_WALKTHROUGH' });
  }, []);

  // Context value
  const value: WalkthroughContextValue = useMemo(
    () => ({
      state,
      dispatch,
      currentStepConfig,
      canGoBack,
      canGoForward,
      activeHotspots,
      progressPercentage,
      totalSteps: WALKTHROUGH_TOTAL_STEPS,
      startWalkthrough,
      skipWalkthrough,
      nextStep,
      prevStep,
      goToStep,
      exitWalkthrough,
    }),
    [
      state,
      currentStepConfig,
      canGoBack,
      canGoForward,
      activeHotspots,
      progressPercentage,
      startWalkthrough,
      skipWalkthrough,
      nextStep,
      prevStep,
      goToStep,
      exitWalkthrough,
    ]
  );

  return (
    <WalkthroughContext.Provider value={value}>
      {children}
    </WalkthroughContext.Provider>
  );
};

// ============================================
// Hook
// ============================================

export const useWalkthroughContext = (): WalkthroughContextValue => {
  const context = useContext(WalkthroughContext);
  if (!context) {
    throw new Error('useWalkthroughContext must be used within a WalkthroughProvider');
  }
  return context;
};

// Export for convenience
export { WalkthroughContext };
