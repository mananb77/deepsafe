import React from 'react';
import { Box, IconButton, Tooltip, Stack, Typography, useMediaQuery, useTheme } from '@mui/material';
import {
  Mic as MicIcon,
  MicOff as MicOffIcon,
  Videocam as VideocamIcon,
  VideocamOff as VideocamOffIcon,
  PresentToAll as PresentIcon,
  MoreVert as MoreVertIcon,
  CallEnd as CallEndIcon,
  ClosedCaption as CaptionsIcon,
  EmojiEmotions as ReactionsIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';

interface ControlBarProps {
  isMuted?: boolean;
  isVideoOff?: boolean;
}

export const ControlBar: React.FC<ControlBarProps> = ({
  isMuted = false,
  isVideoOff = false,
}) => {
  const { isDark } = useThemeMode();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const ControlButton = ({
    icon,
    activeIcon,
    label,
    isActive = false,
    variant = 'default',
    hideOnMobile = false,
  }: {
    icon: React.ReactNode;
    activeIcon?: React.ReactNode;
    label: string;
    isActive?: boolean;
    variant?: 'default' | 'danger';
    hideOnMobile?: boolean;
  }) => {
    if (hideOnMobile && isMobile) return null;

    return (
      <Tooltip title={label} arrow>
        <IconButton
          sx={{
            width: { xs: 40, sm: 48 },
            height: { xs: 40, sm: 48 },
            backgroundColor:
              variant === 'danger'
                ? '#ea4335'
                : isActive
                  ? 'rgba(234, 67, 53, 0.9)'
                  : isDark
                    ? 'rgba(60, 64, 67, 0.95)'
                    : 'rgba(60, 64, 67, 0.8)',
            color: '#fff',
            '&:hover': {
              backgroundColor:
                variant === 'danger'
                  ? '#c5221f'
                  : isActive
                    ? 'rgba(234, 67, 53, 1)'
                    : 'rgba(60, 64, 67, 1)',
            },
            '& .MuiSvgIcon-root': {
              fontSize: { xs: 20, sm: 24 },
            },
          }}
        >
          {isActive && activeIcon ? activeIcon : icon}
        </IconButton>
      </Tooltip>
    );
  };

  return (
    <Box
      sx={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: { xs: 64, sm: 80 },
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: isDark ? 'rgba(32, 33, 36, 0.95)' : 'rgba(32, 33, 36, 0.9)',
        backdropFilter: 'blur(8px)',
        zIndex: 10,
        px: { xs: 1, sm: 2 },
      }}
    >
      {/* Time Display (Google Meet style) - hide on mobile */}
      <Box
        sx={{
          position: 'absolute',
          left: { xs: 8, sm: 24 },
          display: { xs: 'none', sm: 'flex' },
          alignItems: 'center',
          gap: 1,
        }}
      >
        <Typography
          variant="body2"
          sx={{
            color: 'rgba(255, 255, 255, 0.9)',
            fontWeight: 500,
            fontFamily: '"JetBrains Mono", monospace',
          }}
        >
          2:45
        </Typography>
        <Box
          sx={{
            width: 6,
            height: 6,
            borderRadius: '50%',
            backgroundColor: '#3AD6A3',
            animation: 'pulse 2s infinite',
            '@keyframes pulse': {
              '0%, 100%': { opacity: 1 },
              '50%': { opacity: 0.5 },
            },
          }}
        />
      </Box>

      {/* Center Controls */}
      <Stack direction="row" spacing={{ xs: 1, sm: 2 }} alignItems="center">
        <ControlButton
          icon={<MicIcon />}
          activeIcon={<MicOffIcon />}
          label={isMuted ? 'Unmute' : 'Mute'}
          isActive={isMuted}
        />
        <ControlButton
          icon={<VideocamIcon />}
          activeIcon={<VideocamOffIcon />}
          label={isVideoOff ? 'Turn on camera' : 'Turn off camera'}
          isActive={isVideoOff}
        />
        <ControlButton icon={<CaptionsIcon />} label="Turn on captions" hideOnMobile />
        <ControlButton icon={<ReactionsIcon />} label="Send a reaction" hideOnMobile />
        <ControlButton icon={<PresentIcon />} label="Present now" hideOnMobile />
        <ControlButton icon={<MoreVertIcon />} label="More options" />
        <Box sx={{ mx: { xs: 0.5, sm: 1 } }} />
        <ControlButton
          icon={<CallEndIcon />}
          label="Leave call"
          variant="danger"
        />
      </Stack>

      {/* Meeting ID (Google Meet style) - hide on mobile */}
      <Box
        sx={{
          position: 'absolute',
          right: { xs: 8, sm: 24 },
          display: { xs: 'none', sm: 'block' },
        }}
      >
        <Typography
          variant="caption"
          sx={{
            color: 'rgba(255, 255, 255, 0.6)',
            fontFamily: '"JetBrains Mono", monospace',
            fontSize: '0.7rem',
          }}
        >
          abc-defg-hij
        </Typography>
      </Box>
    </Box>
  );
};

export default ControlBar;
