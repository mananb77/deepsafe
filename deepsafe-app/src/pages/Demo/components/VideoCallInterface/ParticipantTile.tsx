import React from 'react';
import { Box, Typography, Avatar, Chip } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mic as MicIcon,
  Warning as WarningIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import type { DemoParticipant } from '../../types/demo.types';
import {
  participantTileVariants,
  detectionOverlayVariants,
} from '../../constants/animations';

const MotionBox = motion(Box);

interface ParticipantTileProps {
  participant: DemoParticipant;
  isLarge?: boolean;
  showDetectionOverlay?: boolean;
  showRemovalAnimation?: boolean;
  riskScore?: number;
}

export const ParticipantTile: React.FC<ParticipantTileProps> = ({
  participant,
  isLarge = false,
  showDetectionOverlay = false,
  showRemovalAnimation = false,
  riskScore = 0,
}) => {
  const { isDark } = useThemeMode();
  const isDeepSafeBot = participant.id === 'deepsafe-bot';

  // Get initials from name
  const initials = participant.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  // Avatar background color
  const avatarBgColor = isDeepSafeBot
    ? 'transparent'
    : participant.isAttacker
      ? brandColors.primary.deepSafeBlue
      : brandColors.primary.signalTeal;

  return (
    <AnimatePresence>
      {!showRemovalAnimation && (
        <MotionBox
          variants={participantTileVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          id={`participant-${participant.id}`}
          sx={{
            position: 'relative',
            borderRadius: '12px',
            overflow: 'hidden',
            backgroundColor: isDark ? '#1a1a2e' : '#2d3436',
            aspectRatio: isLarge ? '16/9' : '4/3',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            border: participant.isSpeaking
              ? `3px solid ${brandColors.primary.signalTeal}`
              : '3px solid transparent',
            transition: 'border-color 0.3s ease',
          }}
        >
          {/* Video Feed Placeholder (Avatar) */}
          <Avatar
            src={participant.avatar}
            sx={{
              width: isLarge ? 100 : 72,
              height: isLarge ? 100 : 72,
              backgroundColor: avatarBgColor,
              fontSize: isLarge ? '2.5rem' : '1.75rem',
              fontWeight: 600,
              border: isDeepSafeBot
                ? `3px solid ${brandColors.primary.signalTeal}`
                : 'none',
            }}
          >
            {isDeepSafeBot ? (
              <ShieldIcon sx={{ fontSize: isLarge ? 56 : 40, color: brandColors.primary.signalTeal }} />
            ) : (
              initials
            )}
          </Avatar>

          {/* Speaking Indicator Animation */}
          {participant.isSpeaking && !isDeepSafeBot && (
            <Box
              sx={{
                position: 'absolute',
                bottom: 44,
                display: 'flex',
                gap: 0.5,
              }}
            >
              {[0, 1, 2, 3].map((i) => (
                <Box
                  key={i}
                  sx={{
                    width: 4,
                    height: 16,
                    backgroundColor: brandColors.primary.signalTeal,
                    borderRadius: 2,
                    animation: `speaking ${0.5 + i * 0.1}s ease-in-out infinite alternate`,
                    '@keyframes speaking': {
                      '0%': { transform: 'scaleY(0.3)' },
                      '100%': { transform: 'scaleY(1)' },
                    },
                    animationDelay: `${i * 0.1}s`,
                  }}
                />
              ))}
            </Box>
          )}

          {/* Name Overlay */}
          <Box
            sx={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              px: 1.5,
              py: 1,
              background: 'linear-gradient(transparent, rgba(0, 0, 0, 0.8))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography
                variant="body2"
                sx={{
                  color: '#fff',
                  fontWeight: 500,
                  fontSize: isLarge ? '0.875rem' : '0.75rem',
                }}
              >
                {participant.name}
              </Typography>
              {!isDeepSafeBot && (
                <MicIcon
                  sx={{
                    fontSize: 14,
                    color: 'rgba(255, 255, 255, 0.7)',
                  }}
                />
              )}
            </Box>
          </Box>

          {/* Trust Badge */}
          {!isDeepSafeBot && (
            <Box
              id={`trust-badge-${participant.id.split('-')[0]}`}
              sx={{
                position: 'absolute',
                top: 8,
                left: 8,
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                px: 1,
                py: 0.25,
                borderRadius: '12px',
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                backdropFilter: 'blur(4px)',
              }}
            >
              <ShieldIcon
                sx={{
                  fontSize: 12,
                  color:
                    participant.trustScore >= 80
                      ? brandColors.statusDark.success
                      : participant.trustScore >= 50
                        ? brandColors.statusDark.warning
                        : brandColors.statusDark.error,
                }}
              />
              <Typography
                variant="caption"
                sx={{
                  color: '#fff',
                  fontSize: '0.65rem',
                  fontWeight: 600,
                }}
              >
                {participant.trustScore}%
              </Typography>
            </Box>
          )}

          {/* DeepSafe Bot Badge */}
          {isDeepSafeBot && (
            <Box
              sx={{
                position: 'absolute',
                top: 8,
                left: 8,
                px: 1,
                py: 0.25,
                borderRadius: '12px',
                backgroundColor: 'rgba(31, 182, 166, 0.2)',
                border: '1px solid rgba(31, 182, 166, 0.4)',
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  color: brandColors.primary.signalTeal,
                  fontSize: '0.6rem',
                  fontWeight: 600,
                  letterSpacing: '0.5px',
                }}
              >
                MONITORING
              </Typography>
            </Box>
          )}

          {/* Detection Overlay for Attacker */}
          <AnimatePresence>
            {showDetectionOverlay && participant.isAttacker && (
              <MotionBox
                id="detection-overlay"
                variants={detectionOverlayVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                sx={{
                  position: 'absolute',
                  inset: 0,
                  backgroundColor: 'rgba(214, 69, 69, 0.15)',
                  border: `3px solid ${brandColors.statusDark.error}`,
                  borderRadius: '12px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'flex-start',
                  pt: 1,
                }}
              >
                <Chip
                  icon={<WarningIcon sx={{ fontSize: 14 }} />}
                  label={`${riskScore}% RISK`}
                  size="small"
                  sx={{
                    backgroundColor: brandColors.statusDark.error,
                    color: '#fff',
                    fontWeight: 700,
                    fontSize: '0.7rem',
                    '& .MuiChip-icon': { color: '#fff' },
                    animation: 'pulse 2s infinite',
                    '@keyframes pulse': {
                      '0%, 100%': { boxShadow: '0 0 0 0 rgba(214, 69, 69, 0.5)' },
                      '50%': { boxShadow: '0 0 0 8px rgba(214, 69, 69, 0)' },
                    },
                  }}
                />

                {/* Scanning Lines Effect */}
                <Box
                  sx={{
                    position: 'absolute',
                    inset: 0,
                    overflow: 'hidden',
                    borderRadius: '12px',
                    pointerEvents: 'none',
                  }}
                >
                  <Box
                    sx={{
                      position: 'absolute',
                      left: 0,
                      right: 0,
                      height: 2,
                      background: `linear-gradient(90deg, transparent, ${brandColors.statusDark.error}, transparent)`,
                      animation: 'scan 2s linear infinite',
                      '@keyframes scan': {
                        '0%': { top: 0 },
                        '100%': { top: '100%' },
                      },
                    }}
                  />
                </Box>
              </MotionBox>
            )}
          </AnimatePresence>
        </MotionBox>
      )}
    </AnimatePresence>
  );
};

export default ParticipantTile;
