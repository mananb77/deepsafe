import React, { useEffect } from 'react';
import { Box } from '@mui/material';
import { AnimatePresence } from 'framer-motion';
import { useDemoContext } from './context/DemoContext';
import { useAutoPlay, useKeyboardNavigation } from './hooks';

// Screen Components
import {
  WelcomeScreen,
  LobbyScreen,
  IncidentReportScreen,
  SuccessScreen,
} from './components/Screens';
import { VideoCallInterface } from './components/VideoCallInterface';
import { DeepSafeOverlay, RightSidePanel } from './components/DeepSafeOverlay';
import { StepNavigation } from './components/Navigation';
import { HotspotManager } from './components/Hotspots';
import { ModalPortal } from './components/Modals';

interface DemoPageProps {
  standalone?: boolean;
}

export const DemoPage: React.FC<DemoPageProps> = ({ standalone = false }) => {
  const { currentStepConfig, state } = useDemoContext();

  // Initialize auto-play hook
  useAutoPlay();

  // Initialize keyboard navigation
  const shortcuts = useKeyboardNavigation();

  // Log keyboard shortcuts on mount (for dev/demo purposes)
  useEffect(() => {
    if (standalone) {
      console.log('Keyboard shortcuts available:', shortcuts);
    }
  }, [standalone, shortcuts]);

  // Render the appropriate screen based on current step
  const renderScreen = () => {
    switch (currentStepConfig.component) {
      case 'welcome':
        return <WelcomeScreen />;

      case 'lobby':
        return <LobbyScreen />;

      case 'call':
        return (
          <VideoCallInterface>
            <DeepSafeOverlay />
            <RightSidePanel />
          </VideoCallInterface>
        );

      case 'report':
        return <IncidentReportScreen />;

      case 'success':
        return <SuccessScreen />;

      default:
        return <WelcomeScreen />;
    }
  };

  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: '100vh',
        width: '100%',
        overflow: 'hidden',
      }}
    >
      {/* Main Content */}
      <AnimatePresence mode="wait">
        <Box key={state.currentStep}>{renderScreen()}</Box>
      </AnimatePresence>

      {/* Navigation - Fixed at bottom */}
      <StepNavigation />

      {/* Hotspots - Positioned dynamically */}
      <HotspotManager />

      {/* Modal Portal - For all modal content */}
      <ModalPortal />
    </Box>
  );
};

export default DemoPage;
