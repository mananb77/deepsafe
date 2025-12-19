import React from 'react';
import { Box } from '@mui/material';
import { motion } from 'framer-motion';
import { useThemeMode } from '../../../../context/ThemeContext';
import { useDemoContext } from '../../context/DemoContext';
import { MeetingHeader } from './MeetingHeader';
import { ParticipantGrid } from './ParticipantGrid';
import { ControlBar } from './ControlBar';
import { screenVariants } from '../../constants/animations';

const MotionBox = motion(Box);

interface VideoCallInterfaceProps {
  children?: React.ReactNode;
}

const PANEL_WIDTH = 320;

export const VideoCallInterface: React.FC<VideoCallInterfaceProps> = ({
  children,
}) => {
  const { isDark } = useThemeMode();
  const { participants, state } = useDemoContext();

  // Count visible participants (excluding removed attacker)
  const participantCount = participants.filter(
    (p) => !state.participantRemoved || !p.isAttacker
  ).length;

  return (
    <MotionBox
      variants={screenVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      sx={{
        position: 'relative',
        minHeight: '100vh',
        backgroundColor: isDark ? '#202124' : '#1a1a1a',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Meeting Header */}
      <MeetingHeader
        meetingTitle="Q4 Financial Review"
        participantCount={participantCount}
      />

      {/* Participant Grid - adjusts when side panel is open */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          transition: 'padding-right 0.3s ease',
          pr: state.transcriptExpanded ? `${PANEL_WIDTH + 40}px` : 0,
        }}
      >
        <ParticipantGrid
          participants={participants}
          riskScore={state.currentRiskScore}
        />
      </Box>

      {/* Control Bar */}
      <ControlBar />

      {/* Overlay Content (Verification Modal, Threat Overlay, RightSidePanel) */}
      {children}
    </MotionBox>
  );
};

export default VideoCallInterface;
