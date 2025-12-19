# DeepSafe Interactive Demo Application
## Technical Design Document (TDD)

**Version:** 1.0
**Date:** December 2024
**Author:** DeepSafe Engineering Team
**Status:** Draft

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Component Design](#3-component-design)
4. [State Management](#4-state-management)
5. [Data Flow](#5-data-flow)
6. [Hooks & Custom Logic](#6-hooks--custom-logic)
7. [Routing & Navigation](#7-routing--navigation)
8. [Animation System](#8-animation-system)
9. [Modal System](#9-modal-system)
10. [Hotspot System](#10-hotspot-system)
11. [Accessibility Implementation](#11-accessibility-implementation)
12. [Performance Optimization](#12-performance-optimization)
13. [Testing Strategy](#13-testing-strategy)
14. [Build Configuration](#14-build-configuration)
15. [File Structure](#15-file-structure)
16. [Implementation Plan](#16-implementation-plan)

---

## 1. Overview

### 1.1 Purpose

This document provides the technical architecture and implementation details for the DeepSafe Interactive Demo application. It covers component design, state management, data flow, and engineering decisions.

### 1.2 Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Framework** | React | 18.x |
| **Language** | TypeScript | 5.x |
| **Build Tool** | Vite | 5.x |
| **UI Library** | Material-UI (MUI) | 5.x |
| **State** | React Context + useReducer | - |
| **Animation** | Framer Motion | 10.x |
| **Styling** | Emotion (via MUI) | 11.x |
| **Icons** | MUI Icons + Custom SVG | - |

### 1.3 Design Principles

1. **Component Isolation** - Each component is self-contained with clear props interface
2. **Declarative State** - Demo state drives all UI through a single source of truth
3. **Performance First** - Lazy loading, memoization, and optimized re-renders
4. **Accessibility Native** - ARIA built into components from the start
5. **Type Safety** - Full TypeScript coverage with strict mode

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              APP SHELL                                   │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        DEMO PROVIDER                               │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │                      DEMO PAGE                               │  │  │
│  │  │                                                              │  │  │
│  │  │  ┌──────────────────────────────────────────────────────┐   │  │  │
│  │  │  │               SCREEN RENDERER                         │   │  │  │
│  │  │  │  ┌────────────┐ ┌────────────┐ ┌────────────────┐   │   │  │  │
│  │  │  │  │  Welcome   │ │   Lobby    │ │  VideoCall     │   │   │  │  │
│  │  │  │  │  Screen    │ │   Screen   │ │  Interface     │   │   │  │  │
│  │  │  │  └────────────┘ └────────────┘ └────────────────┘   │   │  │  │
│  │  │  │  ┌────────────┐ ┌────────────┐                      │   │  │  │
│  │  │  │  │  Report    │ │  Success   │                      │   │  │  │
│  │  │  │  │  Screen    │ │  Screen    │                      │   │  │  │
│  │  │  │  └────────────┘ └────────────┘                      │   │  │  │
│  │  │  └──────────────────────────────────────────────────────┘   │  │  │
│  │  │                                                              │  │  │
│  │  │  ┌──────────────────────────────────────────────────────┐   │  │  │
│  │  │  │            NAVIGATION BAR                             │   │  │  │
│  │  │  │  [◀ Back]  Step 5/9  [▶ Next]  ●●●●●○○○○  [▶ Play]  │   │  │  │
│  │  │  └──────────────────────────────────────────────────────┘   │  │  │
│  │  │                                                              │  │  │
│  │  │  ┌──────────────────────────────────────────────────────┐   │  │  │
│  │  │  │            MODAL LAYER (Portal)                       │   │  │  │
│  │  │  └──────────────────────────────────────────────────────┘   │  │  │
│  │  │                                                              │  │  │
│  │  │  ┌──────────────────────────────────────────────────────┐   │  │  │
│  │  │  │            HOTSPOT MANAGER                            │   │  │  │
│  │  │  └──────────────────────────────────────────────────────┘   │  │  │
│  │  │                                                              │  │  │
│  │  └─────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Hierarchy

```
DemoProvider (Context)
└── DemoPage
    ├── ScreenRenderer
    │   ├── WelcomeScreen
    │   ├── LobbyScreen
    │   ├── VideoCallInterface
    │   │   ├── MeetingHeader
    │   │   ├── ParticipantGrid
    │   │   │   └── ParticipantTile (x2-3)
    │   │   │       ├── VideoFeed
    │   │   │       ├── TrustBadge
    │   │   │       └── DetectionOverlay
    │   │   ├── TranscriptPanel
    │   │   │   └── TranscriptEntry (xN)
    │   │   │       └── RiskChips
    │   │   ├── DeepSafeOverlay
    │   │   │   ├── RiskMeter
    │   │   │   ├── AlertBanner
    │   │   │   └── VerificationModal
    │   │   └── ControlBar
    │   ├── IncidentReportScreen
    │   └── SuccessScreen
    ├── StepNavigation
    │   ├── NavButton (Back)
    │   ├── ProgressIndicator
    │   ├── NavButton (Next)
    │   └── AutoPlayControls
    ├── HotspotManager
    │   └── Hotspot (xN)
    │       └── HotspotTooltip
    └── ModalPortal
        └── DemoModal
            ├── ExplainerModal
            ├── RiskBreakdownModal
            ├── ForensicModal
            └── TimelineModal
```

### 2.3 Data Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STATIC DATA                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │ demoScenario.ts │  │ transcriptData  │  │ forensicData.ts     │ │
│  │                 │  │ .ts             │  │                     │ │
│  │ - 9 step defs   │  │ - 10 entries    │  │ - video analysis    │ │
│  │ - participant   │  │ - risk scores   │  │ - audio analysis    │ │
│  │   configs       │  │ - indicators    │  │ - network analysis  │ │
│  │ - timing        │  │ - flags         │  │ - behavioral        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    hotspotContent.ts                         │   │
│  │  - 25+ hotspot definitions with modal content                │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DEMO CONTEXT                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                       DemoState                              │   │
│  │  {                                                           │   │
│  │    currentStep: number,                                      │   │
│  │    isPlaying: boolean,                                       │   │
│  │    playbackSpeed: 'slow' | 'normal' | 'fast',               │   │
│  │    activeModal: ModalConfig | null,                          │   │
│  │    visitedHotspots: Set<string>,                            │   │
│  │    currentRiskScore: number,                                 │   │
│  │    visibleTranscripts: TranscriptEntry[],                   │   │
│  │    activeAlerts: Alert[],                                    │   │
│  │    participantStates: Map<string, ParticipantState>,        │   │
│  │  }                                                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DERIVED / COMPUTED STATE                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  - currentStepConfig (from demoScenario[currentStep])       │   │
│  │  - riskLevel (computed from currentRiskScore)               │   │
│  │  - canGoBack / canGoForward                                  │   │
│  │  - activeHotspots (filtered by current step)                │   │
│  │  - progressPercentage                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Design

### 3.1 Core Components

#### 3.1.1 DemoPage

**Purpose:** Main container that orchestrates the demo experience.

```typescript
// src/pages/Demo/DemoPage.tsx

interface DemoPageProps {
  standalone?: boolean;  // Enables standalone mode (no app chrome)
}

const DemoPage: React.FC<DemoPageProps> = ({ standalone = false }) => {
  const { state, dispatch } = useDemoContext();

  // Keyboard navigation
  useKeyboardNavigation({
    onNext: () => dispatch({ type: 'NEXT_STEP' }),
    onPrev: () => dispatch({ type: 'PREV_STEP' }),
    onTogglePlay: () => dispatch({ type: 'TOGGLE_PLAY' }),
    onCloseModal: () => dispatch({ type: 'CLOSE_MODAL' }),
  });

  // Auto-play logic
  useAutoPlay(state.isPlaying, state.playbackSpeed, state.currentStep);

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <ScreenRenderer step={state.currentStep} />
      <StepNavigation />
      <HotspotManager />
      <ModalPortal />
    </Box>
  );
};
```

#### 3.1.2 VideoCallInterface

**Purpose:** Google Meet-style video call mockup with DeepSafe overlays.

```typescript
// src/pages/Demo/components/VideoCallInterface/VideoCallInterface.tsx

interface VideoCallInterfaceProps {
  participants: DemoParticipant[];
  activeSpeaker: string | null;
  riskScore: number;
  alerts: Alert[];
  transcripts: TranscriptEntry[];
  showVerification?: boolean;
  showThreatConfirmed?: boolean;
}

const VideoCallInterface: React.FC<VideoCallInterfaceProps> = ({
  participants,
  activeSpeaker,
  riskScore,
  alerts,
  transcripts,
  showVerification,
  showThreatConfirmed,
}) => {
  const [transcriptExpanded, setTranscriptExpanded] = useState(true);

  return (
    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>
      {/* Meeting Header */}
      <MeetingHeader title="Urgent: Acquisition Discussion" />

      {/* Main Content Area */}
      <Box sx={{ flex: 1, display: 'flex' }}>
        {/* Participant Grid */}
        <ParticipantGrid
          participants={participants}
          activeSpeaker={activeSpeaker}
          sx={{ flex: 1 }}
        />

        {/* Transcript Panel (collapsible) */}
        <AnimatePresence>
          {transcriptExpanded && (
            <TranscriptPanel
              entries={transcripts}
              onCollapse={() => setTranscriptExpanded(false)}
            />
          )}
        </AnimatePresence>
      </Box>

      {/* DeepSafe Overlay */}
      <DeepSafeOverlay
        riskScore={riskScore}
        alerts={alerts}
      />

      {/* Control Bar */}
      <ControlBar
        onTranscriptToggle={() => setTranscriptExpanded(!transcriptExpanded)}
      />

      {/* Verification Modal */}
      <AnimatePresence>
        {showVerification && <VerificationModal />}
      </AnimatePresence>

      {/* Threat Confirmed Overlay */}
      <AnimatePresence>
        {showThreatConfirmed && <ThreatConfirmedOverlay />}
      </AnimatePresence>
    </Box>
  );
};
```

#### 3.1.3 ParticipantTile

**Purpose:** Individual participant video tile with trust badge and detection overlay.

```typescript
// src/pages/Demo/components/VideoCallInterface/ParticipantTile.tsx

interface ParticipantTileProps {
  participant: DemoParticipant;
  isActive: boolean;
  size: 'large' | 'small';
  showDetectionOverlay?: boolean;
  showRemovalAnimation?: boolean;
}

const ParticipantTile: React.FC<ParticipantTileProps> = ({
  participant,
  isActive,
  size,
  showDetectionOverlay,
  showRemovalAnimation,
}) => {
  const { isDark } = useThemeMode();

  return (
    <motion.div
      layout
      initial={{ opacity: 1 }}
      animate={{
        opacity: showRemovalAnimation ? 0 : 1,
        scale: showRemovalAnimation ? 0.8 : 1,
      }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.5 }}
    >
      <Card
        sx={{
          position: 'relative',
          borderRadius: 2,
          overflow: 'hidden',
          border: isActive ? `2px solid ${brandColors.primary.signalTeal}` : 'none',
        }}
      >
        {/* Video/Avatar */}
        <Box
          component="img"
          src={participant.avatar}
          sx={{
            width: '100%',
            height: size === 'large' ? 400 : 180,
            objectFit: 'cover',
          }}
        />

        {/* Name & Role Overlay */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            p: 1.5,
            background: 'linear-gradient(transparent, rgba(0,0,0,0.8))',
          }}
        >
          <Typography variant="subtitle1" color="white">
            {participant.name}
          </Typography>
          <Typography variant="caption" color="grey.400">
            {participant.role}
          </Typography>
        </Box>

        {/* Trust Badge */}
        <TrustBadge
          score={participant.trustScore}
          sx={{ position: 'absolute', top: 8, right: 8 }}
        />

        {/* Speaking Indicator */}
        {isActive && (
          <SpeakingIndicator sx={{ position: 'absolute', bottom: 60, left: 8 }} />
        )}

        {/* Detection Overlay */}
        <AnimatePresence>
          {showDetectionOverlay && (
            <DetectionOverlay participant={participant} />
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
};
```

#### 3.1.4 RiskMeter

**Purpose:** Animated risk score display with color-coded levels.

```typescript
// src/pages/Demo/components/DeepSafeOverlay/RiskMeter.tsx

interface RiskMeterProps {
  score: number;
  animated?: boolean;
  showLabel?: boolean;
  compact?: boolean;
}

const RiskMeter: React.FC<RiskMeterProps> = ({
  score,
  animated = true,
  showLabel = true,
  compact = false,
}) => {
  const { isDark } = useThemeMode();
  const prevScore = useRef(score);
  const [displayScore, setDisplayScore] = useState(score);

  // Animate score changes
  useEffect(() => {
    if (!animated) {
      setDisplayScore(score);
      return;
    }

    const duration = 1500;
    const startTime = Date.now();
    const startScore = prevScore.current;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutCubic(progress);
      const current = Math.round(startScore + (score - startScore) * eased);

      setDisplayScore(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
    prevScore.current = score;
  }, [score, animated]);

  const riskLevel = getRiskLevel(displayScore);
  const gradient = getRiskGradient(riskLevel);

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: compact ? 1 : 2,
        p: compact ? 1 : 2,
        borderRadius: 2,
        background: isDark ? 'rgba(0,0,0,0.6)' : 'rgba(255,255,255,0.9)',
        backdropFilter: 'blur(8px)',
        boxShadow: riskLevel === 'critical'
          ? `0 0 20px ${brandColors.primary.threatRed}80`
          : undefined,
      }}
    >
      {/* Progress Bar */}
      <Box sx={{ flex: 1, minWidth: compact ? 80 : 120 }}>
        <LinearProgress
          variant="determinate"
          value={displayScore}
          sx={{
            height: compact ? 6 : 10,
            borderRadius: 5,
            backgroundColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
            '& .MuiLinearProgress-bar': {
              background: gradient,
              borderRadius: 5,
            },
          }}
        />
      </Box>

      {/* Score Display */}
      <Typography
        variant={compact ? 'body2' : 'h6'}
        sx={{
          fontFamily: '"JetBrains Mono", monospace',
          fontWeight: 700,
          background: gradient,
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          minWidth: 50,
          textAlign: 'right',
        }}
      >
        {displayScore}%
      </Typography>

      {/* Risk Label */}
      {showLabel && (
        <Chip
          label={riskLevel.toUpperCase()}
          size="small"
          sx={{
            background: gradient,
            color: 'white',
            fontWeight: 600,
          }}
        />
      )}
    </Box>
  );
};

// Helper functions
const getRiskLevel = (score: number): RiskLevel => {
  if (score >= 86) return 'critical';
  if (score >= 61) return 'high';
  if (score >= 31) return 'medium';
  return 'low';
};

const getRiskGradient = (level: RiskLevel): string => {
  const gradients: Record<RiskLevel, string> = {
    low: 'linear-gradient(135deg, #2DBE8B, #3AD6A3)',
    medium: 'linear-gradient(135deg, #F5A623, #FFC857)',
    high: 'linear-gradient(135deg, #FF6B6B, #F5A623)',
    critical: 'linear-gradient(135deg, #D64545, #FF6B6B)',
  };
  return gradients[level];
};
```

#### 3.1.5 TranscriptEntry

**Purpose:** Individual transcript line with risk indicators.

```typescript
// src/pages/Demo/components/TranscriptPanel/TranscriptEntry.tsx

interface TranscriptEntryProps {
  entry: TranscriptEntryData;
  isHighlighted?: boolean;
  onRiskClick?: () => void;
}

const TranscriptEntry: React.FC<TranscriptEntryProps> = ({
  entry,
  isHighlighted,
  onRiskClick,
}) => {
  const { isDark } = useThemeMode();
  const riskLevel = getRiskLevel(entry.riskScore);

  const backgroundColor = isHighlighted
    ? isDark
      ? 'rgba(214, 69, 69, 0.15)'
      : 'rgba(214, 69, 69, 0.08)'
    : 'transparent';

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Box
        sx={{
          p: 1.5,
          borderRadius: 1,
          backgroundColor,
          borderLeft: entry.isFlagged
            ? `3px solid ${brandColors.primary.threatRed}`
            : 'none',
          mb: 1,
        }}
      >
        {/* Header: Speaker & Time */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography
            variant="caption"
            sx={{ fontWeight: 600, color: entry.isFlagged ? brandColors.primary.threatRed : 'text.primary' }}
          >
            {entry.speaker}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {formatTimestamp(entry.timestamp)}
          </Typography>
        </Box>

        {/* Message Text */}
        <Typography variant="body2" sx={{ mb: entry.isFlagged ? 1 : 0 }}>
          "{entry.text}"
        </Typography>

        {/* Risk Indicators (for flagged entries) */}
        {entry.isFlagged && entry.riskIndicators && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
            {entry.riskIndicators.map((indicator, idx) => (
              <RiskChip
                key={idx}
                label={indicator}
                onClick={onRiskClick}
              />
            ))}
          </Box>
        )}

        {/* Risk Score Bar (mini) */}
        {entry.riskScore > 20 && (
          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Risk:
            </Typography>
            <LinearProgress
              variant="determinate"
              value={entry.riskScore}
              sx={{
                flex: 1,
                height: 4,
                borderRadius: 2,
                '& .MuiLinearProgress-bar': {
                  background: getRiskGradient(riskLevel),
                },
              }}
            />
            <Typography
              variant="caption"
              sx={{ fontFamily: '"JetBrains Mono", monospace' }}
            >
              {entry.riskScore}%
            </Typography>
          </Box>
        )}
      </Box>
    </motion.div>
  );
};
```

---

## 4. State Management

### 4.1 Demo Context

```typescript
// src/pages/Demo/context/DemoContext.tsx

interface DemoState {
  // Navigation
  currentStep: number;
  isPlaying: boolean;
  playbackSpeed: PlaybackSpeed;

  // UI State
  activeModal: ModalConfig | null;
  visitedHotspots: Set<string>;
  transcriptExpanded: boolean;

  // Demo Content State
  currentRiskScore: number;
  visibleTranscriptCount: number;
  activeAlerts: Alert[];
  participantStates: Record<string, ParticipantDisplayState>;

  // Verification Flow
  verificationStep: number | null;
  threatConfirmed: boolean;
  participantRemoved: boolean;
}

type DemoAction =
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' }
  | { type: 'GO_TO_STEP'; step: number }
  | { type: 'TOGGLE_PLAY' }
  | { type: 'SET_SPEED'; speed: PlaybackSpeed }
  | { type: 'OPEN_MODAL'; modal: ModalConfig }
  | { type: 'CLOSE_MODAL' }
  | { type: 'MARK_HOTSPOT_VISITED'; hotspotId: string }
  | { type: 'SET_RISK_SCORE'; score: number }
  | { type: 'ADD_ALERT'; alert: Alert }
  | { type: 'CLEAR_ALERTS' }
  | { type: 'SET_VERIFICATION_STEP'; step: number }
  | { type: 'CONFIRM_THREAT' }
  | { type: 'REMOVE_PARTICIPANT'; participantId: string }
  | { type: 'TOGGLE_TRANSCRIPT' }
  | { type: 'RESET_DEMO' };

const demoReducer = (state: DemoState, action: DemoAction): DemoState => {
  switch (action.type) {
    case 'NEXT_STEP':
      if (state.currentStep >= TOTAL_STEPS) return state;
      return applyStepTransition(state, state.currentStep + 1);

    case 'PREV_STEP':
      if (state.currentStep <= 1) return state;
      return applyStepTransition(state, state.currentStep - 1);

    case 'GO_TO_STEP':
      if (action.step < 1 || action.step > TOTAL_STEPS) return state;
      return applyStepTransition(state, action.step);

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
      return {
        ...state,
        participantRemoved: true,
        participantStates: {
          ...state.participantStates,
          [action.participantId]: { ...state.participantStates[action.participantId], removed: true },
        },
      };

    case 'TOGGLE_TRANSCRIPT':
      return { ...state, transcriptExpanded: !state.transcriptExpanded };

    case 'RESET_DEMO':
      return getInitialState();

    default:
      return state;
  }
};

// Apply step-specific state changes
const applyStepTransition = (state: DemoState, newStep: number): DemoState => {
  const stepConfig = demoScenario[newStep - 1];

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
```

### 4.2 Context Provider

```typescript
// src/pages/Demo/context/DemoProvider.tsx

interface DemoContextValue {
  state: DemoState;
  dispatch: React.Dispatch<DemoAction>;
  // Derived state
  currentStepConfig: DemoStepConfig;
  riskLevel: RiskLevel;
  canGoBack: boolean;
  canGoForward: boolean;
  activeHotspots: Hotspot[];
  progressPercentage: number;
}

const DemoContext = createContext<DemoContextValue | null>(null);

export const DemoProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(demoReducer, getInitialState());

  // Computed values
  const currentStepConfig = useMemo(
    () => demoScenario[state.currentStep - 1],
    [state.currentStep]
  );

  const riskLevel = useMemo(
    () => getRiskLevel(state.currentRiskScore),
    [state.currentRiskScore]
  );

  const canGoBack = state.currentStep > 1;
  const canGoForward = state.currentStep < TOTAL_STEPS;

  const activeHotspots = useMemo(
    () => currentStepConfig.hotspots || [],
    [currentStepConfig]
  );

  const progressPercentage = (state.currentStep / TOTAL_STEPS) * 100;

  const value: DemoContextValue = {
    state,
    dispatch,
    currentStepConfig,
    riskLevel,
    canGoBack,
    canGoForward,
    activeHotspots,
    progressPercentage,
  };

  return <DemoContext.Provider value={value}>{children}</DemoContext.Provider>;
};

export const useDemoContext = () => {
  const context = useContext(DemoContext);
  if (!context) {
    throw new Error('useDemoContext must be used within DemoProvider');
  }
  return context;
};
```

---

## 5. Data Flow

### 5.1 Step Transition Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      STEP TRANSITION FLOW                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   User Action                                                        │
│       │                                                              │
│       ▼                                                              │
│   ┌──────────────┐                                                  │
│   │   dispatch   │ ◄── { type: 'NEXT_STEP' }                        │
│   └──────┬───────┘                                                  │
│          │                                                          │
│          ▼                                                          │
│   ┌──────────────────────────────────────────────────┐              │
│   │              demoReducer                          │              │
│   │  1. Validate step bounds                         │              │
│   │  2. Get new step config from demoScenario        │              │
│   │  3. Apply step-specific state:                   │              │
│   │     - riskScore                                  │              │
│   │     - visibleTranscriptCount                     │              │
│   │     - activeAlerts                               │              │
│   │     - verificationStep                           │              │
│   │     - threatConfirmed                            │              │
│   │     - participantRemoved                         │              │
│   └──────────────────┬───────────────────────────────┘              │
│                      │                                              │
│                      ▼                                              │
│   ┌──────────────────────────────────────────────────┐              │
│   │              New State                            │              │
│   └──────────────────┬───────────────────────────────┘              │
│                      │                                              │
│          ┌───────────┼───────────┬───────────┐                      │
│          ▼           ▼           ▼           ▼                      │
│   ┌────────────┐┌──────────┐┌────────────┐┌────────────┐           │
│   │ RiskMeter  ││Transcript││AlertBanner ││Participant │           │
│   │ animates   ││ updates  ││ appears    ││Tile updates│           │
│   │ to new     ││ entries  ││            ││            │           │
│   │ score      ││          ││            ││            │           │
│   └────────────┘└──────────┘└────────────┘└────────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Modal Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MODAL FLOW                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Hotspot Click                                                      │
│       │                                                              │
│       ▼                                                              │
│   ┌──────────────────────────────┐                                  │
│   │  dispatch({                  │                                  │
│   │    type: 'OPEN_MODAL',       │                                  │
│   │    modal: {                  │                                  │
│   │      type: 'explainer',      │                                  │
│   │      title: '...',           │                                  │
│   │      content: <Component/>,  │                                  │
│   │      size: 'md'              │                                  │
│   │    }                         │                                  │
│   │  })                          │                                  │
│   └──────────────┬───────────────┘                                  │
│                  │                                                  │
│                  ▼                                                  │
│   ┌──────────────────────────────────────────────────┐              │
│   │  State Update:                                    │              │
│   │  - activeModal = modalConfig                      │              │
│   │  - isPlaying = false (pause auto-play)           │              │
│   └──────────────────┬───────────────────────────────┘              │
│                      │                                              │
│                      ▼                                              │
│   ┌──────────────────────────────────────────────────┐              │
│   │  ModalPortal renders:                             │              │
│   │  - Backdrop with blur                             │              │
│   │  - DemoModal with content                         │              │
│   │  - Close button                                   │              │
│   └──────────────────────────────────────────────────┘              │
│                                                                      │
│   Close Action (click X, click backdrop, press Esc)                 │
│       │                                                              │
│       ▼                                                              │
│   dispatch({ type: 'CLOSE_MODAL' })                                 │
│       │                                                              │
│       ▼                                                              │
│   activeModal = null                                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Hooks & Custom Logic

### 6.1 useAutoPlay

```typescript
// src/pages/Demo/hooks/useAutoPlay.ts

const SPEED_DURATIONS: Record<PlaybackSpeed, number> = {
  slow: 20000,    // 20 seconds per step
  normal: 12000,  // 12 seconds per step
  fast: 6000,     // 6 seconds per step
};

export const useAutoPlay = (
  isPlaying: boolean,
  speed: PlaybackSpeed,
  currentStep: number
) => {
  const { dispatch } = useDemoContext();
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Clear existing timer
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }

    // Don't start timer if not playing or at last step
    if (!isPlaying || currentStep >= TOTAL_STEPS) {
      return;
    }

    // Start new timer
    const duration = SPEED_DURATIONS[speed];
    timerRef.current = setTimeout(() => {
      dispatch({ type: 'NEXT_STEP' });
    }, duration);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [isPlaying, speed, currentStep, dispatch]);
};
```

### 6.2 useKeyboardNavigation

```typescript
// src/pages/Demo/hooks/useKeyboardNavigation.ts

interface KeyboardNavigationOptions {
  onNext: () => void;
  onPrev: () => void;
  onTogglePlay: () => void;
  onCloseModal: () => void;
}

export const useKeyboardNavigation = (options: KeyboardNavigationOptions) => {
  const { onNext, onPrev, onTogglePlay, onCloseModal } = options;

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore if user is typing in an input
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      switch (event.key) {
        case 'ArrowRight':
          event.preventDefault();
          onNext();
          break;
        case 'ArrowLeft':
          event.preventDefault();
          onPrev();
          break;
        case ' ':
          event.preventDefault();
          onTogglePlay();
          break;
        case 'Escape':
          event.preventDefault();
          onCloseModal();
          break;
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
          event.preventDefault();
          // Jump to step (handled separately)
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onNext, onPrev, onTogglePlay, onCloseModal]);
};
```

### 6.3 useRiskAnimation

```typescript
// src/pages/Demo/hooks/useRiskAnimation.ts

export const useRiskAnimation = (targetScore: number, duration = 1500) => {
  const [displayScore, setDisplayScore] = useState(targetScore);
  const prevScore = useRef(targetScore);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
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
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [targetScore, duration]);

  return displayScore;
};

const easeOutCubic = (x: number): number => {
  return 1 - Math.pow(1 - x, 3);
};
```

### 6.4 useLocalStorage (Persistence)

```typescript
// src/pages/Demo/hooks/useLocalStorage.ts

interface DemoPreferences {
  playbackSpeed: PlaybackSpeed;
  hintsEnabled: boolean;
  visitedHotspots: string[];
  lastStep: number;
}

const STORAGE_KEY = 'deepsafe-demo-prefs';

export const useDemoPreferences = () => {
  const [preferences, setPreferences] = useState<DemoPreferences>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch {
        return getDefaultPreferences();
      }
    }
    return getDefaultPreferences();
  });

  const updatePreference = useCallback(<K extends keyof DemoPreferences>(
    key: K,
    value: DemoPreferences[K]
  ) => {
    setPreferences(prev => {
      const updated = { ...prev, [key]: value };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  const resetPreferences = useCallback(() => {
    const defaults = getDefaultPreferences();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(defaults));
    setPreferences(defaults);
  }, []);

  return { preferences, updatePreference, resetPreferences };
};

const getDefaultPreferences = (): DemoPreferences => ({
  playbackSpeed: 'normal',
  hintsEnabled: true,
  visitedHotspots: [],
  lastStep: 1,
});
```

---

## 7. Routing & Navigation

### 7.1 Route Configuration

```typescript
// src/App.tsx (additions)

import { DemoPage } from './pages/Demo';

// Inside Routes
<Route path="demo" element={
  <DemoProvider>
    <DemoPage />
  </DemoProvider>
} />
```

### 7.2 Navigation Component

```typescript
// src/pages/Demo/components/Navigation/StepNavigation.tsx

const StepNavigation: React.FC = () => {
  const { state, dispatch, canGoBack, canGoForward, progressPercentage } = useDemoContext();
  const currentStepConfig = demoScenario[state.currentStep - 1];

  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        p: 2,
        background: 'linear-gradient(transparent, rgba(0,0,0,0.9))',
        backdropFilter: 'blur(10px)',
      }}
    >
      <Box sx={{ maxWidth: 800, mx: 'auto' }}>
        {/* Step Info */}
        <Box sx={{ textAlign: 'center', mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Step {state.currentStep} of {TOTAL_STEPS}
          </Typography>
          <Typography variant="h6" sx={{ fontFamily: '"Space Grotesk", sans-serif' }}>
            {currentStepConfig.name}
          </Typography>
        </Box>

        {/* Controls Row */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2 }}>
          {/* Back Button */}
          <IconButton
            onClick={() => dispatch({ type: 'PREV_STEP' })}
            disabled={!canGoBack}
            sx={{ color: 'white' }}
          >
            <ArrowBackIcon />
          </IconButton>

          {/* Progress Indicator */}
          <ProgressIndicator
            currentStep={state.currentStep}
            totalSteps={TOTAL_STEPS}
            onStepClick={(step) => dispatch({ type: 'GO_TO_STEP', step })}
          />

          {/* Next Button */}
          <IconButton
            onClick={() => dispatch({ type: 'NEXT_STEP' })}
            disabled={!canGoForward}
            sx={{ color: 'white' }}
          >
            <ArrowForwardIcon />
          </IconButton>

          {/* Divider */}
          <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />

          {/* Auto-play Controls */}
          <AutoPlayControls
            isPlaying={state.isPlaying}
            speed={state.playbackSpeed}
            onTogglePlay={() => dispatch({ type: 'TOGGLE_PLAY' })}
            onSpeedChange={(speed) => dispatch({ type: 'SET_SPEED', speed })}
          />
        </Box>
      </Box>
    </Box>
  );
};
```

---

## 8. Animation System

### 8.1 Animation Constants

```typescript
// src/pages/Demo/constants/animations.ts

export const ANIMATION_DURATIONS = {
  fast: 0.2,
  normal: 0.3,
  slow: 0.5,
  verySlow: 0.8,
};

export const ANIMATION_EASINGS = {
  ease: [0.25, 0.1, 0.25, 1],
  easeIn: [0.42, 0, 1, 1],
  easeOut: [0, 0, 0.58, 1],
  easeInOut: [0.42, 0, 0.58, 1],
  spring: { type: 'spring', stiffness: 300, damping: 30 },
};

export const TRANSITIONS = {
  default: { duration: ANIMATION_DURATIONS.normal, ease: ANIMATION_EASINGS.easeOut },
  spring: ANIMATION_EASINGS.spring,
  slow: { duration: ANIMATION_DURATIONS.slow, ease: ANIMATION_EASINGS.easeInOut },
};
```

### 8.2 Framer Motion Variants

```typescript
// src/pages/Demo/constants/motionVariants.ts

// Screen transitions
export const screenVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

// Modal animations
export const modalVariants = {
  initial: { opacity: 0, scale: 0.95, y: 10 },
  animate: { opacity: 1, scale: 1, y: 0 },
  exit: { opacity: 0, scale: 0.95, y: 10 },
};

// Hotspot pulse
export const hotspotVariants = {
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

// Alert banner slide
export const alertVariants = {
  initial: { opacity: 0, x: 100 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 100 },
};

// Participant removal
export const participantRemovalVariants = {
  initial: { opacity: 1, scale: 1 },
  exit: {
    opacity: 0,
    scale: 0.8,
    transition: { duration: 0.8 },
  },
};

// Risk chip appearance
export const riskChipVariants = {
  initial: { opacity: 0, scale: 0.8, y: 10 },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 300, damping: 20 },
  },
};

// Transcript entry
export const transcriptEntryVariants = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
};
```

### 8.3 Reduced Motion Support

```typescript
// src/pages/Demo/hooks/useReducedMotion.ts

export const useReducedMotion = () => {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mediaQuery.matches);

    const handler = (event: MediaQueryListEvent) => {
      setReducedMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return reducedMotion;
};

// Usage in components
const MyComponent = () => {
  const reducedMotion = useReducedMotion();

  return (
    <motion.div
      variants={reducedMotion ? {} : screenVariants}
      initial={reducedMotion ? false : 'initial'}
      animate="animate"
      exit={reducedMotion ? undefined : 'exit'}
    >
      {/* content */}
    </motion.div>
  );
};
```

---

## 9. Modal System

### 9.1 Modal Types

```typescript
// src/pages/Demo/types/modal.types.ts

type ModalType =
  | 'explainer'           // General educational content
  | 'riskBreakdown'       // Detailed risk score analysis
  | 'forensic'            // Forensic evidence viewer
  | 'timeline'            // Full timeline detail
  | 'transcript'          // Transcript analysis
  | 'glossary';           // Term definitions

interface ModalConfig {
  type: ModalType;
  title: string;
  content: React.ReactNode;
  size: 'sm' | 'md' | 'lg' | 'xl';
  data?: unknown;         // Type-specific data
}

interface ExplainerModalData {
  description: string;
  bulletPoints?: string[];
  image?: string;
}

interface RiskBreakdownModalData {
  videoAnalysis: number;
  audioAnalysis: number;
  behavioralAnalysis: number;
  networkAnalysis: number;
  overallScore: number;
}

interface ForensicModalData {
  forensics: ForensicEvidence;
  activeTab?: 'video' | 'audio' | 'network' | 'behavioral';
}
```

### 9.2 Modal Portal

```typescript
// src/pages/Demo/components/Modals/ModalPortal.tsx

const ModalPortal: React.FC = () => {
  const { state, dispatch } = useDemoContext();
  const { activeModal } = state;

  if (!activeModal) return null;

  return createPortal(
    <AnimatePresence>
      <motion.div
        key="modal-backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={() => dispatch({ type: 'CLOSE_MODAL' })}
        style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
        }}
      >
        <motion.div
          key="modal-content"
          variants={modalVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          onClick={(e) => e.stopPropagation()}
        >
          <DemoModal config={activeModal} onClose={() => dispatch({ type: 'CLOSE_MODAL' })} />
        </motion.div>
      </motion.div>
    </AnimatePresence>,
    document.body
  );
};
```

### 9.3 Risk Breakdown Modal

```typescript
// src/pages/Demo/components/Modals/RiskBreakdownModal.tsx

interface RiskBreakdownModalProps {
  data: RiskBreakdownModalData;
}

const RiskBreakdownModal: React.FC<RiskBreakdownModalProps> = ({ data }) => {
  const { isDark } = useThemeMode();

  const components = [
    { label: 'Video Analysis', value: data.videoAnalysis, weight: 40, icon: <VideocamIcon /> },
    { label: 'Audio Analysis', value: data.audioAnalysis, weight: 30, icon: <MicIcon /> },
    { label: 'Behavioral', value: data.behavioralAnalysis, weight: 20, icon: <PsychologyIcon /> },
    { label: 'Network', value: data.networkAnalysis, weight: 10, icon: <PublicIcon /> },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom sx={{ fontFamily: '"Space Grotesk", sans-serif' }}>
        Risk Score Breakdown
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        This participant's risk score is calculated from multiple analysis dimensions:
      </Typography>

      <Stack spacing={2}>
        {components.map((component) => (
          <Box key={component.label}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {component.icon}
                <Typography variant="body2" fontWeight={600}>
                  {component.label}
                </Typography>
              </Box>
              <Typography
                variant="body2"
                sx={{ fontFamily: '"JetBrains Mono", monospace' }}
              >
                {component.value}% ({component.weight}% weight)
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={component.value}
              sx={{
                height: 8,
                borderRadius: 4,
                '& .MuiLinearProgress-bar': {
                  background: getRiskGradient(getRiskLevel(component.value)),
                },
              }}
            />
          </Box>
        ))}
      </Stack>

      <Divider sx={{ my: 3 }} />

      {/* Overall Score */}
      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="overline" color="text.secondary">
          Overall Risk Score
        </Typography>
        <Typography
          variant="h2"
          sx={{
            fontFamily: '"JetBrains Mono", monospace',
            fontWeight: 700,
            background: getRiskGradient(getRiskLevel(data.overallScore)),
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          {data.overallScore}%
        </Typography>
        <Chip
          label={getRiskLevel(data.overallScore).toUpperCase()}
          sx={{
            mt: 1,
            background: getRiskGradient(getRiskLevel(data.overallScore)),
            color: 'white',
            fontWeight: 600,
          }}
        />
      </Box>
    </Box>
  );
};
```

---

## 10. Hotspot System

### 10.1 Hotspot Configuration

```typescript
// src/pages/Demo/data/hotspotContent.ts

export const hotspotDefinitions: Record<string, HotspotDefinition> = {
  'risk-meter': {
    type: 'data',
    tooltip: 'Real-time threat assessment',
    modal: {
      type: 'riskBreakdown',
      title: 'Risk Score Breakdown',
      size: 'md',
    },
  },
  'trust-badge': {
    type: 'info',
    tooltip: 'Participant trust score',
    modal: {
      type: 'explainer',
      title: 'Trust Scores Explained',
      size: 'md',
      content: (
        <Box>
          <Typography paragraph>
            Trust scores are calculated based on multiple factors:
          </Typography>
          <List>
            <ListItem>Device fingerprint recognition</ListItem>
            <ListItem>Login history and patterns</ListItem>
            <ListItem>Video/audio authenticity analysis</ListItem>
            <ListItem>Behavioral consistency</ListItem>
          </List>
        </Box>
      ),
    },
  },
  'deepsafe-bot': {
    type: 'info',
    tooltip: 'DeepSafe meeting guardian',
    modal: {
      type: 'explainer',
      title: 'DeepSafe Bot',
      size: 'sm',
      content: (
        <Typography>
          The DeepSafe bot automatically joins every protected meeting.
          It analyzes all participants in real-time without recording
          or storing video content.
        </Typography>
      ),
    },
  },
  // ... more hotspots
};
```

### 10.2 Hotspot Component

```typescript
// src/pages/Demo/components/Hotspots/Hotspot.tsx

interface HotspotProps {
  id: string;
  anchor: string;           // CSS selector or element ID
  offsetX?: number;
  offsetY?: number;
}

const Hotspot: React.FC<HotspotProps> = ({ id, anchor, offsetX = 0, offsetY = 0 }) => {
  const { state, dispatch } = useDemoContext();
  const definition = hotspotDefinitions[id];
  const [position, setPosition] = useState<{ top: number; left: number } | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);

  const isVisited = state.visitedHotspots.has(id);

  // Calculate position based on anchor element
  useEffect(() => {
    const updatePosition = () => {
      const anchorElement = document.querySelector(anchor);
      if (anchorElement) {
        const rect = anchorElement.getBoundingClientRect();
        setPosition({
          top: rect.top + offsetY,
          left: rect.right + offsetX,
        });
      }
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    return () => window.removeEventListener('resize', updatePosition);
  }, [anchor, offsetX, offsetY]);

  const handleClick = () => {
    dispatch({ type: 'MARK_HOTSPOT_VISITED', hotspotId: id });
    dispatch({
      type: 'OPEN_MODAL',
      modal: {
        ...definition.modal,
        data: getHotspotData(id, state),
      },
    });
  };

  if (!position) return null;

  const hotspotColor = {
    info: brandColors.primary.signalTeal,
    data: brandColors.primary.deepSafeBlue,
    action: brandColors.primary.alertAmber,
  }[definition.type];

  return (
    <Box
      sx={{
        position: 'fixed',
        top: position.top,
        left: position.left,
        zIndex: 1000,
      }}
    >
      <motion.button
        variants={hotspotVariants}
        initial="initial"
        animate="animate"
        onClick={handleClick}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        style={{
          width: 16,
          height: 16,
          borderRadius: '50%',
          backgroundColor: hotspotColor,
          border: 'none',
          cursor: 'pointer',
          boxShadow: `0 0 10px ${hotspotColor}80`,
          opacity: isVisited ? 0.5 : 1,
        }}
        aria-label={definition.tooltip}
      />

      {/* Tooltip */}
      <AnimatePresence>
        {showTooltip && (
          <HotspotTooltip text={definition.tooltip} />
        )}
      </AnimatePresence>
    </Box>
  );
};
```

### 10.3 Hotspot Manager

```typescript
// src/pages/Demo/components/Hotspots/HotspotManager.tsx

const HotspotManager: React.FC = () => {
  const { activeHotspots, state } = useDemoContext();
  const { preferences } = useDemoPreferences();

  // Don't render hotspots if hints are disabled
  if (!preferences.hintsEnabled) return null;

  // Don't render while modal is open
  if (state.activeModal) return null;

  return (
    <>
      {activeHotspots.map((hotspot) => (
        <Hotspot
          key={hotspot.id}
          id={hotspot.id}
          anchor={hotspot.anchor}
          offsetX={hotspot.offsetX}
          offsetY={hotspot.offsetY}
        />
      ))}
    </>
  );
};
```

---

## 11. Accessibility Implementation

### 11.1 ARIA Attributes

```typescript
// Example: RiskMeter with accessibility
const RiskMeter: React.FC<RiskMeterProps> = ({ score, showLabel }) => {
  const riskLevel = getRiskLevel(score);

  return (
    <Box
      role="meter"
      aria-valuenow={score}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Risk score: ${score} percent, ${riskLevel} risk level`}
    >
      <LinearProgress
        variant="determinate"
        value={score}
        aria-hidden="true"  // Visual only, role="meter" provides semantics
      />
      {showLabel && (
        <span className="sr-only">
          Risk level: {riskLevel}
        </span>
      )}
    </Box>
  );
};
```

### 11.2 Live Regions for Announcements

```typescript
// src/pages/Demo/components/Accessibility/LiveRegion.tsx

const LiveRegion: React.FC = () => {
  const [announcement, setAnnouncement] = useState('');

  useEffect(() => {
    const handleAnnouncement = (event: CustomEvent<string>) => {
      setAnnouncement(event.detail);
      // Clear after announcement is read
      setTimeout(() => setAnnouncement(''), 1000);
    };

    window.addEventListener('demo-announce', handleAnnouncement as EventListener);
    return () => window.removeEventListener('demo-announce', handleAnnouncement as EventListener);
  }, []);

  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    >
      {announcement}
    </div>
  );
};

// Usage
export const announceToScreenReader = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
  window.dispatchEvent(new CustomEvent('demo-announce', { detail: message }));
};
```

### 11.3 Focus Management

```typescript
// src/pages/Demo/hooks/useFocusManagement.ts

export const useFocusManagement = () => {
  const { state } = useDemoContext();
  const previousFocusRef = useRef<HTMLElement | null>(null);

  // Store focus when modal opens
  useEffect(() => {
    if (state.activeModal) {
      previousFocusRef.current = document.activeElement as HTMLElement;

      // Focus first focusable element in modal
      setTimeout(() => {
        const modal = document.querySelector('[role="dialog"]');
        const firstFocusable = modal?.querySelector<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        firstFocusable?.focus();
      }, 100);
    } else if (previousFocusRef.current) {
      // Restore focus when modal closes
      previousFocusRef.current.focus();
      previousFocusRef.current = null;
    }
  }, [state.activeModal]);
};
```

---

## 12. Performance Optimization

### 12.1 Code Splitting

```typescript
// src/pages/Demo/DemoPage.tsx

// Lazy load heavy components
const ForensicModal = lazy(() => import('./components/Modals/ForensicModal'));
const VideoCallInterface = lazy(() => import('./components/VideoCallInterface/VideoCallInterface'));

// Usage with Suspense
<Suspense fallback={<ScreenSkeleton />}>
  {currentStep >= 3 && currentStep <= 7 && <VideoCallInterface {...props} />}
</Suspense>
```

### 12.2 Memoization

```typescript
// Memoize expensive computations
const activeHotspots = useMemo(
  () => currentStepConfig.hotspots?.filter(h => !state.visitedHotspots.has(h.id)) || [],
  [currentStepConfig.hotspots, state.visitedHotspots]
);

// Memoize components that don't need frequent updates
const MemoizedTranscriptPanel = memo(TranscriptPanel, (prev, next) => {
  return prev.entries.length === next.entries.length &&
         prev.highlightedEntryId === next.highlightedEntryId;
});

// Memoize callbacks passed to children
const handleHotspotClick = useCallback((id: string) => {
  dispatch({ type: 'OPEN_MODAL', modal: hotspotDefinitions[id].modal });
}, [dispatch]);
```

### 12.3 Image Optimization

```typescript
// src/pages/Demo/components/OptimizedImage.tsx

interface OptimizedImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
}

const OptimizedImage: React.FC<OptimizedImageProps> = ({ src, alt, width, height }) => {
  const [loaded, setLoaded] = useState(false);

  return (
    <Box sx={{ position: 'relative', width, height }}>
      {!loaded && (
        <Skeleton
          variant="rectangular"
          width={width}
          height={height}
          animation="wave"
        />
      )}
      <img
        src={src}
        alt={alt}
        width={width}
        height={height}
        loading="lazy"
        decoding="async"
        onLoad={() => setLoaded(true)}
        style={{
          opacity: loaded ? 1 : 0,
          transition: 'opacity 0.3s',
        }}
      />
    </Box>
  );
};
```

---

## 13. Testing Strategy

### 13.1 Unit Tests

```typescript
// src/pages/Demo/__tests__/demoReducer.test.ts

describe('demoReducer', () => {
  describe('NEXT_STEP', () => {
    it('increments currentStep when not at max', () => {
      const state = { ...initialState, currentStep: 3 };
      const result = demoReducer(state, { type: 'NEXT_STEP' });
      expect(result.currentStep).toBe(4);
    });

    it('does not increment past TOTAL_STEPS', () => {
      const state = { ...initialState, currentStep: TOTAL_STEPS };
      const result = demoReducer(state, { type: 'NEXT_STEP' });
      expect(result.currentStep).toBe(TOTAL_STEPS);
    });

    it('applies step-specific state changes', () => {
      const state = { ...initialState, currentStep: 3 };
      const result = demoReducer(state, { type: 'NEXT_STEP' });
      expect(result.currentRiskScore).toBe(demoScenario[3].riskScore);
    });
  });

  describe('OPEN_MODAL', () => {
    it('sets activeModal and pauses playback', () => {
      const state = { ...initialState, isPlaying: true };
      const modal: ModalConfig = { type: 'explainer', title: 'Test', size: 'md', content: null };
      const result = demoReducer(state, { type: 'OPEN_MODAL', modal });

      expect(result.activeModal).toEqual(modal);
      expect(result.isPlaying).toBe(false);
    });
  });
});
```

### 13.2 Integration Tests

```typescript
// src/pages/Demo/__tests__/DemoPage.integration.test.tsx

describe('DemoPage Integration', () => {
  it('navigates through all steps', async () => {
    render(
      <DemoProvider>
        <DemoPage />
      </DemoProvider>
    );

    // Start at step 1
    expect(screen.getByText('Step 1 of 9')).toBeInTheDocument();

    // Navigate forward
    const nextButton = screen.getByRole('button', { name: /next/i });
    await userEvent.click(nextButton);

    expect(screen.getByText('Step 2 of 9')).toBeInTheDocument();
  });

  it('opens modal when hotspot clicked', async () => {
    render(
      <DemoProvider>
        <DemoPage />
      </DemoProvider>
    );

    // Navigate to step with hotspots
    // ... navigate to step 3

    const hotspot = screen.getByRole('button', { name: /risk score/i });
    await userEvent.click(hotspot);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Risk Score Breakdown')).toBeInTheDocument();
  });

  it('supports keyboard navigation', async () => {
    render(
      <DemoProvider>
        <DemoPage />
      </DemoProvider>
    );

    // Press right arrow
    await userEvent.keyboard('{ArrowRight}');
    expect(screen.getByText('Step 2 of 9')).toBeInTheDocument();

    // Press left arrow
    await userEvent.keyboard('{ArrowLeft}');
    expect(screen.getByText('Step 1 of 9')).toBeInTheDocument();
  });
});
```

### 13.3 E2E Tests

```typescript
// cypress/e2e/demo.cy.ts

describe('Demo E2E', () => {
  beforeEach(() => {
    cy.visit('/demo');
  });

  it('completes full demo flow', () => {
    // Welcome screen
    cy.contains('Experience DeepSafe in Action').should('be.visible');
    cy.contains('Start Demo').click();

    // Step through demo
    for (let i = 2; i <= 9; i++) {
      cy.contains(`Step ${i} of 9`).should('be.visible');
      cy.get('[aria-label="Next step"]').click();
    }

    // Success screen
    cy.contains('ATTACK PREVENTED').should('be.visible');
    cy.contains('$250,000 Protected').should('be.visible');
  });

  it('shows risk score animation', () => {
    cy.contains('Start Demo').click();

    // Navigate to step with risk increase
    cy.navigateToStep(4);

    // Risk meter should animate
    cy.get('[role="meter"]')
      .should('have.attr', 'aria-valuenow')
      .and('be.gt', '0');
  });
});
```

---

## 14. Build Configuration

### 14.1 Integrated Build

No changes needed - uses standard Vite build.

### 14.2 Standalone Build

```typescript
// vite.config.demo.ts

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist-demo',
    rollupOptions: {
      input: resolve(__dirname, 'demo.html'),
    },
  },
  define: {
    'import.meta.env.STANDALONE_DEMO': JSON.stringify(true),
  },
});
```

```html
<!-- demo.html -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DeepSafe Interactive Demo</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/demo-entry.tsx"></script>
  </body>
</html>
```

```typescript
// src/demo-entry.tsx

import React from 'react';
import ReactDOM from 'react-dom/client';
import { ThemeProvider } from './context/ThemeContext';
import { DemoProvider } from './pages/Demo/context/DemoProvider';
import { DemoPage } from './pages/Demo';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <DemoProvider>
        <DemoPage standalone />
      </DemoProvider>
    </ThemeProvider>
  </React.StrictMode>
);
```

### 14.3 Package.json Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "build:demo": "tsc && vite build --config vite.config.demo.ts",
    "preview:demo": "vite preview --outDir dist-demo",
    "test:demo": "vitest run src/pages/Demo",
    "test:demo:watch": "vitest src/pages/Demo"
  }
}
```

---

## 15. File Structure

```
src/pages/Demo/
├── DemoPage.tsx                    # Main container component
├── index.ts                        # Public exports
│
├── context/
│   ├── DemoContext.tsx             # Context definition
│   ├── DemoProvider.tsx            # Context provider
│   └── demoReducer.ts              # State reducer
│
├── hooks/
│   ├── useDemoContext.ts           # Context hook
│   ├── useAutoPlay.ts              # Auto-play timer logic
│   ├── useKeyboardNavigation.ts    # Keyboard shortcuts
│   ├── useRiskAnimation.ts         # Risk score animation
│   ├── useDemoPreferences.ts       # LocalStorage persistence
│   ├── useReducedMotion.ts         # A11y motion preference
│   └── useFocusManagement.ts       # Modal focus trap
│
├── components/
│   ├── VideoCallInterface/
│   │   ├── VideoCallInterface.tsx  # Main video call layout
│   │   ├── MeetingHeader.tsx       # Meeting title bar
│   │   ├── ParticipantGrid.tsx     # Video tile grid
│   │   ├── ParticipantTile.tsx     # Individual video tile
│   │   ├── ControlBar.tsx          # Bottom controls (mute, etc.)
│   │   ├── SpeakingIndicator.tsx   # Active speaker animation
│   │   └── DetectionOverlay.tsx    # Deepfake detection visual
│   │
│   ├── DeepSafeOverlay/
│   │   ├── RiskMeter.tsx           # Risk score display
│   │   ├── AlertBanner.tsx         # Warning notifications
│   │   ├── VerificationModal.tsx   # Identity verification UI
│   │   └── ThreatConfirmedOverlay.tsx  # Threat confirmation
│   │
│   ├── TranscriptPanel/
│   │   ├── TranscriptPanel.tsx     # Sidebar container
│   │   ├── TranscriptEntry.tsx     # Individual message
│   │   └── RiskChips.tsx           # Risk indicator tags
│   │
│   ├── Navigation/
│   │   ├── StepNavigation.tsx      # Full navigation bar
│   │   ├── ProgressIndicator.tsx   # Step dots
│   │   ├── NavButton.tsx           # Back/Next buttons
│   │   └── AutoPlayControls.tsx    # Play/speed controls
│   │
│   ├── Modals/
│   │   ├── ModalPortal.tsx         # Portal renderer
│   │   ├── DemoModal.tsx           # Base modal component
│   │   ├── ExplainerModal.tsx      # Educational content
│   │   ├── RiskBreakdownModal.tsx  # Risk score details
│   │   ├── ForensicModal.tsx       # Evidence viewer
│   │   └── TimelineModal.tsx       # Full timeline view
│   │
│   ├── Hotspots/
│   │   ├── HotspotManager.tsx      # Hotspot orchestrator
│   │   ├── Hotspot.tsx             # Individual hotspot
│   │   └── HotspotTooltip.tsx      # Hover tooltip
│   │
│   ├── Screens/
│   │   ├── WelcomeScreen.tsx       # Step 1: Introduction
│   │   ├── LobbyScreen.tsx         # Step 2: Meeting lobby
│   │   ├── IncidentReportScreen.tsx # Step 8: Report
│   │   └── SuccessScreen.tsx       # Step 9: Summary
│   │
│   └── Accessibility/
│       └── LiveRegion.tsx          # Screen reader announcements
│
├── data/
│   ├── demoScenario.ts             # Step configurations
│   ├── transcriptData.ts           # Conversation script
│   ├── forensicData.ts             # Forensic evidence
│   ├── hotspotContent.ts           # Hotspot definitions
│   └── participantData.ts          # Character definitions
│
├── types/
│   ├── demo.types.ts               # Core type definitions
│   ├── modal.types.ts              # Modal-specific types
│   └── hotspot.types.ts            # Hotspot types
│
├── constants/
│   ├── animations.ts               # Animation constants
│   ├── motionVariants.ts           # Framer Motion variants
│   └── config.ts                   # General config
│
├── utils/
│   ├── riskHelpers.ts              # Risk calculation helpers
│   ├── formatters.ts               # Date/time formatting
│   └── accessibility.ts            # A11y utilities
│
└── __tests__/
    ├── demoReducer.test.ts         # Reducer unit tests
    ├── DemoPage.integration.test.tsx # Integration tests
    └── hooks/                      # Hook tests
```

---

## 16. Implementation Plan

### Phase 1: Foundation (Week 1)

| Task | Priority | Estimate |
|------|----------|----------|
| Set up file structure | P0 | 2h |
| Create type definitions | P0 | 3h |
| Implement DemoContext + reducer | P0 | 4h |
| Create demoScenario data | P0 | 3h |
| Build StepNavigation component | P0 | 4h |
| Add keyboard navigation hook | P1 | 2h |

### Phase 2: Core Screens (Week 2)

| Task | Priority | Estimate |
|------|----------|----------|
| WelcomeScreen | P0 | 3h |
| LobbyScreen | P0 | 3h |
| VideoCallInterface (basic) | P0 | 6h |
| ParticipantTile | P0 | 4h |
| TranscriptPanel | P0 | 4h |

### Phase 3: DeepSafe Overlays (Week 3)

| Task | Priority | Estimate |
|------|----------|----------|
| RiskMeter with animation | P0 | 4h |
| AlertBanner | P0 | 2h |
| DetectionOverlay | P0 | 3h |
| VerificationModal | P0 | 4h |
| ThreatConfirmedOverlay | P0 | 3h |
| IncidentReportScreen | P0 | 4h |
| SuccessScreen | P0 | 3h |

### Phase 4: Interactive Features (Week 4)

| Task | Priority | Estimate |
|------|----------|----------|
| Hotspot system | P0 | 6h |
| Modal system + portal | P0 | 4h |
| ExplainerModal content | P0 | 3h |
| RiskBreakdownModal | P1 | 4h |
| ForensicModal | P1 | 5h |
| Auto-play functionality | P1 | 3h |

### Phase 5: Polish & Testing (Week 5)

| Task | Priority | Estimate |
|------|----------|----------|
| Animations & transitions | P1 | 6h |
| Accessibility audit | P0 | 4h |
| Unit tests | P1 | 6h |
| Integration tests | P1 | 4h |
| Performance optimization | P2 | 4h |
| Standalone build setup | P2 | 3h |

### Milestones

1. **M1 (End of Week 2)**: Basic demo flow functional (no hotspots/modals)
2. **M2 (End of Week 3)**: Full visual experience complete
3. **M3 (End of Week 4)**: All interactive features working
4. **M4 (End of Week 5)**: Production-ready with tests

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2024 | DeepSafe Engineering | Initial TDD creation |

---

*This TDD provides the technical blueprint for implementing the DeepSafe Interactive Demo. Refer to the PRD for product requirements and user experience specifications.*
