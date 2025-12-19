import React from 'react';
import { Box, Grid } from '@mui/material';
import type { DemoParticipant } from '../../types/demo.types';
import { ParticipantTile } from './ParticipantTile';

interface ParticipantGridProps {
  participants: DemoParticipant[];
  riskScore: number;
}

export const ParticipantGrid: React.FC<ParticipantGridProps> = ({
  participants,
  riskScore,
}) => {
  // Filter out participants that should be removed
  const visibleParticipants = participants.filter(
    (p) => !p.showRemovalAnimation || !p.isAttacker
  );

  // Determine grid layout based on participant count
  const getGridSize = (count: number, index: number) => {
    if (count === 1) {
      return { xs: 12 };
    }
    if (count === 2) {
      return { xs: 12, sm: 6 };
    }
    if (count === 3) {
      // First participant takes full width on mobile, half on sm+
      // Bottom two split the row
      if (index === 0) {
        return { xs: 12, sm: 6, md: 4 };
      }
      return { xs: 6, sm: 6, md: 4 };
    }
    // 4+ participants: 2x2 grid
    return { xs: 6, md: 6 };
  };

  return (
    <Box
      sx={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 3,
        pt: 8, // Account for header
        pb: 18, // Account for control bar + navigation gradient
      }}
    >
      <Grid
        container
        spacing={2}
        sx={{
          maxWidth: 900,
          width: '100%',
          justifyContent: 'center',
        }}
      >
        {visibleParticipants.map((participant, index) => {
          const sizes = getGridSize(visibleParticipants.length, index);
          return (
            <Grid
              key={participant.id}
              size={{ xs: sizes.xs, sm: sizes.sm, md: sizes.md }}
            >
              <ParticipantTile
                participant={participant}
                isLarge={visibleParticipants.length <= 2}
                showDetectionOverlay={
                  participant.isAttacker &&
                  (participant.showDetectionOverlay || riskScore >= 61)
                }
                showRemovalAnimation={participant.showRemovalAnimation}
                riskScore={riskScore}
              />
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
};

export default ParticipantGrid;
