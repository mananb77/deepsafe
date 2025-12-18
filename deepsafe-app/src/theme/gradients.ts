// DeepSafe Gradient System - Based on official branding guidelines
// Gradients are a primary visual language for DeepSafe

import { brandColors } from './colors';

// Dark Mode Gradients
export const darkGradients = {
  // Foundational Gradients
  midnightCore: 'linear-gradient(180deg, #05070C 0%, #0B1220 100%)',
  secureNavy: 'linear-gradient(180deg, #0B1220 0%, #121C2E 100%)',
  deepOcean: 'linear-gradient(180deg, #121C2E 0%, #1A2740 100%)',
  blueDepth: 'linear-gradient(180deg, #1A2740 0%, #1F3C88 100%)',

  // Aliases for cross-mode compatibility
  cloudSecure: 'linear-gradient(180deg, #05070C 0%, #0B1220 100%)', // alias for midnightCore
  blueGlass: 'linear-gradient(180deg, #121C2E 0%, #1A2740 100%)', // alias for deepOcean
  executiveBlue: 'linear-gradient(180deg, #1A2740 0%, #1F3C88 100%)', // alias for blueDepth

  // Brand Signature Gradients
  signature: 'linear-gradient(180deg, #05070C 0%, #0B1220 50%, #1F3C88 100%)',
  trustFlow: 'linear-gradient(180deg, #0B1220 0%, #121C2E 50%, #1FB6A6 100%)',
  intelligenceBlue: 'linear-gradient(180deg, #1A2740 0%, #1F3C88 50%, #3A6EDC 100%)',

  // Header Gradient
  header: 'linear-gradient(90deg, #0B1220 0%, #1F3C88 100%)',

  // Card Gradients
  card: 'linear-gradient(180deg, #121C2E 0%, #1A2740 100%)',
  cardHover: 'linear-gradient(180deg, #1A2740 0%, #1F3C88 100%)',
  cardElevated: 'linear-gradient(135deg, #1A2740 0%, #1F3C88 100%)',

  // Subtle overlays
  overlay: 'linear-gradient(180deg, rgba(5, 7, 12, 0.8) 0%, rgba(11, 18, 32, 0.9) 100%)',
  glassOverlay: 'linear-gradient(180deg, rgba(18, 28, 46, 0.6) 0%, rgba(26, 39, 64, 0.8) 100%)',
};

// Light Mode Gradients (matching structure with dark gradients)
export const lightGradients = {
  // Foundational Gradients (mapped from dark equivalents)
  midnightCore: 'linear-gradient(180deg, #F7F9FC 0%, #EEF2F7 100%)', // cloudSecure equivalent
  secureNavy: 'linear-gradient(180deg, #EEF2F7 0%, #E6ECF5 100%)',
  deepOcean: 'linear-gradient(180deg, #FFFFFF 0%, #E6ECF5 100%)', // blueGlass equivalent
  blueDepth: 'linear-gradient(180deg, #E6ECF5 0%, #C7D4F5 100%)', // executiveBlue equivalent

  // Light-specific aliases
  cloudSecure: 'linear-gradient(180deg, #F7F9FC 0%, #EEF2F7 100%)',
  blueGlass: 'linear-gradient(180deg, #FFFFFF 0%, #E6ECF5 100%)',
  executiveBlue: 'linear-gradient(180deg, #E6ECF5 0%, #C7D4F5 100%)',

  // Brand Signature Gradients
  signature: 'linear-gradient(180deg, #F7F9FC 0%, #EEF2F7 50%, #C7D4F5 100%)',
  trustFlow: 'linear-gradient(180deg, #F7F9FC 0%, #E6ECF5 50%, #D4F5F2 100%)',
  intelligenceBlue: 'linear-gradient(180deg, #E6ECF5 0%, #C7D4F5 50%, #A8C4F5 100%)',

  // Header Gradient
  header: 'linear-gradient(90deg, #F7F9FC 0%, #E6ECF5 100%)',

  // Card Gradients
  card: 'linear-gradient(180deg, #FFFFFF 0%, #F7F9FC 100%)',
  cardHover: 'linear-gradient(180deg, #F7F9FC 0%, #E6ECF5 100%)',
  cardElevated: 'linear-gradient(135deg, #FFFFFF 0%, #E6ECF5 100%)',

  // Subtle overlays
  overlay: 'linear-gradient(180deg, rgba(247, 249, 252, 0.9) 0%, rgba(238, 242, 247, 0.95) 100%)',
  glassOverlay: 'linear-gradient(180deg, rgba(255, 255, 255, 0.7) 0%, rgba(247, 249, 252, 0.9) 100%)',
};

// Functional Gradients (same for both modes, used for status indicators)
export const functionalGradients = {
  info: 'linear-gradient(135deg, #1A2740 0%, #1FB6A6 100%)',
  success: 'linear-gradient(135deg, #0F3D2E 0%, #2DBE8B 100%)',
  warning: 'linear-gradient(135deg, #3A2B10 0%, #F5A623 100%)',
  critical: 'linear-gradient(135deg, #2A0F14 0%, #D64545 100%)',

  // Chart gradients
  confidenceMeter: 'linear-gradient(90deg, #1FB6A6 0%, #3AD6A3 100%)',
  riskScore: 'linear-gradient(90deg, #F5A623 0%, #D64545 100%)',
  neutralData: 'linear-gradient(90deg, #7F8CA8 0%, #B8C3D9 100%)',

  // Glow effects
  infoGlow: `0 0 20px ${brandColors.primary.signalTeal}40`,
  successGlow: `0 0 20px ${brandColors.statusDark.success}40`,
  warningGlow: `0 0 20px ${brandColors.primary.alertAmber}40`,
  criticalGlow: `0 0 20px ${brandColors.primary.threatRed}40`,
};

// Combined gradient system
export const gradients = {
  dark: darkGradients,
  light: lightGradients,
  functional: functionalGradients,
};

// Helper function to get gradient by mode
export const getGradient = (
  name: keyof typeof darkGradients | keyof typeof lightGradients,
  mode: 'dark' | 'light'
): string => {
  const gradientSet = mode === 'dark' ? darkGradients : lightGradients;
  return (gradientSet as Record<string, string>)[name] || '';
};

// Helper function to get functional gradient
export const getFunctionalGradient = (
  status: 'info' | 'success' | 'warning' | 'critical'
): string => {
  return functionalGradients[status];
};

// Helper to create gradient border (using pseudo-element approach)
export const gradientBorderStyles = (
  gradient: string,
  borderWidth = 1,
  borderRadius = 12
) => ({
  position: 'relative' as const,
  background: 'transparent',
  '&::before': {
    content: '""',
    position: 'absolute' as const,
    inset: 0,
    padding: borderWidth,
    borderRadius,
    background: gradient,
    mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
    maskComposite: 'xor',
    WebkitMaskComposite: 'xor',
    pointerEvents: 'none' as const,
  },
});

// Glass morphism effect helper
export const glassMorphism = (mode: 'dark' | 'light') => ({
  background: mode === 'dark'
    ? 'rgba(18, 28, 46, 0.7)'
    : 'rgba(255, 255, 255, 0.8)',
  backdropFilter: 'blur(10px)',
  WebkitBackdropFilter: 'blur(10px)',
  border: mode === 'dark'
    ? '1px solid rgba(255, 255, 255, 0.08)'
    : '1px solid rgba(0, 0, 0, 0.08)',
});

export default gradients;
