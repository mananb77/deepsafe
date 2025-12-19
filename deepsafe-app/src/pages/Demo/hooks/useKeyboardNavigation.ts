import { useEffect, useCallback } from 'react';
import { useDemoContext } from '../context/DemoContext';

interface KeyboardNavigationOptions {
  enabled?: boolean;
  onStepChange?: (step: number) => void;
}

/**
 * Hook for keyboard navigation in the demo
 * Supports arrow keys, space bar, escape, and number keys
 */
export const useKeyboardNavigation = (options: KeyboardNavigationOptions = {}) => {
  const { enabled = true, onStepChange } = options;
  const { state, dispatch, canGoBack, canGoForward } = useDemoContext();

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Don't handle if typing in an input
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement ||
        (event.target as HTMLElement).isContentEditable
      ) {
        return;
      }

      // Don't handle if modal is open (except Escape)
      if (state.activeModal && event.key !== 'Escape') {
        return;
      }

      switch (event.key) {
        case 'ArrowRight':
          event.preventDefault();
          if (canGoForward) {
            dispatch({ type: 'NEXT_STEP' });
            onStepChange?.(state.currentStep + 1);
          }
          break;

        case 'ArrowLeft':
          event.preventDefault();
          if (canGoBack) {
            dispatch({ type: 'PREV_STEP' });
            onStepChange?.(state.currentStep - 1);
          }
          break;

        case ' ': // Space bar
          event.preventDefault();
          dispatch({ type: 'TOGGLE_PLAY' });
          break;

        case 'Escape':
          event.preventDefault();
          if (state.activeModal) {
            dispatch({ type: 'CLOSE_MODAL' });
          }
          break;

        // Number keys 1-9 to jump to specific steps
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9': {
          event.preventDefault();
          const targetStep = parseInt(event.key, 10);
          dispatch({ type: 'GO_TO_STEP', step: targetStep });
          onStepChange?.(targetStep);
          break;
        }

        // 'R' to reset/replay
        case 'r':
        case 'R':
          if (event.metaKey || event.ctrlKey) {
            // Don't override browser refresh
            return;
          }
          event.preventDefault();
          dispatch({ type: 'RESET_DEMO' });
          onStepChange?.(1);
          break;

        // 'T' to toggle transcript
        case 't':
        case 'T':
          event.preventDefault();
          dispatch({ type: 'TOGGLE_TRANSCRIPT' });
          break;

        default:
          break;
      }
    },
    [state, dispatch, canGoBack, canGoForward, onStepChange]
  );

  useEffect(() => {
    if (!enabled) return;

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [enabled, handleKeyDown]);

  return {
    shortcuts: [
      { key: '←/→', description: 'Previous/Next step' },
      { key: 'Space', description: 'Play/Pause auto-play' },
      { key: '1-9', description: 'Jump to step' },
      { key: 'Esc', description: 'Close modal' },
      { key: 'T', description: 'Toggle transcript' },
      { key: 'R', description: 'Replay demo' },
    ],
  };
};

export default useKeyboardNavigation;
