import React, { useRef, useEffect } from 'react';
import { Box, Typography, IconButton, Paper, Chip, Divider, useMediaQuery, useTheme } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronRight as ChevronRightIcon,
  ChevronLeft as ChevronLeftIcon,
  Shield as ShieldIcon,
  Warning as WarningIcon,
  Chat as ChatIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { useDemoContext } from '../../context/DemoContext';
import { useRiskAnimation } from '../../hooks';
import { TranscriptEntry } from '../TranscriptPanel/TranscriptEntry';

const MotionBox = motion(Box);
const MotionPaper = motion(Paper);

const PANEL_WIDTH = 320;

// Panel variants will be created dynamically based on screen size
const createPanelVariants = (width: string | number) => ({
  open: {
    width: width,
    opacity: 1,
    transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] as const },
  },
  closed: {
    width: 0,
    opacity: 0,
    transition: { duration: 0.2, ease: [0.4, 0, 1, 1] as const },
  },
});

export const RightSidePanel: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { isDark } = useThemeMode();
  const { state, dispatch, visibleTranscripts, currentStepConfig, riskLevel } = useDemoContext();
  const scrollRef = useRef<HTMLDivElement>(null);
  const animatedScore = useRiskAnimation(state.currentRiskScore);

  // Responsive panel width
  const panelWidth = isMobile ? '100%' : PANEL_WIDTH;

  // Only show during call screens
  const showPanel = currentStepConfig.component === 'call';

  // Auto-scroll to bottom when new transcripts appear
  useEffect(() => {
    if (scrollRef.current && state.transcriptExpanded) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [visibleTranscripts.length, state.transcriptExpanded]);

  const handleToggle = () => {
    dispatch({ type: 'TOGGLE_TRANSCRIPT' });
  };

  if (!showPanel) return null;

  // Risk meter colors
  const getRiskMeterColor = (): string => {
    switch (riskLevel) {
      case 'critical':
        return brandColors.statusDark.error;
      case 'high':
        return '#FF6B6B';
      case 'medium':
        return brandColors.statusDark.warning;
      default:
        return brandColors.statusDark.success;
    }
  };

  const getRiskLabel = (): string => {
    switch (riskLevel) {
      case 'critical':
        return 'CRITICAL';
      case 'high':
        return 'HIGH';
      case 'medium':
        return 'MEDIUM';
      default:
        return 'LOW';
    }
  };

  const riskColor = getRiskMeterColor();
  const showGlow = riskLevel === 'critical' || riskLevel === 'high';

  // Get latest alert
  const latestAlert = state.activeAlerts[state.activeAlerts.length - 1];

  return (
    <Box
      sx={{
        position: 'absolute',
        top: { xs: 48, sm: 56 }, // Below the MeetingHeader
        right: 0,
        bottom: { xs: 100, sm: 140 }, // Above control bar and navigation gradient
        left: isMobile && state.transcriptExpanded ? 0 : 'auto', // Full width on mobile when expanded
        zIndex: 15,
        display: 'flex',
        alignItems: 'stretch',
        pointerEvents: 'none',
      }}
    >
      {/* Toggle Button */}
      <Box
        sx={{
          display: isMobile && state.transcriptExpanded ? 'none' : 'flex',
          alignItems: 'flex-start',
          pt: 2, // Small padding from top
          pointerEvents: 'auto',
        }}
      >
        <IconButton
          onClick={handleToggle}
          sx={{
            backgroundColor: isDark
              ? 'rgba(0, 0, 0, 0.7)'
              : 'rgba(0, 0, 0, 0.6)',
            color: '#fff',
            borderRadius: '8px 0 0 8px',
            width: 32,
            height: 48,
            '&:hover': {
              backgroundColor: isDark
                ? 'rgba(0, 0, 0, 0.85)'
                : 'rgba(0, 0, 0, 0.75)',
            },
          }}
        >
          {state.transcriptExpanded ? (
            <ChevronRightIcon />
          ) : (
            <ChevronLeftIcon />
          )}
        </IconButton>
      </Box>

      {/* Panel Content */}
      <AnimatePresence>
        {state.transcriptExpanded && (
          <MotionPaper
            variants={createPanelVariants(panelWidth)}
            initial="closed"
            animate="open"
            exit="closed"
            elevation={0}
            sx={{
              height: '100%',
              backgroundColor: isDark
                ? 'rgba(11, 18, 32, 0.98)'
                : 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(16px)',
              borderLeft: isMobile ? 'none' : `1px solid ${
                isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
              }`,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              pointerEvents: 'auto',
            }}
          >
            {/* Top Section - Two Cards */}
            <Box sx={{ p: 1.5, display: 'flex', gap: 1.5 }}>
              {/* Risk Meter Card */}
              <Box
                id="risk-meter"
                sx={{
                  flex: 1,
                  p: 1.5,
                  borderRadius: '12px',
                  backgroundColor: isDark ? 'rgba(0, 0, 0, 0.4)' : 'rgba(0, 0, 0, 0.05)',
                  border: `1px solid ${
                    showGlow ? `${riskColor}50` : isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'
                  }`,
                  boxShadow: showGlow ? `0 0 12px ${riskColor}25` : 'none',
                  transition: 'all 0.3s ease',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, mb: 1 }}>
                  <ShieldIcon sx={{ fontSize: 14, color: brandColors.primary.signalTeal }} />
                  <Typography
                    variant="caption"
                    sx={{
                      color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.5)',
                      fontSize: '0.6rem',
                      fontWeight: 600,
                      letterSpacing: '0.5px',
                    }}
                  >
                    THREAT LEVEL
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.25, mb: 1 }}>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 700,
                      fontFamily: '"Space Grotesk", sans-serif',
                      color: riskColor,
                      lineHeight: 1,
                    }}
                  >
                    {Math.round(animatedScore)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: riskColor, fontWeight: 600, fontSize: '0.75rem' }}>
                    %
                  </Typography>
                </Box>
                <Chip
                  icon={riskLevel !== 'low' ? <WarningIcon sx={{ fontSize: 10 }} /> : undefined}
                  label={getRiskLabel()}
                  size="small"
                  sx={{
                    height: 18,
                    fontSize: '0.55rem',
                    fontWeight: 700,
                    backgroundColor: `${riskColor}20`,
                    color: riskColor,
                    border: `1px solid ${riskColor}40`,
                    '& .MuiChip-icon': { color: riskColor },
                    '& .MuiChip-label': { px: 0.75 },
                  }}
                />
                {/* Mini progress bar */}
                <Box
                  sx={{
                    mt: 1,
                    height: 3,
                    backgroundColor: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    borderRadius: 1.5,
                    overflow: 'hidden',
                  }}
                >
                  <MotionBox
                    animate={{ width: `${animatedScore}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                    sx={{
                      height: '100%',
                      backgroundColor: riskColor,
                      borderRadius: 1.5,
                    }}
                  />
                </Box>
              </Box>

              {/* Alert Summary Card */}
              <Box
                sx={{
                  flex: 1,
                  p: 1.5,
                  borderRadius: '12px',
                  backgroundColor: latestAlert
                    ? isDark ? 'rgba(214, 69, 69, 0.15)' : 'rgba(214, 69, 69, 0.1)'
                    : isDark ? 'rgba(0, 0, 0, 0.4)' : 'rgba(0, 0, 0, 0.05)',
                  border: `1px solid ${
                    latestAlert
                      ? `${brandColors.statusDark.error}40`
                      : isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'
                  }`,
                  transition: 'all 0.3s ease',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, mb: 1 }}>
                  <WarningIcon
                    sx={{
                      fontSize: 14,
                      color: latestAlert ? brandColors.statusDark.error : isDark ? 'rgba(255, 255, 255, 0.4)' : 'rgba(0, 0, 0, 0.3)',
                    }}
                  />
                  <Typography
                    variant="caption"
                    sx={{
                      color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.5)',
                      fontSize: '0.6rem',
                      fontWeight: 600,
                      letterSpacing: '0.5px',
                    }}
                  >
                    ALERTS
                  </Typography>
                </Box>
                {latestAlert ? (
                  <>
                    <Typography
                      variant="body2"
                      sx={{
                        color: isDark ? '#fff' : '#333',
                        fontSize: '0.7rem',
                        fontWeight: 500,
                        lineHeight: 1.3,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                    >
                      {latestAlert.message}
                    </Typography>
                    <Chip
                      label={`${state.activeAlerts.length} active`}
                      size="small"
                      sx={{
                        mt: 1,
                        height: 18,
                        fontSize: '0.55rem',
                        fontWeight: 600,
                        backgroundColor: `${brandColors.statusDark.error}30`,
                        color: brandColors.statusDark.error,
                        '& .MuiChip-label': { px: 0.75 },
                      }}
                    />
                  </>
                ) : (
                  <Typography
                    variant="body2"
                    sx={{
                      color: isDark ? 'rgba(255, 255, 255, 0.4)' : 'rgba(0, 0, 0, 0.4)',
                      fontSize: '0.7rem',
                    }}
                  >
                    No active alerts
                  </Typography>
                )}
              </Box>
            </Box>

            {/* View Risk Breakdown Button */}
            <Box sx={{ px: 1.5, pb: 1.5 }}>
              <Box
                component="button"
                onClick={() => dispatch({
                  type: 'OPEN_MODAL',
                  modal: {
                    type: 'riskBreakdown',
                    title: 'Risk Score Breakdown',
                    size: 'md',
                  },
                })}
                sx={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 1,
                  py: 1.25,
                  px: 2,
                  border: 'none',
                  borderRadius: '10px',
                  backgroundColor: brandColors.primary.signalTeal,
                  color: '#fff',
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  transition: 'all 0.2s ease',
                  boxShadow: `0 2px 8px ${brandColors.primary.signalTeal}40`,
                  '&:hover': {
                    backgroundColor: '#1AA396',
                    transform: 'translateY(-1px)',
                    boxShadow: `0 4px 12px ${brandColors.primary.signalTeal}50`,
                  },
                  '&:active': {
                    transform: 'translateY(0)',
                  },
                }}
              >
                <AnalyticsIcon sx={{ fontSize: 18 }} />
                View Risk Breakdown
              </Box>
            </Box>

            <Divider sx={{ borderColor: isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)' }} />

            {/* Transcript Header */}
            <Box
              sx={{
                px: 1.5,
                py: 1,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}
            >
              <ChatIcon sx={{ fontSize: 16, color: brandColors.primary.signalTeal }} />
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: 600,
                  fontSize: '0.8rem',
                  color: isDark ? '#fff' : brandColors.primary.deepSafeBlue,
                }}
              >
                Live Transcript
              </Typography>
              <Box
                sx={{
                  ml: 'auto',
                  px: 0.75,
                  py: 0.25,
                  borderRadius: '8px',
                  backgroundColor: 'rgba(31, 182, 166, 0.15)',
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: brandColors.primary.signalTeal,
                    fontWeight: 600,
                    fontSize: '0.55rem',
                  }}
                >
                  AI MONITORING
                </Typography>
              </Box>
              {/* Close button for mobile */}
              {isMobile && (
                <IconButton
                  onClick={handleToggle}
                  size="small"
                  sx={{
                    ml: 1,
                    color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.5)',
                  }}
                >
                  <ChevronRightIcon />
                </IconButton>
              )}
            </Box>

            {/* Transcript Entries */}
            <Box
              ref={scrollRef}
              sx={{
                flex: 1,
                overflowY: 'auto',
                overflowX: 'hidden',
                '&::-webkit-scrollbar': { width: 4 },
                '&::-webkit-scrollbar-track': { backgroundColor: 'transparent' },
                '&::-webkit-scrollbar-thumb': {
                  backgroundColor: isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)',
                  borderRadius: 2,
                },
              }}
            >
              {visibleTranscripts.length === 0 ? (
                <Box
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    color: isDark ? 'rgba(255, 255, 255, 0.4)' : 'rgba(0, 0, 0, 0.4)',
                  }}
                >
                  <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                    Waiting for conversation...
                  </Typography>
                </Box>
              ) : (
                <AnimatePresence mode="popLayout">
                  {visibleTranscripts.map((entry, index) => (
                    <React.Fragment key={entry.id}>
                      <TranscriptEntry entry={entry} index={index} compact />
                      {index < visibleTranscripts.length - 1 && (
                        <Divider
                          sx={{
                            mx: 1.5,
                            borderColor: isDark ? 'rgba(255, 255, 255, 0.04)' : 'rgba(0, 0, 0, 0.04)',
                          }}
                        />
                      )}
                    </React.Fragment>
                  ))}
                </AnimatePresence>
              )}
            </Box>

            {/* Footer */}
            <Box
              sx={{
                px: 1.5,
                py: 0.75,
                borderTop: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)'}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  color: isDark ? 'rgba(255, 255, 255, 0.4)' : 'rgba(0, 0, 0, 0.4)',
                  fontSize: '0.6rem',
                }}
              >
                {visibleTranscripts.length} messages
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: brandColors.primary.signalTeal,
                  fontSize: '0.6rem',
                  fontWeight: 500,
                }}
              >
                DeepSafe Active
              </Typography>
            </Box>
          </MotionPaper>
        )}
      </AnimatePresence>
    </Box>
  );
};

export default RightSidePanel;
