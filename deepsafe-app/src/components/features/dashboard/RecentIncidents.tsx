import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Button,
  Divider,
  useTheme,
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useThemeMode } from '../../../context/ThemeContext';
import { brandColors } from '../../../theme/colors';
import type { RecentIncident } from '../../../types';

interface RecentIncidentsProps {
  incidents: RecentIncident[];
  maxItems?: number;
}

const getIncidentIcon = (incident: RecentIncident, isDark: boolean) => {
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  if (incident.riskScore >= 80) {
    return (
      <Box
        sx={{
          p: 1,
          borderRadius: 2,
          background: isDark
            ? 'rgba(214, 69, 69, 0.15)'
            : 'rgba(214, 69, 69, 0.1)',
        }}
      >
        <ErrorIcon sx={{ color: brandColors.primary.threatRed, fontSize: 24 }} />
      </Box>
    );
  }
  if (incident.riskScore >= 60) {
    return (
      <Box
        sx={{
          p: 1,
          borderRadius: 2,
          background: isDark
            ? 'rgba(255, 107, 107, 0.15)'
            : 'rgba(214, 69, 69, 0.08)',
        }}
      >
        <WarningIcon sx={{ color: statusColors.error, fontSize: 24 }} />
      </Box>
    );
  }
  return (
    <Box
      sx={{
        p: 1,
        borderRadius: 2,
        background: isDark
          ? 'rgba(58, 214, 163, 0.15)'
          : 'rgba(45, 190, 139, 0.1)',
      }}
    >
      <CheckCircleIcon sx={{ color: statusColors.success, fontSize: 24 }} />
    </Box>
  );
};

const getStatusChip = (status: RecentIncident['status'], isDark: boolean) => {
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  switch (status) {
    case 'resolved':
      return (
        <Chip
          label="Resolved"
          size="small"
          icon={<CheckCircleIcon sx={{ fontSize: 14 }} />}
          sx={{
            background: isDark
              ? 'linear-gradient(135deg, rgba(58, 214, 163, 0.15) 0%, rgba(45, 190, 139, 0.25) 100%)'
              : 'rgba(45, 190, 139, 0.1)',
            color: statusColors.success,
            fontWeight: 500,
            fontSize: '0.6875rem',
            border: `1px solid ${isDark ? 'rgba(58, 214, 163, 0.3)' : 'rgba(45, 190, 139, 0.2)'}`,
            '& .MuiChip-icon': { color: statusColors.success },
          }}
        />
      );
    case 'investigating':
      return (
        <Chip
          label="Investigating"
          size="small"
          sx={{
            background: isDark
              ? 'linear-gradient(135deg, rgba(59, 201, 201, 0.15) 0%, rgba(31, 182, 166, 0.25) 100%)'
              : 'rgba(31, 182, 166, 0.1)',
            color: statusColors.info,
            fontWeight: 500,
            fontSize: '0.6875rem',
            border: `1px solid ${isDark ? 'rgba(59, 201, 201, 0.3)' : 'rgba(31, 182, 166, 0.2)'}`,
          }}
        />
      );
    default:
      return (
        <Chip
          label="Pending"
          size="small"
          sx={{
            background: isDark
              ? 'linear-gradient(135deg, rgba(255, 200, 87, 0.15) 0%, rgba(245, 166, 35, 0.25) 100%)'
              : 'rgba(245, 166, 35, 0.1)',
            color: statusColors.warning,
            fontWeight: 500,
            fontSize: '0.6875rem',
            border: `1px solid ${isDark ? 'rgba(255, 200, 87, 0.3)' : 'rgba(245, 166, 35, 0.2)'}`,
          }}
        />
      );
  }
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 0,
  }).format(amount);
};

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};

export const RecentIncidents: React.FC<RecentIncidentsProps> = ({
  incidents,
  maxItems = 5,
}) => {
  const navigate = useNavigate();
  const theme = useTheme();
  const { isDark } = useThemeMode();
  const displayIncidents = incidents.slice(0, maxItems);
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  return (
    <Card
      sx={{
        height: '100%',
        background: isDark
          ? theme.gradients.deepOcean
          : theme.gradients.blueGlass,
      }}
    >
      <CardContent sx={{ p: 0 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            p: 2.5,
            pb: 2,
          }}
        >
          <Typography
            variant="h6"
            sx={{
              fontWeight: 600,
              fontFamily: '"Space Grotesk", sans-serif',
            }}
          >
            Recent High-Risk Incidents
          </Typography>
          <Button
            endIcon={<ArrowForwardIcon />}
            onClick={() => navigate('/meetings?filter=compromised')}
            sx={{
              color: brandColors.primary.signalTeal,
              '&:hover': {
                backgroundColor: isDark
                  ? 'rgba(31, 182, 166, 0.08)'
                  : 'rgba(31, 60, 136, 0.04)',
              },
            }}
          >
            View All
          </Button>
        </Box>

        <Box>
          {displayIncidents.map((incident, index) => (
            <React.Fragment key={incident.id}>
              {index > 0 && (
                <Divider
                  sx={{
                    borderColor: theme.customColors.borderColor,
                    mx: 2,
                  }}
                />
              )}
              <Box
                onClick={() => navigate(`/meetings/${incident.meetingId}`)}
                sx={{
                  p: 2,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    backgroundColor: isDark
                      ? 'rgba(31, 182, 166, 0.06)'
                      : 'rgba(31, 60, 136, 0.03)',
                  },
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: 2,
                  }}
                >
                  {getIncidentIcon(incident, isDark)}
                  <Box sx={{ flex: 1 }}>
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        mb: 0.5,
                      }}
                    >
                      <Typography
                        variant="subtitle2"
                        sx={{
                          fontWeight: 600,
                          fontFamily: '"JetBrains Mono", monospace',
                          fontSize: '0.8125rem',
                        }}
                      >
                        {incident.incidentCode}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {formatTime(incident.timestamp)}
                      </Typography>
                    </Box>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 1.5 }}
                    >
                      {incident.type}
                      {incident.amountProtected && (
                        <>
                          {' '}
                          &bull;{' '}
                          <Box
                            component="span"
                            sx={{ color: statusColors.success, fontWeight: 500 }}
                          >
                            {formatCurrency(incident.amountProtected)} protected
                          </Box>
                        </>
                      )}
                    </Typography>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                      }}
                    >
                      <Typography
                        variant="caption"
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5,
                        }}
                      >
                        Risk:{' '}
                        <Box
                          component="span"
                          sx={{
                            fontWeight: 700,
                            fontFamily: '"JetBrains Mono", monospace',
                            color:
                              incident.riskScore >= 80
                                ? brandColors.primary.threatRed
                                : incident.riskScore >= 60
                                  ? statusColors.error
                                  : 'inherit',
                          }}
                        >
                          {incident.riskScore}%
                        </Box>
                      </Typography>
                      {getStatusChip(incident.status, isDark)}
                    </Box>
                  </Box>
                </Box>
              </Box>
            </React.Fragment>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default RecentIncidents;
