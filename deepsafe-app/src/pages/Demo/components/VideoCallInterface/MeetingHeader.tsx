import React from 'react';
import { Box, Typography, IconButton, Stack, Tooltip } from '@mui/material';
import {
  Info as InfoIcon,
  PeopleAlt as PeopleIcon,
  Chat as ChatIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';

interface MeetingHeaderProps {
  meetingTitle: string;
  participantCount: number;
}

export const MeetingHeader: React.FC<MeetingHeaderProps> = ({
  meetingTitle,
  participantCount,
}) => {
  const { isDark } = useThemeMode();

  return (
    <Box
      sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: 56,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        px: 2,
        backgroundColor: isDark ? 'rgba(0, 0, 0, 0.6)' : 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(8px)',
        zIndex: 10,
      }}
    >
      {/* Left - Meeting Info */}
      <Stack direction="row" alignItems="center" spacing={1.5}>
        <Typography
          variant="body1"
          sx={{
            color: '#fff',
            fontWeight: 500,
          }}
        >
          {meetingTitle}
        </Typography>
        <Tooltip title="Meeting info" arrow>
          <IconButton size="small" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            <InfoIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>

      {/* Right - Meeting Actions */}
      <Stack direction="row" alignItems="center" spacing={1}>
        {/* DeepSafe Badge */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.75,
            px: 1.5,
            py: 0.5,
            borderRadius: '16px',
            backgroundColor: 'rgba(31, 182, 166, 0.2)',
            border: '1px solid rgba(31, 182, 166, 0.4)',
            mr: 1,
          }}
        >
          <ShieldIcon
            sx={{
              fontSize: 16,
              color: brandColors.primary.signalTeal,
            }}
          />
          <Typography
            variant="caption"
            sx={{
              color: brandColors.primary.signalTeal,
              fontWeight: 600,
              fontSize: '0.7rem',
            }}
          >
            PROTECTED
          </Typography>
        </Box>

        <Tooltip title="Participants" arrow>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              px: 1,
              py: 0.5,
              borderRadius: '16px',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
              cursor: 'pointer',
            }}
          >
            <PeopleIcon sx={{ fontSize: 18, color: 'rgba(255, 255, 255, 0.9)' }} />
            <Typography
              variant="body2"
              sx={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 500 }}
            >
              {participantCount}
            </Typography>
          </Box>
        </Tooltip>

        <Tooltip title="Chat" arrow>
          <IconButton size="small" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            <ChatIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>
    </Box>
  );
};

export default MeetingHeader;
