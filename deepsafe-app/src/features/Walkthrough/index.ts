// Context and Provider
export { WalkthroughProvider, useWalkthroughContext } from './context/WalkthroughContext';

// Components
export { WalkthroughOverlay } from './components/WalkthroughOverlay';
export { WelcomeModal } from './components/WelcomeModal';
export { CompletionScreen } from './components/CompletionScreen';
export { WalkthroughModal } from './components/WalkthroughModal';
export { Hotspot, HotspotTooltip } from './components/Hotspots';

// Types
export type {
  WalkthroughState,
  WalkthroughAction,
  WalkthroughStep,
  WalkthroughHotspot,
  WalkthroughModalContent,
  WalkthroughContextValue,
  PlaybackSpeed,
  SkipPreference,
} from './types/walkthrough.types';

// Data
export { walkthroughScenario, WALKTHROUGH_TOTAL_STEPS } from './data/walkthroughScenario';
