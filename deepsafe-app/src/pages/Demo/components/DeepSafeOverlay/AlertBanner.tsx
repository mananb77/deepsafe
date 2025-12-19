import React from 'react';
import { Box, Typography, IconButton, Stack } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { brandColors } from '../../../../theme/colors';
import { useDemoContext } from '../../context/DemoContext';
import type { DemoAlert } from '../../types/demo.types';
import { alertBannerVariants } from '../../constants/animations';

const MotionBox = motion(Box);

interface AlertBannerItemProps {
  alert: DemoAlert;
  onClose: () => void;
}

const AlertBannerItem: React.FC<AlertBannerItemProps> = ({ alert, onClose }) => {

  const getAlertStyles = () => {
    switch (alert.riskLevel) {
      case 'critical':
        return {
          backgroundColor: 'rgba(214, 69, 69, 0.95)',
          borderColor: brandColors.statusDark.error,
          icon: <ErrorIcon sx={{ fontSize: 20 }} />,
        };
      case 'high':
        return {
          backgroundColor: 'rgba(255, 107, 107, 0.9)',
          borderColor: '#FF6B6B',
          icon: <ErrorIcon sx={{ fontSize: 20 }} />,
        };
      case 'medium':
        return {
          backgroundColor: 'rgba(245, 166, 35, 0.9)',
          borderColor: brandColors.statusDark.warning,
          icon: <WarningIcon sx={{ fontSize: 20 }} />,
        };
      default:
        return {
          backgroundColor: 'rgba(59, 201, 201, 0.9)',
          borderColor: brandColors.statusDark.info,
          icon: <InfoIcon sx={{ fontSize: 20 }} />,
        };
    }
  };

  const styles = getAlertStyles();

  return (
    <MotionBox
      id="alert-banner"
      variants={alertBannerVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      sx={{
        backgroundColor: styles.backgroundColor,
        backdropFilter: 'blur(8px)',
        borderRadius: '12px',
        border: `2px solid ${styles.borderColor}`,
        px: 2,
        py: 1.5,
        display: 'flex',
        alignItems: 'center',
        gap: 1.5,
        boxShadow: `0 8px 32px ${styles.borderColor}40`,
        maxWidth: 400,
      }}
    >
      <Box sx={{ color: '#fff', display: 'flex', alignItems: 'center' }}>
        {styles.icon}
      </Box>
      <Typography
        variant="body2"
        sx={{
          color: '#fff',
          fontWeight: 600,
          flex: 1,
          fontSize: '0.85rem',
        }}
      >
        {alert.message}
      </Typography>
      <IconButton
        size="small"
        onClick={onClose}
        sx={{
          color: 'rgba(255, 255, 255, 0.8)',
          p: 0.5,
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
          },
        }}
      >
        <CloseIcon sx={{ fontSize: 18 }} />
      </IconButton>
    </MotionBox>
  );
};

export const AlertBanner: React.FC = () => {
  const { state, dispatch } = useDemoContext();

  const handleClose = () => {
    dispatch({ type: 'CLEAR_ALERTS' });
  };

  return (
    <Box
      sx={{
        position: 'absolute',
        top: 72,
        left: 16,
        zIndex: 20,
      }}
    >
      <AnimatePresence mode="popLayout">
        <Stack spacing={1.5}>
          {state.activeAlerts.map((alert) => (
            <AlertBannerItem
              key={alert.id}
              alert={alert}
              onClose={handleClose}
            />
          ))}
        </Stack>
      </AnimatePresence>
    </Box>
  );
};

export default AlertBanner;
