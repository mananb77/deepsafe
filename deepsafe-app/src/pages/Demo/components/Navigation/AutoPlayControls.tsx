import React from 'react';
import { Box, IconButton, Tooltip, ToggleButtonGroup, ToggleButton } from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
} from '@mui/icons-material';
import { useDemoContext } from '../../context/DemoContext';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import type { PlaybackSpeed } from '../../types/demo.types';

const AutoPlayControls: React.FC = () => {
  const { state, dispatch } = useDemoContext();
  const { isDark } = useThemeMode();
  const { isPlaying, playbackSpeed } = state;

  const handleSpeedChange = (_: React.MouseEvent<HTMLElement>, newSpeed: PlaybackSpeed | null) => {
    if (newSpeed) {
      dispatch({ type: 'SET_SPEED', speed: newSpeed });
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      {/* Play/Pause Button */}
      <Tooltip title={isPlaying ? 'Pause (Space)' : 'Auto-play (Space)'}>
        <IconButton
          onClick={() => dispatch({ type: 'TOGGLE_PLAY' })}
          sx={{
            color: isPlaying
              ? brandColors.primary.signalTeal
              : isDark
                ? brandColors.darkText.primary
                : brandColors.lightText.primary,
            backgroundColor: isPlaying
              ? isDark
                ? 'rgba(31, 182, 166, 0.15)'
                : 'rgba(31, 182, 166, 0.1)'
              : 'transparent',
            '&:hover': {
              backgroundColor: isDark
                ? 'rgba(31, 182, 166, 0.2)'
                : 'rgba(31, 182, 166, 0.15)',
            },
          }}
          aria-label={isPlaying ? 'Pause auto-play' : 'Start auto-play'}
        >
          {isPlaying ? <PauseIcon /> : <PlayIcon />}
        </IconButton>
      </Tooltip>

      {/* Speed Selector */}
      <ToggleButtonGroup
        value={playbackSpeed}
        exclusive
        onChange={handleSpeedChange}
        size="small"
        aria-label="Playback speed"
        sx={{
          '& .MuiToggleButton-root': {
            px: 1.5,
            py: 0.5,
            fontSize: '0.75rem',
            fontWeight: 500,
            border: `1px solid ${isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)'}`,
            color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
            '&.Mui-selected': {
              backgroundColor: isDark
                ? 'rgba(31, 182, 166, 0.15)'
                : 'rgba(31, 182, 166, 0.1)',
              color: brandColors.primary.signalTeal,
              borderColor: brandColors.primary.signalTeal,
              '&:hover': {
                backgroundColor: isDark
                  ? 'rgba(31, 182, 166, 0.2)'
                  : 'rgba(31, 182, 166, 0.15)',
              },
            },
            '&:hover': {
              backgroundColor: isDark
                ? 'rgba(255, 255, 255, 0.05)'
                : 'rgba(0, 0, 0, 0.04)',
            },
          },
        }}
      >
        <ToggleButton value="slow" aria-label="Slow speed (20s per step)">
          0.5x
        </ToggleButton>
        <ToggleButton value="normal" aria-label="Normal speed (12s per step)">
          1x
        </ToggleButton>
        <ToggleButton value="fast" aria-label="Fast speed (6s per step)">
          2x
        </ToggleButton>
      </ToggleButtonGroup>
    </Box>
  );
};

export default AutoPlayControls;
