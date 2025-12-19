import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Stack, CircularProgress } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckCircle as CheckCircleIcon,
  Videocam as VideocamIcon,
  RecordVoiceOver as VoiceIcon,
  DeviceHub as DeviceIcon,
  Smartphone as PhoneIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { useDemoContext } from '../../context/DemoContext';
import { modalContentVariants, verificationStepVariants } from '../../constants/animations';

const MotionBox = motion(Box);
const MotionPaper = motion(Paper);

interface VerificationStep {
  id: number;
  icon: React.ReactNode;
  label: string;
  status: 'pending' | 'in_progress' | 'complete';
}

export const VerificationModal: React.FC = () => {
  const { isDark } = useThemeMode();
  const { state, dispatch } = useDemoContext();
  const [steps, setSteps] = useState<VerificationStep[]>([
    { id: 1, icon: <VideocamIcon />, label: 'Analyzing video authenticity', status: 'pending' },
    { id: 2, icon: <VoiceIcon />, label: 'Checking voice fingerprint', status: 'pending' },
    { id: 3, icon: <DeviceIcon />, label: 'Cross-referencing device data', status: 'pending' },
    { id: 4, icon: <PhoneIcon />, label: 'Contacting verified identity...', status: 'pending' },
  ]);
  const [smsResponse, setSmsResponse] = useState<string | null>(null);

  // Auto-progress through verification steps
  useEffect(() => {
    if (!state.verificationStep) return;

    const progressSteps = async () => {
      for (let i = 0; i < steps.length; i++) {
        await new Promise((resolve) => setTimeout(resolve, 1500));

        setSteps((prev) =>
          prev.map((step, idx) => ({
            ...step,
            status:
              idx < i + 1 ? 'complete' : idx === i + 1 ? 'in_progress' : 'pending',
          }))
        );

        // Show SMS response after all steps complete
        if (i === steps.length - 1) {
          await new Promise((resolve) => setTimeout(resolve, 1000));
          setSmsResponse(
            '"I\'m not in any meeting right now. This is not me." - David Mitchell (verified phone)'
          );
          await new Promise((resolve) => setTimeout(resolve, 2000));
          dispatch({ type: 'CONFIRM_THREAT' });
        }
      }
    };

    // Start first step immediately
    setSteps((prev) =>
      prev.map((step, idx) => ({
        ...step,
        status: idx === 0 ? 'in_progress' : 'pending',
      }))
    );

    progressSteps();
  }, [state.verificationStep]);

  if (!state.verificationStep) return null;

  return (
    <AnimatePresence>
      <Box
        id="verification-modal"
        sx={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(4px)',
        }}
      >
        <MotionPaper
          variants={modalContentVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          elevation={0}
          sx={{
            width: 420,
            p: 3,
            borderRadius: '20px',
            backgroundColor: isDark ? brandColors.dark.elevated : '#fff',
            border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'}`,
            boxShadow: '0 24px 80px rgba(0, 0, 0, 0.4)',
          }}
        >
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Box
              sx={{
                width: 56,
                height: 56,
                borderRadius: '14px',
                backgroundColor: 'rgba(31, 182, 166, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mx: 'auto',
                mb: 2,
              }}
            >
              <ShieldIcon sx={{ fontSize: 32, color: brandColors.primary.signalTeal }} />
            </Box>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                color: isDark ? '#fff' : brandColors.primary.deepSafeBlue,
                fontFamily: '"Space Grotesk", sans-serif',
              }}
            >
              Identity Verification
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)',
                mt: 0.5,
              }}
            >
              Verifying participant "David Mitchell"
            </Typography>
          </Box>

          {/* Verification Steps */}
          <Stack spacing={2} sx={{ mb: 3 }}>
            {steps.map((step) => (
              <MotionBox
                key={step.id}
                id={`verification-step-${step.id}`}
                variants={verificationStepVariants}
                initial="initial"
                animate={step.status === 'complete' ? 'complete' : 'animate'}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  opacity: step.status === 'pending' ? 0.4 : 1,
                  transition: 'opacity 0.3s ease',
                }}
              >
                {/* Status Icon */}
                <Box
                  sx={{
                    width: 32,
                    height: 32,
                    borderRadius: '8px',
                    backgroundColor:
                      step.status === 'complete'
                        ? 'rgba(58, 214, 163, 0.15)'
                        : step.status === 'in_progress'
                          ? 'rgba(31, 182, 166, 0.15)'
                          : isDark
                            ? 'rgba(255, 255, 255, 0.05)'
                            : 'rgba(0, 0, 0, 0.04)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {step.status === 'complete' ? (
                    <CheckCircleIcon
                      sx={{ fontSize: 18, color: brandColors.statusDark.success }}
                    />
                  ) : step.status === 'in_progress' ? (
                    <CircularProgress
                      size={16}
                      sx={{ color: brandColors.primary.signalTeal }}
                    />
                  ) : (
                    <Box
                      sx={{
                        color: isDark
                          ? 'rgba(255, 255, 255, 0.3)'
                          : 'rgba(0, 0, 0, 0.3)',
                        display: 'flex',
                        '& svg': { fontSize: 16 },
                      }}
                    >
                      {step.icon}
                    </Box>
                  )}
                </Box>

                {/* Label */}
                <Typography
                  variant="body2"
                  sx={{
                    color:
                      step.status === 'complete'
                        ? brandColors.statusDark.success
                        : step.status === 'in_progress'
                          ? isDark
                            ? '#fff'
                            : '#333'
                          : isDark
                            ? 'rgba(255, 255, 255, 0.4)'
                            : 'rgba(0, 0, 0, 0.4)',
                    fontWeight: step.status === 'in_progress' ? 500 : 400,
                    transition: 'color 0.3s ease',
                  }}
                >
                  {step.status === 'complete' ? '✓ ' : ''}
                  {step.label}
                </Typography>
              </MotionBox>
            ))}
          </Stack>

          {/* SMS Response */}
          <AnimatePresence>
            {smsResponse && (
              <MotionBox
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                sx={{
                  p: 2,
                  borderRadius: '12px',
                  backgroundColor: 'rgba(214, 69, 69, 0.1)',
                  border: `1px solid ${brandColors.statusDark.error}`,
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: brandColors.statusDark.error,
                    fontWeight: 600,
                    display: 'block',
                    mb: 0.5,
                  }}
                >
                  SMS RESPONSE RECEIVED
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: isDark ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.8)',
                    fontStyle: 'italic',
                  }}
                >
                  {smsResponse}
                </Typography>
              </MotionBox>
            )}
          </AnimatePresence>
        </MotionPaper>
      </Box>
    </AnimatePresence>
  );
};

export default VerificationModal;
