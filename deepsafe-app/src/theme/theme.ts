import { createTheme } from '@mui/material/styles';
import type { Theme, ThemeOptions } from '@mui/material/styles';
import { brandColors } from './colors';
import { darkGradients, lightGradients, functionalGradients } from './gradients';

// Extend MUI theme types for custom properties
declare module '@mui/material/styles' {
  interface Theme {
    gradients: typeof darkGradients | typeof lightGradients;
    functional: typeof functionalGradients;
    customColors: {
      surface: string;
      elevated: string;
      cardBg: string;
      borderColor: string;
      borderColorLight: string;
      glowPrimary: string;
      glowSecondary: string;
    };
  }
  interface ThemeOptions {
    gradients?: typeof darkGradients | typeof lightGradients;
    functional?: typeof functionalGradients;
    customColors?: {
      surface: string;
      elevated: string;
      cardBg: string;
      borderColor: string;
      borderColorLight: string;
      glowPrimary: string;
      glowSecondary: string;
    };
  }
}

// Shared typography configuration
const baseTypography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  h1: {
    fontFamily: '"Space Grotesk", "Inter", sans-serif',
    fontSize: '2.5rem',
    fontWeight: 700,
    lineHeight: 1.2,
    letterSpacing: '-0.02em',
  },
  h2: {
    fontFamily: '"Space Grotesk", "Inter", sans-serif',
    fontSize: '2rem',
    fontWeight: 700,
    lineHeight: 1.3,
    letterSpacing: '-0.01em',
  },
  h3: {
    fontFamily: '"Space Grotesk", "Inter", sans-serif',
    fontSize: '1.75rem',
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h4: {
    fontSize: '1.5rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1.25rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h6: {
    fontSize: '1rem',
    fontWeight: 600,
    lineHeight: 1.5,
  },
  subtitle1: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.5,
  },
  subtitle2: {
    fontSize: '0.875rem',
    fontWeight: 500,
    lineHeight: 1.5,
  },
  body1: {
    fontSize: '1rem',
    lineHeight: 1.6,
  },
  body2: {
    fontSize: '0.875rem',
    lineHeight: 1.6,
  },
  caption: {
    fontSize: '0.75rem',
    lineHeight: 1.5,
  },
  overline: {
    fontSize: '0.75rem',
    fontWeight: 600,
    letterSpacing: '0.1em',
    textTransform: 'uppercase' as const,
    lineHeight: 1.5,
  },
  button: {
    textTransform: 'none' as const,
    fontWeight: 600,
  },
};

// Shared shape configuration
const baseShape = {
  borderRadius: 12,
};

// Create Dark Theme (DEFAULT)
export const createDarkTheme = (): Theme => {
  const darkThemeOptions: ThemeOptions = {
    palette: {
      mode: 'dark',
      primary: {
        main: brandColors.primary.deepSafeBlue,
        light: '#3A6EDC',
        dark: '#152B5C',
        contrastText: '#FFFFFF',
      },
      secondary: {
        main: brandColors.primary.signalTeal,
        light: '#3BC9C9',
        dark: '#148F82',
        contrastText: '#FFFFFF',
      },
      error: {
        main: brandColors.statusDark.error,
        light: '#FF8A8A',
        dark: brandColors.primary.threatRed,
      },
      warning: {
        main: brandColors.statusDark.warning,
        light: '#FFD970',
        dark: brandColors.primary.alertAmber,
      },
      success: {
        main: brandColors.statusDark.success,
        light: '#5EE4B8',
        dark: '#2DBE8B',
      },
      info: {
        main: brandColors.statusDark.info,
        light: '#5ED8D8',
        dark: brandColors.primary.signalTeal,
      },
      background: {
        default: brandColors.dark.primary,
        paper: brandColors.dark.surface,
      },
      text: {
        primary: brandColors.darkText.primary,
        secondary: brandColors.darkText.secondary,
        disabled: brandColors.darkText.muted,
      },
      divider: 'rgba(255, 255, 255, 0.08)',
    },
    gradients: darkGradients,
    functional: functionalGradients,
    customColors: {
      surface: brandColors.dark.surface,
      elevated: brandColors.dark.elevated,
      cardBg: brandColors.dark.surface,
      borderColor: 'rgba(255, 255, 255, 0.08)',
      borderColorLight: 'rgba(255, 255, 255, 0.12)',
      glowPrimary: `0 0 20px ${brandColors.primary.deepSafeBlue}40`,
      glowSecondary: `0 0 20px ${brandColors.primary.signalTeal}40`,
    },
    typography: {
      ...baseTypography,
      caption: {
        ...baseTypography.caption,
        color: brandColors.darkText.secondary,
      },
    },
    shape: baseShape,
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            scrollbarColor: `${brandColors.dark.elevated} ${brandColors.dark.primary}`,
            '&::-webkit-scrollbar': {
              width: 8,
              height: 8,
            },
            '&::-webkit-scrollbar-track': {
              background: brandColors.dark.primary,
            },
            '&::-webkit-scrollbar-thumb': {
              background: brandColors.dark.elevated,
              borderRadius: 4,
              '&:hover': {
                background: brandColors.primary.deepSafeBlue,
              },
            },
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            padding: '10px 20px',
            fontWeight: 600,
            transition: 'all 0.2s ease',
          },
          contained: {
            boxShadow: 'none',
            '&:hover': {
              boxShadow: `0 4px 12px ${brandColors.primary.deepSafeBlue}40`,
              transform: 'translateY(-1px)',
            },
          },
          containedPrimary: {
            background: darkGradients.blueDepth,
            '&:hover': {
              background: darkGradients.intelligenceBlue,
            },
          },
          outlined: {
            borderColor: 'rgba(255, 255, 255, 0.2)',
            '&:hover': {
              borderColor: brandColors.primary.signalTeal,
              backgroundColor: 'rgba(31, 182, 166, 0.08)',
            },
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            background: darkGradients.deepOcean,
            border: '1px solid rgba(255, 255, 255, 0.08)',
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.4)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s ease',
            '&:hover': {
              border: '1px solid rgba(255, 255, 255, 0.12)',
              boxShadow: `0 8px 32px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(31, 60, 136, 0.2)`,
              transform: 'translateY(-2px)',
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            backgroundImage: 'none',
          },
          elevation1: {
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.4)',
          },
        },
      },
      MuiTableHead: {
        styleOverrides: {
          root: {
            background: darkGradients.secureNavy,
            '& .MuiTableCell-head': {
              fontWeight: 600,
              fontSize: '0.75rem',
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              color: brandColors.darkText.secondary,
              borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
            },
          },
        },
      },
      MuiTableRow: {
        styleOverrides: {
          root: {
            transition: 'background 0.2s ease',
            '&:hover': {
              backgroundColor: 'rgba(31, 182, 166, 0.06)',
            },
          },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
            padding: '16px',
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            fontWeight: 600,
            fontSize: '0.75rem',
            borderRadius: 8,
          },
          filled: {
            background: 'rgba(255, 255, 255, 0.08)',
          },
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 500,
            fontSize: '0.9375rem',
          },
        },
      },
      MuiAlert: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            backdropFilter: 'blur(10px)',
          },
          standardError: {
            background: 'rgba(214, 69, 69, 0.15)',
            border: '1px solid rgba(214, 69, 69, 0.3)',
          },
          standardWarning: {
            background: 'rgba(245, 166, 35, 0.15)',
            border: '1px solid rgba(245, 166, 35, 0.3)',
          },
          standardSuccess: {
            background: 'rgba(58, 214, 163, 0.15)',
            border: '1px solid rgba(58, 214, 163, 0.3)',
          },
          standardInfo: {
            background: 'rgba(59, 201, 201, 0.15)',
            border: '1px solid rgba(59, 201, 201, 0.3)',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            background: darkGradients.header,
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.4)',
            backdropFilter: 'blur(10px)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: 8,
              '& fieldset': {
                borderColor: 'rgba(255, 255, 255, 0.12)',
              },
              '&:hover fieldset': {
                borderColor: 'rgba(255, 255, 255, 0.2)',
              },
              '&.Mui-focused fieldset': {
                borderColor: brandColors.primary.signalTeal,
              },
            },
          },
        },
      },
      MuiSelect: {
        styleOverrides: {
          root: {
            borderRadius: 8,
          },
        },
      },
      MuiMenu: {
        styleOverrides: {
          paper: {
            background: brandColors.dark.elevated,
            border: '1px solid rgba(255, 255, 255, 0.08)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
          },
        },
      },
      MuiPopover: {
        styleOverrides: {
          paper: {
            background: brandColors.dark.elevated,
            border: '1px solid rgba(255, 255, 255, 0.08)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
          },
        },
      },
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            background: brandColors.dark.elevated,
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: 8,
            fontSize: '0.75rem',
          },
        },
      },
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            borderRadius: 4,
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
          },
        },
      },
      MuiSkeleton: {
        styleOverrides: {
          root: {
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
          },
        },
      },
    },
  };

  return createTheme(darkThemeOptions);
};

// Create Light Theme
export const createLightTheme = (): Theme => {
  const lightThemeOptions: ThemeOptions = {
    palette: {
      mode: 'light',
      primary: {
        main: brandColors.primary.deepSafeBlue,
        light: '#3A6EDC',
        dark: '#152B5C',
        contrastText: '#FFFFFF',
      },
      secondary: {
        main: brandColors.primary.signalTeal,
        light: '#3BC9C9',
        dark: '#148F82',
        contrastText: '#FFFFFF',
      },
      error: {
        main: brandColors.statusLight.error,
        light: '#FF7B7B',
        dark: '#B53A3A',
      },
      warning: {
        main: brandColors.statusLight.warning,
        light: '#FFB74D',
        dark: '#C7850C',
      },
      success: {
        main: brandColors.statusLight.success,
        light: '#4ED4A6',
        dark: '#1F9B6C',
      },
      info: {
        main: brandColors.statusLight.info,
        light: '#4DCBCB',
        dark: '#148F82',
      },
      background: {
        default: brandColors.light.primary,
        paper: brandColors.light.surface,
      },
      text: {
        primary: brandColors.lightText.primary,
        secondary: brandColors.lightText.secondary,
        disabled: brandColors.lightText.muted,
      },
      divider: 'rgba(0, 0, 0, 0.08)',
    },
    gradients: lightGradients,
    functional: functionalGradients,
    customColors: {
      surface: brandColors.light.surface,
      elevated: brandColors.light.subtle,
      cardBg: brandColors.light.surface,
      borderColor: 'rgba(0, 0, 0, 0.08)',
      borderColorLight: 'rgba(0, 0, 0, 0.12)',
      glowPrimary: `0 0 20px ${brandColors.primary.deepSafeBlue}20`,
      glowSecondary: `0 0 20px ${brandColors.primary.signalTeal}20`,
    },
    typography: {
      ...baseTypography,
      caption: {
        ...baseTypography.caption,
        color: brandColors.lightText.secondary,
      },
    },
    shape: baseShape,
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            scrollbarColor: `${brandColors.light.subtle} ${brandColors.light.primary}`,
            '&::-webkit-scrollbar': {
              width: 8,
              height: 8,
            },
            '&::-webkit-scrollbar-track': {
              background: brandColors.light.primary,
            },
            '&::-webkit-scrollbar-thumb': {
              background: brandColors.lightText.muted,
              borderRadius: 4,
              '&:hover': {
                background: brandColors.lightText.secondary,
              },
            },
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            padding: '10px 20px',
            fontWeight: 600,
            transition: 'all 0.2s ease',
          },
          contained: {
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
            '&:hover': {
              boxShadow: '0 4px 16px rgba(31, 60, 136, 0.25)',
              transform: 'translateY(-1px)',
            },
          },
          outlined: {
            borderColor: 'rgba(0, 0, 0, 0.15)',
            '&:hover': {
              borderColor: brandColors.primary.deepSafeBlue,
              backgroundColor: 'rgba(31, 60, 136, 0.04)',
            },
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            background: lightGradients.blueGlass,
            border: '1px solid rgba(0, 0, 0, 0.06)',
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.06)',
            transition: 'all 0.3s ease',
            '&:hover': {
              border: '1px solid rgba(0, 0, 0, 0.1)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
              transform: 'translateY(-2px)',
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            backgroundImage: 'none',
          },
          elevation1: {
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
          },
        },
      },
      MuiTableHead: {
        styleOverrides: {
          root: {
            background: lightGradients.cloudSecure,
            '& .MuiTableCell-head': {
              fontWeight: 600,
              fontSize: '0.75rem',
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              color: brandColors.lightText.secondary,
              borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
            },
          },
        },
      },
      MuiTableRow: {
        styleOverrides: {
          root: {
            transition: 'background 0.2s ease',
            '&:hover': {
              backgroundColor: 'rgba(31, 60, 136, 0.03)',
            },
          },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            borderBottom: '1px solid rgba(0, 0, 0, 0.06)',
            padding: '16px',
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            fontWeight: 600,
            fontSize: '0.75rem',
            borderRadius: 8,
          },
          filled: {
            background: 'rgba(0, 0, 0, 0.06)',
          },
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 500,
            fontSize: '0.9375rem',
          },
        },
      },
      MuiAlert: {
        styleOverrides: {
          root: {
            borderRadius: 12,
          },
          standardError: {
            background: 'rgba(214, 69, 69, 0.08)',
            border: '1px solid rgba(214, 69, 69, 0.2)',
          },
          standardWarning: {
            background: 'rgba(245, 166, 35, 0.08)',
            border: '1px solid rgba(245, 166, 35, 0.2)',
          },
          standardSuccess: {
            background: 'rgba(45, 190, 139, 0.08)',
            border: '1px solid rgba(45, 190, 139, 0.2)',
          },
          standardInfo: {
            background: 'rgba(31, 182, 166, 0.08)',
            border: '1px solid rgba(31, 182, 166, 0.2)',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            background: lightGradients.header,
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
            borderBottom: '1px solid rgba(0, 0, 0, 0.06)',
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: 8,
              '& fieldset': {
                borderColor: 'rgba(0, 0, 0, 0.15)',
              },
              '&:hover fieldset': {
                borderColor: 'rgba(0, 0, 0, 0.25)',
              },
              '&.Mui-focused fieldset': {
                borderColor: brandColors.primary.deepSafeBlue,
              },
            },
          },
        },
      },
      MuiSelect: {
        styleOverrides: {
          root: {
            borderRadius: 8,
          },
        },
      },
      MuiMenu: {
        styleOverrides: {
          paper: {
            background: brandColors.light.surface,
            border: '1px solid rgba(0, 0, 0, 0.08)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          },
        },
      },
      MuiPopover: {
        styleOverrides: {
          paper: {
            background: brandColors.light.surface,
            border: '1px solid rgba(0, 0, 0, 0.08)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          },
        },
      },
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            background: brandColors.lightText.primary,
            color: brandColors.light.surface,
            borderRadius: 8,
            fontSize: '0.75rem',
          },
        },
      },
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            borderRadius: 4,
            backgroundColor: 'rgba(0, 0, 0, 0.08)',
          },
        },
      },
      MuiSkeleton: {
        styleOverrides: {
          root: {
            backgroundColor: 'rgba(0, 0, 0, 0.08)',
          },
        },
      },
    },
  };

  return createTheme(lightThemeOptions);
};

// Export default light theme for backwards compatibility
export const lightTheme = createLightTheme();
export const darkTheme = createDarkTheme();

export default lightTheme;
