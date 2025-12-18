// DeepSafe Brand Colors - Based on official branding guidelines

export const brandColors = {
  // Core Brand Colors
  primary: {
    deepSafeBlue: '#1F3C88',
    signalTeal: '#1FB6A6',
    alertAmber: '#F5A623',
    threatRed: '#D64545',
  },

  // Dark Mode Backgrounds
  dark: {
    deepest: '#05070C',
    primary: '#0B1220',
    surface: '#121C2E',
    elevated: '#1A2740',
  },

  // Dark Mode Text
  darkText: {
    primary: '#E6ECF5',
    secondary: '#B8C3D9',
    muted: '#7F8CA8',
  },

  // Light Mode Backgrounds
  light: {
    primary: '#F7F9FC',
    surface: '#FFFFFF',
    subtle: '#EEF2F7',
  },

  // Light Mode Text
  lightText: {
    primary: '#0B1B3A',
    secondary: '#4A5D73',
    muted: '#7B8CA5',
  },

  // Status Colors - Dark Mode
  statusDark: {
    success: '#3AD6A3',
    warning: '#FFC857',
    error: '#FF6B6B',
    info: '#3BC9C9',
  },

  // Status Colors - Light Mode
  statusLight: {
    success: '#2DBE8B',
    warning: '#F5A623',
    error: '#D64545',
    info: '#1FB6A6',
  },
};

// Theme-aware color system for backwards compatibility
export const colors = {
  // Primary - DeepSafe Blue
  primary: {
    main: brandColors.primary.deepSafeBlue,
    light: '#3A6EDC',
    dark: '#152B5C',
    contrastText: '#FFFFFF',
  },

  // Secondary - Signal Teal
  secondary: {
    main: brandColors.primary.signalTeal,
    light: '#3BC9C9',
    dark: '#148F82',
    contrastText: '#FFFFFF',
  },

  // Background Colors (for light theme - legacy support)
  background: {
    default: brandColors.light.primary,
    paper: brandColors.light.surface,
    header: `linear-gradient(90deg, ${brandColors.dark.primary} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
  },

  // Table Colors
  table: {
    headerBg: brandColors.light.subtle,
    rowHover: 'rgba(31, 60, 136, 0.04)',
    border: 'rgba(0, 0, 0, 0.08)',
  },

  // Risk Indicator Colors
  risk: {
    low: brandColors.statusLight.success,
    lowBg: 'rgba(45, 190, 139, 0.1)',
    lowLight: 'rgba(45, 190, 139, 0.2)',
    medium: brandColors.statusLight.warning,
    mediumBg: 'rgba(245, 166, 35, 0.1)',
    mediumLight: 'rgba(245, 166, 35, 0.2)',
    high: brandColors.statusLight.error,
    highBg: 'rgba(214, 69, 69, 0.1)',
    highLight: 'rgba(214, 69, 69, 0.2)',
    critical: brandColors.primary.threatRed,
    criticalBg: 'rgba(214, 69, 69, 0.15)',
  },

  // Trust Badge Colors
  trust: {
    verified: brandColors.statusLight.success,
    partial: brandColors.statusLight.warning,
    highRisk: brandColors.statusLight.error,
    external: brandColors.lightText.muted,
  },

  // Alert/Warning Colors
  alert: {
    info: brandColors.statusLight.info,
    warning: brandColors.statusLight.warning,
    error: brandColors.statusLight.error,
    success: brandColors.statusLight.success,
  },

  // Text Colors
  text: {
    primary: brandColors.lightText.primary,
    secondary: brandColors.lightText.secondary,
    disabled: brandColors.lightText.muted,
    onPrimary: '#FFFFFF',
    onDark: '#FFFFFF',
  },

  // Accent Colors
  accent: {
    blacklist: brandColors.primary.deepSafeBlue,
    statNumbers: brandColors.primary.signalTeal,
    link: brandColors.primary.deepSafeBlue,
  },

  // Status Colors
  status: {
    active: brandColors.statusLight.success,
    pending: brandColors.statusLight.warning,
    resolved: brandColors.statusLight.success,
    investigating: brandColors.statusLight.info,
  },
};

// Risk score to category mapping
export const getRiskCategory = (score: number): 'low' | 'medium' | 'high' | 'critical' => {
  if (score >= 86) return 'critical';
  if (score >= 61) return 'high';
  if (score >= 31) return 'medium';
  return 'low';
};

// Get color for risk score (theme-aware)
export const getRiskColor = (score: number, isDark = false): string => {
  const category = getRiskCategory(score);
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  switch (category) {
    case 'critical':
      return brandColors.primary.threatRed;
    case 'high':
      return statusColors.error;
    case 'medium':
      return statusColors.warning;
    case 'low':
      return statusColors.success;
    default:
      return statusColors.success;
  }
};

// Get background color for risk score (theme-aware)
export const getRiskBgColor = (score: number, isDark = false): string => {
  const category = getRiskCategory(score);
  const alpha = isDark ? 0.2 : 0.1;

  switch (category) {
    case 'critical':
      return `rgba(214, 69, 69, ${alpha + 0.05})`;
    case 'high':
      return `rgba(214, 69, 69, ${alpha})`;
    case 'medium':
      return `rgba(245, 166, 35, ${alpha})`;
    case 'low':
      return `rgba(45, 190, 139, ${alpha})`;
    default:
      return `rgba(45, 190, 139, ${alpha})`;
  }
};

export default colors;
