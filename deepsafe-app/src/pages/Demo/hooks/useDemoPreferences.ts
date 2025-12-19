import { useState, useCallback, useEffect } from 'react';
import type { DemoPreferences, PlaybackSpeed } from '../types/demo.types';

const STORAGE_KEY = 'deepsafe-demo-prefs';

/**
 * Get default preferences
 */
const getDefaultPreferences = (): DemoPreferences => ({
  playbackSpeed: 'normal',
  hintsEnabled: true,
  visitedHotspots: [],
  lastStep: 1,
});

/**
 * Load preferences from localStorage
 */
const loadPreferences = (): DemoPreferences => {
  if (typeof window === 'undefined') {
    return getDefaultPreferences();
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      return {
        ...getDefaultPreferences(),
        ...parsed,
      };
    }
  } catch (error) {
    console.warn('Failed to load demo preferences:', error);
  }

  return getDefaultPreferences();
};

/**
 * Save preferences to localStorage
 */
const savePreferences = (prefs: DemoPreferences): void => {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  } catch (error) {
    console.warn('Failed to save demo preferences:', error);
  }
};

/**
 * Hook for managing demo preferences with localStorage persistence
 */
export const useDemoPreferences = () => {
  const [preferences, setPreferences] = useState<DemoPreferences>(getDefaultPreferences);

  // Load preferences on mount
  useEffect(() => {
    setPreferences(loadPreferences());
  }, []);

  // Save preferences whenever they change
  useEffect(() => {
    savePreferences(preferences);
  }, [preferences]);

  /**
   * Update a single preference
   */
  const updatePreference = useCallback(
    <K extends keyof DemoPreferences>(key: K, value: DemoPreferences[K]) => {
      setPreferences((prev) => ({
        ...prev,
        [key]: value,
      }));
    },
    []
  );

  /**
   * Update playback speed
   */
  const setPlaybackSpeed = useCallback((speed: PlaybackSpeed) => {
    updatePreference('playbackSpeed', speed);
  }, [updatePreference]);

  /**
   * Toggle hints
   */
  const toggleHints = useCallback(() => {
    setPreferences((prev) => ({
      ...prev,
      hintsEnabled: !prev.hintsEnabled,
    }));
  }, []);

  /**
   * Mark a hotspot as visited
   */
  const markHotspotVisited = useCallback((hotspotId: string) => {
    setPreferences((prev) => {
      if (prev.visitedHotspots.includes(hotspotId)) {
        return prev;
      }
      return {
        ...prev,
        visitedHotspots: [...prev.visitedHotspots, hotspotId],
      };
    });
  }, []);

  /**
   * Check if a hotspot has been visited
   */
  const isHotspotVisited = useCallback(
    (hotspotId: string) => preferences.visitedHotspots.includes(hotspotId),
    [preferences.visitedHotspots]
  );

  /**
   * Save last step for resume functionality
   */
  const saveLastStep = useCallback((step: number) => {
    updatePreference('lastStep', step);
  }, [updatePreference]);

  /**
   * Reset all preferences to defaults
   */
  const resetPreferences = useCallback(() => {
    const defaults = getDefaultPreferences();
    setPreferences(defaults);
    savePreferences(defaults);
  }, []);

  /**
   * Clear visited hotspots only
   */
  const clearVisitedHotspots = useCallback(() => {
    setPreferences((prev) => ({
      ...prev,
      visitedHotspots: [],
    }));
  }, []);

  return {
    preferences,
    setPlaybackSpeed,
    toggleHints,
    markHotspotVisited,
    isHotspotVisited,
    saveLastStep,
    resetPreferences,
    clearVisitedHotspots,
    // Convenience getters
    isHintsEnabled: preferences.hintsEnabled,
    playbackSpeed: preferences.playbackSpeed,
    lastStep: preferences.lastStep,
    visitedHotspotsCount: preferences.visitedHotspots.length,
  };
};

export default useDemoPreferences;
