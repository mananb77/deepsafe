import React from 'react';
import { Box, Typography, IconButton, Paper } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { Close as CloseIcon } from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { useDemoContext } from '../../context/DemoContext';
import {
  modalBackdropVariants,
  modalContentVariants,
} from '../../constants/animations';

const MotionBox = motion(Box);
const MotionPaper = motion(Paper);

interface DemoModalProps {
  children: React.ReactNode;
}

export const DemoModal: React.FC<DemoModalProps> = ({ children }) => {
  const { isDark } = useThemeMode();
  const { state, dispatch } = useDemoContext();

  const handleClose = () => {
    dispatch({ type: 'CLOSE_MODAL' });
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  if (!state.activeModal) return null;

  const getModalWidth = () => {
    switch (state.activeModal?.size) {
      case 'sm':
        return 360;
      case 'lg':
        return 640;
      default:
        return 480;
    }
  };

  return (
    <AnimatePresence>
      <MotionBox
        variants={modalBackdropVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        onClick={handleBackdropClick}
        sx={{
          position: 'fixed',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 200,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          backdropFilter: 'blur(4px)',
          p: 2,
        }}
      >
        <MotionPaper
          variants={modalContentVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          elevation={0}
          sx={{
            width: '100%',
            maxWidth: getModalWidth(),
            maxHeight: '80vh',
            overflow: 'hidden',
            borderRadius: '20px',
            backgroundColor: isDark ? brandColors.dark.elevated : '#fff',
            border: `1px solid ${
              isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'
            }`,
            boxShadow: '0 24px 80px rgba(0, 0, 0, 0.4)',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Header */}
          <Box
            sx={{
              px: 3,
              py: 2,
              borderBottom: `1px solid ${
                isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'
              }`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                fontFamily: '"Space Grotesk", sans-serif',
                color: isDark ? '#fff' : brandColors.primary.deepSafeBlue,
              }}
            >
              {state.activeModal.title}
            </Typography>
            <IconButton
              onClick={handleClose}
              size="small"
              sx={{
                color: isDark
                  ? 'rgba(255, 255, 255, 0.5)'
                  : 'rgba(0, 0, 0, 0.5)',
                '&:hover': {
                  backgroundColor: isDark
                    ? 'rgba(255, 255, 255, 0.1)'
                    : 'rgba(0, 0, 0, 0.05)',
                },
              }}
            >
              <CloseIcon />
            </IconButton>
          </Box>

          {/* Content */}
          <Box
            sx={{
              flex: 1,
              overflowY: 'auto',
              p: 3,
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
            {children}
          </Box>
        </MotionPaper>
      </MotionBox>
    </AnimatePresence>
  );
};

export default DemoModal;
