import React, { useRef, useEffect } from 'react';
import { Box, Typography, IconButton, Paper, Divider } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Chat as ChatIcon,
  ChevronRight as ChevronRightIcon,
  ChevronLeft as ChevronLeftIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { useDemoContext } from '../../context/DemoContext';
import { TranscriptEntry } from './TranscriptEntry';

const MotionPaper = motion(Paper);

const panelVariants = {
  open: {
    width: 360,
    opacity: 1,
    transition: { duration: 0.3, ease: [0, 0, 0.58, 1] as const },
  },
  closed: {
    width: 0,
    opacity: 0,
    transition: { duration: 0.2, ease: [0.42, 0, 1, 1] as const },
  },
};

export const TranscriptPanel: React.FC = () => {
  const { isDark } = useThemeMode();
  const { state, dispatch, visibleTranscripts, currentStepConfig } = useDemoContext();
  const scrollRef = useRef<HTMLDivElement>(null);

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

  return (
    <Box
      sx={{
        position: 'absolute',
        top: 56,
        right: 0,
        bottom: 80,
        zIndex: 15,
        display: 'flex',
        alignItems: 'stretch',
      }}
    >
      {/* Toggle Button */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          pr: state.transcriptExpanded ? 0 : 1,
        }}
      >
        <IconButton
          onClick={handleToggle}
          sx={{
            backgroundColor: isDark
              ? 'rgba(0, 0, 0, 0.6)'
              : 'rgba(0, 0, 0, 0.5)',
            color: '#fff',
            borderRadius: '8px 0 0 8px',
            '&:hover': {
              backgroundColor: isDark
                ? 'rgba(0, 0, 0, 0.8)'
                : 'rgba(0, 0, 0, 0.7)',
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
            variants={panelVariants}
            initial="closed"
            animate="open"
            exit="closed"
            elevation={0}
            sx={{
              height: '100%',
              backgroundColor: isDark
                ? 'rgba(11, 18, 32, 0.95)'
                : 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(12px)',
              borderLeft: `1px solid ${
                isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
              }`,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            {/* Header */}
            <Box
              sx={{
                px: 2,
                py: 1.5,
                borderBottom: `1px solid ${
                  isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'
                }`,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}
            >
              <ChatIcon
                sx={{
                  fontSize: 18,
                  color: brandColors.primary.signalTeal,
                }}
              />
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: 600,
                  color: isDark ? '#fff' : brandColors.primary.deepSafeBlue,
                }}
              >
                Live Transcript
              </Typography>
              <Box
                sx={{
                  ml: 'auto',
                  px: 1,
                  py: 0.25,
                  borderRadius: '10px',
                  backgroundColor: 'rgba(31, 182, 166, 0.15)',
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: brandColors.primary.signalTeal,
                    fontWeight: 600,
                    fontSize: '0.65rem',
                  }}
                >
                  AI MONITORING
                </Typography>
              </Box>
            </Box>

            {/* Transcript Entries */}
            <Box
              ref={scrollRef}
              sx={{
                flex: 1,
                overflowY: 'auto',
                overflowX: 'hidden',
                '&::-webkit-scrollbar': {
                  width: 6,
                },
                '&::-webkit-scrollbar-track': {
                  backgroundColor: 'transparent',
                },
                '&::-webkit-scrollbar-thumb': {
                  backgroundColor: isDark
                    ? 'rgba(255, 255, 255, 0.2)'
                    : 'rgba(0, 0, 0, 0.15)',
                  borderRadius: 3,
                },
              }}
            >
              {visibleTranscripts.length === 0 ? (
                <Box
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    color: isDark
                      ? 'rgba(255, 255, 255, 0.4)'
                      : 'rgba(0, 0, 0, 0.4)',
                  }}
                >
                  <Typography variant="body2">
                    Waiting for conversation...
                  </Typography>
                </Box>
              ) : (
                <AnimatePresence mode="popLayout">
                  {visibleTranscripts.map((entry, index) => (
                    <React.Fragment key={entry.id}>
                      <TranscriptEntry entry={entry} index={index} />
                      {index < visibleTranscripts.length - 1 && (
                        <Divider
                          sx={{
                            mx: 2,
                            borderColor: isDark
                              ? 'rgba(255, 255, 255, 0.05)'
                              : 'rgba(0, 0, 0, 0.05)',
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
                px: 2,
                py: 1,
                borderTop: `1px solid ${
                  isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'
                }`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  color: isDark
                    ? 'rgba(255, 255, 255, 0.4)'
                    : 'rgba(0, 0, 0, 0.4)',
                  fontSize: '0.65rem',
                }}
              >
                {visibleTranscripts.length} messages
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: brandColors.primary.signalTeal,
                  fontSize: '0.65rem',
                  fontWeight: 500,
                }}
              >
                DeepSafe Analysis Active
              </Typography>
            </Box>
          </MotionPaper>
        )}
      </AnimatePresence>
    </Box>
  );
};

export default TranscriptPanel;
