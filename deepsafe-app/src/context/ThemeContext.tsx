import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { createDarkTheme, createLightTheme } from '../theme/theme';

type ThemeMode = 'dark' | 'light';

interface ThemeContextType {
  mode: ThemeMode;
  toggleTheme: () => void;
  setTheme: (mode: ThemeMode) => void;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = 'deepsafe-theme';

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mode, setMode] = useState<ThemeMode>(() => {
    // Check localStorage first
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(THEME_STORAGE_KEY);
      if (saved === 'dark' || saved === 'light') {
        return saved;
      }
    }
    // Default to dark mode per brand guidelines
    return 'dark';
  });

  // Create theme based on current mode
  const theme = useMemo(
    () => (mode === 'dark' ? createDarkTheme() : createLightTheme()),
    [mode]
  );

  // Persist theme and update data attribute
  useEffect(() => {
    localStorage.setItem(THEME_STORAGE_KEY, mode);
    document.documentElement.setAttribute('data-theme', mode);

    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', mode === 'dark' ? '#0B1220' : '#F7F9FC');
    }
  }, [mode]);

  // Toggle with smooth transition
  const toggleTheme = useCallback(() => {
    // Add transition class for smooth theme change
    document.body.classList.add('theme-transitioning');

    setMode((prev) => (prev === 'dark' ? 'light' : 'dark'));

    // Remove transition class after animation completes
    setTimeout(() => {
      document.body.classList.remove('theme-transitioning');
    }, 300);
  }, []);

  // Set specific theme
  const setTheme = useCallback((newMode: ThemeMode) => {
    if (newMode !== mode) {
      document.body.classList.add('theme-transitioning');
      setMode(newMode);
      setTimeout(() => {
        document.body.classList.remove('theme-transitioning');
      }, 300);
    }
  }, [mode]);

  const value = useMemo(
    () => ({
      mode,
      toggleTheme,
      setTheme,
      isDark: mode === 'dark',
    }),
    [mode, toggleTheme, setTheme]
  );

  return (
    <ThemeContext.Provider value={value}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

export const useThemeMode = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useThemeMode must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeContext;
