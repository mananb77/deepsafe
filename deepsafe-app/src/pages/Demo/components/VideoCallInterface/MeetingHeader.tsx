import React from 'react';
import { Box, Typography, IconButton, Stack, Tooltip, useMediaQuery, useTheme } from '@mui/material';
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
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box
      sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: { xs: 48, sm: 56 },
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        px: { xs: 1, sm: 2 },
        backgroundColor: isDark ? 'rgba(0, 0, 0, 0.6)' : 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(8px)',
        zIndex: 10,
      }}
    >
      {/* Left - Meeting Info */}
      <Stack direction="row" alignItems="center" spacing={{ xs: 0.5, sm: 1.5 }}>
        <Typography
          variant="body1"
          sx={{
            color: '#fff',
            fontWeight: 500,
            fontSize: { xs: '0.875rem', sm: '1rem' },
            maxWidth: { xs: 120, sm: 'none' },
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {meetingTitle}
        </Typography>
        <Tooltip title="Meeting info" arrow>
          <IconButton size="small" sx={{ color: 'rgba(255, 255, 255, 0.7)', display: { xs: 'none', sm: 'flex' } }}>
            <InfoIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>

      {/* Right - Meeting Actions */}
      <Stack direction="row" alignItems="center" spacing={{ xs: 0.5, sm: 1 }}>
        {/* DeepSafe Badge */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.75,
            px: { xs: 1, sm: 1.5 },
            py: 0.5,
            borderRadius: '16px',
            backgroundColor: 'rgba(31, 182, 166, 0.2)',
            border: '1px solid rgba(31, 182, 166, 0.4)',
            mr: { xs: 0.5, sm: 1 },
          }}
        >
          <ShieldIcon
            sx={{
              fontSize: { xs: 14, sm: 16 },
              color: brandColors.primary.signalTeal,
            }}
          />
          {!isMobile && (
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
          )}
        </Box>

        <Tooltip title="Participants" arrow>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              px: { xs: 0.75, sm: 1 },
              py: 0.5,
              borderRadius: '16px',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
              cursor: 'pointer',
            }}
          >
            <PeopleIcon sx={{ fontSize: { xs: 16, sm: 18 }, color: 'rgba(255, 255, 255, 0.9)' }} />
            <Typography
              variant="body2"
              sx={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 500, fontSize: { xs: '0.8rem', sm: '0.875rem' } }}
            >
              {participantCount}
            </Typography>
          </Box>
        </Tooltip>

        <Tooltip title="Chat" arrow>
          <IconButton size="small" sx={{ color: 'rgba(255, 255, 255, 0.7)', display: { xs: 'none', sm: 'flex' } }}>
            <ChatIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>
    </Box>
  );
};

export default MeetingHeader;
