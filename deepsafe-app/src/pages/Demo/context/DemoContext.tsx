import React, { createContext, useContext, useReducer, useMemo } from 'react';
import type {
  DemoState,
  DemoAction,
  DemoContextValue,
  DemoStep,
  RiskLevel,
  HotspotConfig,
  DemoTranscriptEntry,
  DemoParticipant,
} from '../types/demo.types';
import { demoScenario, DEMO_TOTAL_STEPS } from '../data/demoScenario';
import { transcriptData } from '../data/transcriptData';
import { demoParticipants } from '../data/demoScenario';

// ============================================
// Initial State
// ============================================

const getInitialState = (): DemoState => ({
  // Navigation
  currentStep: 1,
  isPlaying: false,
  playbackSpeed: 'normal',

  // UI State
  activeModal: null,
  visitedHotspots: new Set<string>(),
  transcriptExpanded: true,

  // Demo Content State
  currentRiskScore: 0,
  visibleTranscriptCount: 0,
  activeAlerts: [],

  // Verification Flow
  verificationStep: null,
  threatConfirmed: false,
  participantRemoved: false,
});

// ============================================
// Helper Functions
// ============================================

export const getRiskLevel = (score: number): RiskLevel => {
  if (score >= 86) return 'critical';
  if (score >= 61) return 'high';
  if (score >= 31) return 'medium';
  return 'low';
};

// ============================================
// Reducer
// ============================================

const applyStepTransition = (state: DemoState, newStep: number): DemoState => {
  const stepConfig = demoScenario[newStep - 1];
  if (!stepConfig) return state;

  return {
    ...state,
    currentStep: newStep,
    currentRiskScore: stepConfig.riskScore,
    visibleTranscriptCount: stepConfig.transcriptUpTo,
    activeAlerts: stepConfig.alerts || [],
    verificationStep: stepConfig.showVerification ? 1 : null,
    threatConfirmed: stepConfig.showThreatConfirmed || false,
    participantRemoved: stepConfig.showRemovalAnimation || false,
  };
};

const demoReducer = (state: DemoState, action: DemoAction): DemoState => {
  switch (action.type) {
    case 'NEXT_STEP': {
      if (state.currentStep >= DEMO_TOTAL_STEPS) return state;
      return applyStepTransition(state, state.currentStep + 1);
    }

    case 'PREV_STEP': {
      if (state.currentStep <= 1) return state;
      return applyStepTransition(state, state.currentStep - 1);
    }

    case 'GO_TO_STEP': {
      if (action.step < 1 || action.step > DEMO_TOTAL_STEPS) return state;
      return applyStepTransition(state, action.step);
    }

    case 'TOGGLE_PLAY':
      return { ...state, isPlaying: !state.isPlaying };

    case 'SET_SPEED':
      return { ...state, playbackSpeed: action.speed };

    case 'OPEN_MODAL':
      return { ...state, activeModal: action.modal, isPlaying: false };

    case 'CLOSE_MODAL':
      return { ...state, activeModal: null };

    case 'MARK_HOTSPOT_VISITED':
      return {
        ...state,
        visitedHotspots: new Set([...state.visitedHotspots, action.hotspotId]),
      };

    case 'SET_RISK_SCORE':
      return { ...state, currentRiskScore: action.score };

    case 'ADD_ALERT':
      return { ...state, activeAlerts: [...state.activeAlerts, action.alert] };

    case 'CLEAR_ALERTS':
      return { ...state, activeAlerts: [] };

    case 'SET_VERIFICATION_STEP':
      return { ...state, verificationStep: action.step };

    case 'CONFIRM_THREAT':
      return { ...state, threatConfirmed: true };

    case 'REMOVE_PARTICIPANT':
      return { ...state, participantRemoved: true };

    case 'TOGGLE_TRANSCRIPT':
      return { ...state, transcriptExpanded: !state.transcriptExpanded };

    case 'RESET_DEMO':
      return getInitialState();

    default:
      return state;
  }
};

// ============================================
// Context
// ============================================

const DemoContext = createContext<DemoContextValue | null>(null);

// ============================================
// Provider
// ============================================

interface DemoProviderProps {
  children: React.ReactNode;
}

export const DemoProvider: React.FC<DemoProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(demoReducer, getInitialState());

  // Computed: Current step config
  const currentStepConfig = useMemo<DemoStep>(
    () => demoScenario[state.currentStep - 1] || demoScenario[0],
    [state.currentStep]
  );

  // Computed: Risk level
  const riskLevel = useMemo<RiskLevel>(
    () => getRiskLevel(state.currentRiskScore),
    [state.currentRiskScore]
  );

  // Computed: Navigation state
  const canGoBack = state.currentStep > 1;
  const canGoForward = state.currentStep < DEMO_TOTAL_STEPS;

  // Computed: Active hotspots for current step
  const activeHotspots = useMemo<HotspotConfig[]>(
    () => currentStepConfig.hotspots || [],
    [currentStepConfig]
  );

  // Computed: Progress percentage
  const progressPercentage = (state.currentStep / DEMO_TOTAL_STEPS) * 100;

  // Computed: Visible transcripts
  const visibleTranscripts = useMemo<DemoTranscriptEntry[]>(
    () => transcriptData.slice(0, state.visibleTranscriptCount),
    [state.visibleTranscriptCount]
  );

  // Computed: Participants with current state
  const participants = useMemo<DemoParticipant[]>(() => {
    return demoParticipants.map((p) => ({
      ...p,
      isSpeaking: currentStepConfig.activeSpeaker === p.id,
      showDetectionOverlay: p.isAttacker && state.currentRiskScore >= 61,
      showRemovalAnimation: p.isAttacker && state.participantRemoved,
    }));
  }, [currentStepConfig.activeSpeaker, state.currentRiskScore, state.participantRemoved]);

  // Context value
  const value: DemoContextValue = useMemo(
    () => ({
      state,
      dispatch,
      currentStepConfig,
      riskLevel,
      canGoBack,
      canGoForward,
      activeHotspots,
      progressPercentage,
      visibleTranscripts,
      participants,
    }),
    [
      state,
      currentStepConfig,
      riskLevel,
      canGoBack,
      canGoForward,
      activeHotspots,
      progressPercentage,
      visibleTranscripts,
      participants,
    ]
  );

  return <DemoContext.Provider value={value}>{children}</DemoContext.Provider>;
};

// ============================================
// Hook
// ============================================

export const useDemoContext = (): DemoContextValue => {
  const context = useContext(DemoContext);
  if (!context) {
    throw new Error('useDemoContext must be used within a DemoProvider');
  }
  return context;
};

// Re-export getRiskLevel for use in other components
export { getRiskLevel as calculateRiskLevel };
