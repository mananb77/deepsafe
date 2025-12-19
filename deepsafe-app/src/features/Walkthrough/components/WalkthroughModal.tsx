import React from 'react';
import { Box, Typography, IconButton } from '@mui/material';
import {
  Close as CloseIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { brandColors } from '../../../theme/colors';
import { useThemeMode } from '../../../context/ThemeContext';
import { useWalkthroughContext } from '../context/WalkthroughContext';
import { modalBackdropVariants, modalContentVariants } from '../constants/animations';

const MotionBox = motion.create(Box);

export const WalkthroughModal: React.FC = () => {
  const { isDark } = useThemeMode();
  const { state, dispatch } = useWalkthroughContext();

  const handleClose = () => {
    dispatch({ type: 'CLOSE_MODAL' });
  };

  const modal = state.activeModal;

  return (
    <AnimatePresence>
      {modal && (
        <MotionBox
          variants={modalBackdropVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          onClick={handleClose}
          sx={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1500,
            p: 2,
          }}
        >
          <MotionBox
            variants={modalContentVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            onClick={(e) => e.stopPropagation()}
            sx={{
              width: '100%',
              maxWidth: 480,
              backgroundColor: isDark ? brandColors.dark.elevated : '#fff',
              borderRadius: 3,
              overflow: 'hidden',
              boxShadow: isDark
                ? '0 16px 48px rgba(0, 0, 0, 0.5)'
                : '0 16px 48px rgba(0, 0, 0, 0.2)',
            }}
          >
            {/* Header */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                p: 3,
                pb: 0,
              }}
            >
              <Typography
                variant="h5"
                sx={{
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 700,
                  color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                  pr: 2,
                }}
              >
                {modal.title}
              </Typography>
              <IconButton
                onClick={handleClose}
                size="small"
                sx={{
                  color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                  '&:hover': {
                    backgroundColor: isDark
                      ? 'rgba(255, 255, 255, 0.05)'
                      : 'rgba(0, 0, 0, 0.05)',
                  },
                }}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>

            {/* Content */}
            <Box sx={{ p: 3 }}>
              <Typography
                sx={{
                  color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                  lineHeight: 1.7,
                  mb: modal.features ? 3 : 0,
                }}
              >
                {modal.description}
              </Typography>

              {/* Features list */}
              {modal.features && modal.features.length > 0 && (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {modal.features.map((feature, index) => (
                    <Box
                      key={index}
                      sx={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: 1.5,
                      }}
                    >
                      <CheckIcon
                        sx={{
                          fontSize: 18,
                          color: brandColors.primary.signalTeal,
                          mt: 0.3,
                        }}
                      />
                      <Typography
                        variant="body2"
                        sx={{
                          color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                        }}
                      >
                        {feature}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </Box>

            {/* Footer hint */}
            <Box
              sx={{
                px: 3,
                py: 2,
                backgroundColor: isDark
                  ? 'rgba(255, 255, 255, 0.03)'
                  : 'rgba(0, 0, 0, 0.02)',
                borderTop: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'}`,
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                }}
              >
                Press Escape or click outside to close
              </Typography>
            </Box>
          </MotionBox>
        </MotionBox>
      )}
    </AnimatePresence>
  );
};

export default WalkthroughModal;
