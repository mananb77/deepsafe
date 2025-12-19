import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
  Alert,
  AlertTitle,
  LinearProgress,
  IconButton,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Warning as WarningIcon,
  Security as SecurityIcon,
  Block as BlockIcon,
  CheckCircle as VerifiedIcon,
  LocationOn as LocationIcon,
  Devices as DevicesIcon,
  Schedule as ScheduleIcon,
  Email as EmailIcon,
  Business as DepartmentIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { useThemeMode } from '../../context/ThemeContext';
import { TrustBadge, RiskIndicator } from '../../components/common';
import { brandColors } from '../../theme/colors';
import { getParticipantById } from '../../data';
import type { ParticipantStatus } from '../../types';

const getStatusChip = (status: ParticipantStatus, isDark: boolean) => {
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  switch (status) {
    case 'blacklisted':
      return (
        <Chip
          label="BLACKLISTED"
          sx={{
            background: `linear-gradient(135deg, ${brandColors.primary.threatRed} 0%, #8B2525 100%)`,
            color: 'white',
            fontWeight: 700,
            fontSize: '0.875rem',
            px: 2,
            py: 0.5,
          }}
        />
      );
    case 'verified':
      return (
        <Chip
          icon={<VerifiedIcon sx={{ color: `${statusColors.success} !important` }} />}
          label="VERIFIED"
          sx={{
            background: isDark
              ? 'linear-gradient(135deg, rgba(58, 214, 163, 0.2) 0%, rgba(45, 190, 139, 0.3) 100%)'
              : 'rgba(45, 190, 139, 0.15)',
            color: statusColors.success,
            fontWeight: 700,
            fontSize: '0.875rem',
            px: 2,
            border: `1px solid ${isDark ? 'rgba(58, 214, 163, 0.3)' : 'rgba(45, 190, 139, 0.3)'}`,
          }}
        />
      );
    case 'flagged':
      return (
        <Chip
          icon={<WarningIcon sx={{ color: `${statusColors.error} !important` }} />}
          label="FLAGGED"
          sx={{
            background: isDark
              ? 'linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(214, 69, 69, 0.3) 100%)'
              : 'rgba(214, 69, 69, 0.1)',
            color: statusColors.error,
            fontWeight: 700,
            fontSize: '0.875rem',
            px: 2,
            border: `1px solid ${isDark ? 'rgba(255, 107, 107, 0.3)' : 'rgba(214, 69, 69, 0.3)'}`,
          }}
        />
      );
    case 'external':
      return (
        <Chip
          label="EXTERNAL"
          sx={{
            background: isDark
              ? 'rgba(255, 255, 255, 0.1)'
              : 'rgba(0, 0, 0, 0.08)',
            color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
            fontWeight: 700,
            fontSize: '0.875rem',
            px: 2,
            border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.12)'}`,
          }}
        />
      );
    case 'guest':
    default:
      return (
        <Chip
          label="GUEST"
          sx={{
            background: isDark
              ? 'linear-gradient(135deg, rgba(255, 200, 87, 0.2) 0%, rgba(245, 166, 35, 0.3) 100%)'
              : 'rgba(245, 166, 35, 0.15)',
            color: statusColors.warning,
            fontWeight: 700,
            fontSize: '0.875rem',
            px: 2,
            border: `1px solid ${isDark ? 'rgba(255, 200, 87, 0.3)' : 'rgba(245, 166, 35, 0.3)'}`,
          }}
        />
      );
  }
};

export const ParticipantProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const { isDark } = useThemeMode();
  const { participantId } = useParams<{ participantId: string }>();

  const participant = participantId ? getParticipantById(participantId) : undefined;
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  if (!participant) {
    return (
      <Box>
        <Button
          startIcon={<BackIcon />}
          onClick={() => navigate('/app/participants')}
          sx={{
            mb: 2,
            color: brandColors.primary.signalTeal,
            '&:hover': {
              backgroundColor: isDark
                ? 'rgba(31, 182, 166, 0.08)'
                : 'rgba(31, 60, 136, 0.04)',
            },
          }}
        >
          Back to Participants
        </Button>
        <Alert
          severity="error"
          sx={{
            background: isDark
              ? 'linear-gradient(135deg, rgba(214, 69, 69, 0.15) 0%, rgba(139, 37, 37, 0.2) 100%)'
              : 'rgba(214, 69, 69, 0.1)',
            border: `1px solid ${brandColors.primary.threatRed}`,
          }}
        >
          <AlertTitle>Participant Not Found</AlertTitle>
          The requested participant could not be found.
        </Alert>
      </Box>
    );
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatShortDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <Box>
      {/* Back Button */}
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate('/app/participants')}
        sx={{
          mb: 2,
          color: brandColors.primary.signalTeal,
          '&:hover': {
            backgroundColor: isDark
              ? 'rgba(31, 182, 166, 0.08)'
              : 'rgba(31, 60, 136, 0.04)',
          },
        }}
      >
        Back to Participants
      </Button>

      {/* Blacklist Alert */}
      {participant.status === 'blacklisted' && (
        <Alert
          severity="error"
          icon={<BlockIcon />}
          sx={{
            mb: 3,
            background: isDark
              ? 'linear-gradient(135deg, rgba(214, 69, 69, 0.15) 0%, rgba(139, 37, 37, 0.2) 100%)'
              : 'rgba(214, 69, 69, 0.08)',
            border: `1px solid ${brandColors.primary.threatRed}`,
            '& .MuiAlert-icon': { color: brandColors.primary.threatRed },
          }}
        >
          <AlertTitle sx={{ fontWeight: 700 }}>User Blacklisted</AlertTitle>
          This user has been blacklisted due to fraudulent activity and cannot join any company meetings.
          {participant.blacklistDetails?.blacklistedAt && (
            <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
              Blacklisted on: {formatDate(participant.blacklistDetails.blacklistedAt)}
            </Typography>
          )}
        </Alert>
      )}

      {/* Profile Header */}
      <Card
        sx={{
          mb: 3,
          background: isDark
            ? theme.gradients.deepOcean
            : theme.gradients.blueGlass,
        }}
      >
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background:
                    participant.status === 'blacklisted'
                      ? `linear-gradient(135deg, ${brandColors.primary.threatRed} 0%, #8B2525 100%)`
                      : participant.status === 'verified'
                        ? `linear-gradient(135deg, ${statusColors.success} 0%, #1B8B6A 100%)`
                        : `linear-gradient(135deg, ${statusColors.warning} 0%, #C98500 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '2rem',
                  fontWeight: 700,
                  fontFamily: '"Space Grotesk", sans-serif',
                  boxShadow: `0 4px 20px ${
                    participant.status === 'blacklisted'
                      ? 'rgba(214, 69, 69, 0.4)'
                      : participant.status === 'verified'
                        ? 'rgba(58, 214, 163, 0.4)'
                        : 'rgba(245, 166, 35, 0.4)'
                  }`,
                }}
              >
                {participant.name.charAt(0)}
              </Box>
            </Grid>
            <Grid size="grow">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                <Typography
                  variant="h4"
                  sx={{
                    fontWeight: 700,
                    fontFamily: '"Space Grotesk", sans-serif',
                  }}
                >
                  {participant.name}
                </Typography>
                {getStatusChip(participant.status, isDark)}
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, color: 'text.secondary' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <EmailIcon fontSize="small" />
                  <Typography variant="body2">{participant.email}</Typography>
                </Box>
                {participant.department && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <DepartmentIcon fontSize="small" />
                    <Typography variant="body2">
                      {participant.department} - {participant.role}
                    </Typography>
                  </Box>
                )}
              </Box>
            </Grid>
            <Grid>
              <TrustBadge status={participant.status} size="large" />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Risk & Trust Scores */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card
            sx={{
              height: '100%',
              background: isDark
                ? theme.gradients.deepOcean
                : theme.gradients.blueGlass,
            }}
          >
            <CardContent>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 600,
                  mb: 2,
                  fontFamily: '"Space Grotesk", sans-serif',
                }}
              >
                Risk Assessment
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Typography
                  variant="h2"
                  sx={{
                    fontWeight: 700,
                    fontFamily: '"JetBrains Mono", monospace',
                    color:
                      participant.riskScore >= 86
                        ? brandColors.primary.threatRed
                        : participant.riskScore >= 60
                          ? statusColors.error
                          : participant.riskScore >= 30
                            ? statusColors.warning
                            : statusColors.success,
                  }}
                >
                  {participant.riskScore}%
                </Typography>
                <Box sx={{ flexGrow: 1 }}>
                  <RiskIndicator
                    score={participant.riskScore}
                    showLabel={true}
                    showPercentage={false}
                    size="large"
                  />
                </Box>
              </Box>
              <Divider sx={{ my: 2, borderColor: theme.customColors.borderColor }} />
              <Grid container spacing={2}>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="caption" color="text.secondary">
                    Total Meetings
                  </Typography>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 600,
                      fontFamily: '"JetBrains Mono", monospace',
                    }}
                  >
                    {participant.totalMeetings}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="caption" color="text.secondary">
                    Incident Rate
                  </Typography>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 600,
                      fontFamily: '"JetBrains Mono", monospace',
                      color:
                        participant.incidentRate > 50
                          ? brandColors.primary.threatRed
                          : participant.incidentRate > 0
                            ? statusColors.warning
                            : 'inherit',
                    }}
                  >
                    {participant.incidentRate}%
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="caption" color="text.secondary">
                    Compromised Meetings
                  </Typography>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 600,
                      fontFamily: '"JetBrains Mono", monospace',
                      color: participant.compromisedMeetings > 0 ? brandColors.primary.threatRed : 'inherit',
                    }}
                  >
                    {participant.compromisedMeetings}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="caption" color="text.secondary">
                    Trust Score
                  </Typography>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 600,
                      fontFamily: '"JetBrains Mono", monospace',
                      color:
                        participant.trustScore >= 70
                          ? statusColors.success
                          : participant.trustScore >= 40
                            ? statusColors.warning
                            : statusColors.error,
                    }}
                  >
                    {participant.trustScore}%
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card
            sx={{
              height: '100%',
              background: isDark
                ? theme.gradients.deepOcean
                : theme.gradients.blueGlass,
            }}
          >
            <CardContent>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 600,
                  mb: 2,
                  fontFamily: '"Space Grotesk", sans-serif',
                }}
              >
                Activity Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 6 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <ScheduleIcon fontSize="small" sx={{ color: brandColors.primary.signalTeal }} />
                    <Typography variant="caption" color="text.secondary">
                      First Seen
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight={500}>
                    {formatShortDate(participant.firstSeen)}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <ScheduleIcon fontSize="small" sx={{ color: brandColors.primary.signalTeal }} />
                    <Typography variant="caption" color="text.secondary">
                      Last Seen
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight={500}>
                    {formatShortDate(participant.lastSeen)}
                  </Typography>
                </Grid>
              </Grid>

              {/* Verification Details */}
              {participant.verification && (
                <>
                  <Divider sx={{ my: 2, borderColor: theme.customColors.borderColor }} />
                  <Typography
                    variant="subtitle2"
                    sx={{
                      fontWeight: 600,
                      mb: 1.5,
                      fontFamily: '"Space Grotesk", sans-serif',
                    }}
                  >
                    Verification Details
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {participant.verification.ssoVerified && (
                      <Chip
                        size="small"
                        icon={<VerifiedIcon />}
                        label={`SSO: ${participant.verification.ssoProvider}`}
                        sx={{
                          background: isDark
                            ? 'rgba(58, 214, 163, 0.15)'
                            : 'rgba(45, 190, 139, 0.1)',
                          color: statusColors.success,
                          border: `1px solid ${statusColors.success}`,
                          '& .MuiChip-icon': { color: statusColors.success },
                        }}
                      />
                    )}
                    {participant.verification.behavioralBiometricsConsistent && (
                      <Chip
                        size="small"
                        icon={<SecurityIcon />}
                        label="Biometrics Consistent"
                        sx={{
                          background: isDark
                            ? 'rgba(58, 214, 163, 0.15)'
                            : 'rgba(45, 190, 139, 0.1)',
                          color: statusColors.success,
                          border: `1px solid ${statusColors.success}`,
                          '& .MuiChip-icon': { color: statusColors.success },
                        }}
                      />
                    )}
                    {participant.verification.noDeepfakeIndicators && (
                      <Chip
                        size="small"
                        icon={<VerifiedIcon />}
                        label="No Deepfake Indicators"
                        sx={{
                          background: isDark
                            ? 'rgba(58, 214, 163, 0.15)'
                            : 'rgba(45, 190, 139, 0.1)',
                          color: statusColors.success,
                          border: `1px solid ${statusColors.success}`,
                          '& .MuiChip-icon': { color: statusColors.success },
                        }}
                      />
                    )}
                  </Box>

                  {/* Known Devices */}
                  {participant.verification.knownDevices && (
                    <Box sx={{ mt: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <DevicesIcon fontSize="small" sx={{ color: brandColors.primary.signalTeal }} />
                        <Typography variant="caption" color="text.secondary">
                          Known Devices
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {participant.verification.knownDevices.map((device, idx) => (
                          <Chip
                            key={idx}
                            size="small"
                            label={device.name}
                            variant="outlined"
                            sx={{
                              borderColor: theme.customColors.borderColor,
                            }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {/* Typical Locations */}
                  {participant.verification.typicalLocations && (
                    <Box sx={{ mt: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <LocationIcon fontSize="small" sx={{ color: brandColors.primary.signalTeal }} />
                        <Typography variant="caption" color="text.secondary">
                          Typical Locations
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {participant.verification.typicalLocations.map((loc, idx) => (
                          <Chip
                            key={idx}
                            size="small"
                            label={loc}
                            variant="outlined"
                            sx={{
                              borderColor: theme.customColors.borderColor,
                            }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Threat Intelligence (for flagged/blacklisted users) */}
      {participant.threatIntelligence && (
        <Card
          sx={{
            mb: 3,
            border: `2px solid ${brandColors.primary.threatRed}`,
            background: isDark
              ? 'linear-gradient(135deg, rgba(214, 69, 69, 0.08) 0%, rgba(26, 39, 64, 0.95) 100%)'
              : 'linear-gradient(135deg, rgba(214, 69, 69, 0.05) 0%, rgba(255, 255, 255, 0.95) 100%)',
          }}
        >
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <WarningIcon sx={{ color: brandColors.primary.threatRed }} />
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 600,
                  color: brandColors.primary.threatRed,
                  fontFamily: '"Space Grotesk", sans-serif',
                }}
              >
                Threat Intelligence
              </Typography>
            </Box>

            <Grid container spacing={3}>
              {/* Detection Indicators */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 600,
                    mb: 1.5,
                    fontFamily: '"Space Grotesk", sans-serif',
                  }}
                >
                  Detection Indicators
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {participant.threatIntelligence.deepfakeTechnologyUsed && (
                    <Alert
                      severity="error"
                      icon={<WarningIcon />}
                      sx={{
                        py: 0,
                        background: isDark
                          ? 'rgba(214, 69, 69, 0.15)'
                          : 'rgba(214, 69, 69, 0.1)',
                        border: `1px solid ${brandColors.primary.threatRed}`,
                      }}
                    >
                      Deepfake Technology Detected
                    </Alert>
                  )}
                  {participant.threatIntelligence.voiceCloningDetected && (
                    <Alert
                      severity="error"
                      icon={<WarningIcon />}
                      sx={{
                        py: 0,
                        background: isDark
                          ? 'rgba(214, 69, 69, 0.15)'
                          : 'rgba(214, 69, 69, 0.1)',
                        border: `1px solid ${brandColors.primary.threatRed}`,
                      }}
                    >
                      Voice Cloning Detected
                    </Alert>
                  )}
                  {participant.threatIntelligence.faceSwapDetected && (
                    <Alert
                      severity="error"
                      icon={<WarningIcon />}
                      sx={{
                        py: 0,
                        background: isDark
                          ? 'rgba(214, 69, 69, 0.15)'
                          : 'rgba(214, 69, 69, 0.1)',
                        border: `1px solid ${brandColors.primary.threatRed}`,
                      }}
                    >
                      Face Swap Detected
                    </Alert>
                  )}
                  {participant.threatIntelligence.virtualCameraUsage && (
                    <Alert
                      severity="warning"
                      icon={<WarningIcon />}
                      sx={{
                        py: 0,
                        background: isDark
                          ? 'rgba(245, 166, 35, 0.15)'
                          : 'rgba(245, 166, 35, 0.1)',
                        border: `1px solid ${brandColors.primary.alertAmber}`,
                      }}
                    >
                      Virtual Camera Usage
                    </Alert>
                  )}
                  {participant.threatIntelligence.unknownDeviceFingerprint && (
                    <Alert
                      severity="warning"
                      icon={<WarningIcon />}
                      sx={{
                        py: 0,
                        background: isDark
                          ? 'rgba(245, 166, 35, 0.15)'
                          : 'rgba(245, 166, 35, 0.1)',
                        border: `1px solid ${brandColors.primary.alertAmber}`,
                      }}
                    >
                      Unknown Device Fingerprint
                    </Alert>
                  )}
                </Box>
              </Grid>

              {/* Location & Network */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 600,
                    mb: 1.5,
                    fontFamily: '"Space Grotesk", sans-serif',
                  }}
                >
                  Location & Network Analysis
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Origin Location
                    </Typography>
                    <Typography variant="body1" fontWeight={500}>
                      {participant.threatIntelligence.originLocation}
                    </Typography>
                  </Box>
                  {participant.threatIntelligence.vpnUsage && (
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        VPN Provider
                      </Typography>
                      <Typography variant="body1" fontWeight={500}>
                        {participant.threatIntelligence.vpnProvider || 'Unknown VPN'}
                      </Typography>
                    </Box>
                  )}
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Verification Failures
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{
                        fontWeight: 500,
                        color: brandColors.primary.threatRed,
                        fontFamily: '"JetBrains Mono", monospace',
                      }}
                    >
                      {participant.threatIntelligence.multipleVerificationFailures} failed attempts
                    </Typography>
                  </Box>
                </Box>
              </Grid>

              {/* Social Engineering Tactics */}
              {participant.threatIntelligence.socialEngineeringTactics.length > 0 && (
                <Grid size={{ xs: 12 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{
                      fontWeight: 600,
                      mb: 1.5,
                      fontFamily: '"Space Grotesk", sans-serif',
                    }}
                  >
                    Social Engineering Tactics Used
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {participant.threatIntelligence.socialEngineeringTactics.map((tactic, idx) => (
                      <Chip
                        key={idx}
                        label={tactic}
                        size="small"
                        sx={{
                          background: isDark
                            ? 'linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(214, 69, 69, 0.3) 100%)'
                            : 'rgba(214, 69, 69, 0.1)',
                          color: statusColors.error,
                          fontWeight: 600,
                          border: `1px solid ${isDark ? 'rgba(255, 107, 107, 0.3)' : 'rgba(214, 69, 69, 0.3)'}`,
                        }}
                      />
                    ))}
                  </Box>
                </Grid>
              )}

              {/* Threat Pattern Match */}
              <Grid size={{ xs: 12 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 600,
                    mb: 1,
                    fontFamily: '"Space Grotesk", sans-serif',
                  }}
                >
                  Known Threat Pattern Match
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="body1">
                    {participant.threatIntelligence.knownThreatPatternMatch}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={participant.threatIntelligence.threatMatchPercentage}
                      sx={{
                        width: 100,
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: isDark
                          ? 'rgba(214, 69, 69, 0.2)'
                          : 'rgba(214, 69, 69, 0.1)',
                        '& .MuiLinearProgress-bar': {
                          background: `linear-gradient(90deg, ${brandColors.primary.threatRed} 0%, #8B2525 100%)`,
                          borderRadius: 4,
                        },
                      }}
                    />
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: 600,
                        color: brandColors.primary.threatRed,
                        fontFamily: '"JetBrains Mono", monospace',
                      }}
                    >
                      {participant.threatIntelligence.threatMatchPercentage}% match
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Blacklist Details */}
      {participant.blacklistDetails && (
        <Card
          sx={{
            mb: 3,
            background: isDark
              ? 'linear-gradient(135deg, rgba(214, 69, 69, 0.1) 0%, rgba(26, 39, 64, 0.95) 100%)'
              : 'linear-gradient(135deg, rgba(214, 69, 69, 0.08) 0%, rgba(255, 255, 255, 0.95) 100%)',
          }}
        >
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <BlockIcon sx={{ color: brandColors.primary.threatRed }} />
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 600,
                  fontFamily: '"Space Grotesk", sans-serif',
                }}
              >
                Blacklist Details
              </Typography>
            </Box>

            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 6 }}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Reason for Blacklist
                  </Typography>
                  <Typography variant="body1" fontWeight={500}>
                    {participant.blacklistDetails.reason}
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Blacklisted By
                  </Typography>
                  <Typography variant="body1">
                    {participant.blacklistDetails.blacklistedBy}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Blacklisted At
                  </Typography>
                  <Typography variant="body1">
                    {formatDate(participant.blacklistDetails.blacklistedAt)}
                  </Typography>
                </Box>
              </Grid>

              <Grid size={{ xs: 12, md: 6 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 600,
                    mb: 1,
                    fontFamily: '"Space Grotesk", sans-serif',
                  }}
                >
                  Blocked Attributes
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                  <Typography variant="body2">
                    Email: {participant.blacklistDetails.blockedAttributes.email}
                  </Typography>
                  {participant.blacklistDetails.blockedAttributes.ipRange && (
                    <Typography variant="body2">
                      IP Range: {participant.blacklistDetails.blockedAttributes.ipRange}
                    </Typography>
                  )}
                  {participant.blacklistDetails.blockedAttributes.deviceFingerprint && (
                    <Typography variant="body2">
                      Device: {participant.blacklistDetails.blockedAttributes.deviceFingerprint}
                    </Typography>
                  )}
                </Box>
              </Grid>

              <Grid size={{ xs: 12 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 600,
                    mb: 1,
                    fontFamily: '"Space Grotesk", sans-serif',
                  }}
                >
                  Enforced Actions
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {participant.blacklistDetails.actions.map((action, idx) => (
                    <Chip
                      key={idx}
                      label={action}
                      size="small"
                      sx={{
                        background: `linear-gradient(135deg, ${brandColors.primary.threatRed} 0%, #8B2525 100%)`,
                        color: 'white',
                      }}
                    />
                  ))}
                </Box>
              </Grid>

              <Grid size={{ xs: 12 }}>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  {participant.blacklistDetails.reportedToAuthorities && (
                    <Chip
                      icon={<SecurityIcon sx={{ color: 'white !important' }} />}
                      label="Reported to Authorities"
                      sx={{
                        background: `linear-gradient(135deg, ${brandColors.primary.threatRed} 0%, #8B2525 100%)`,
                        color: 'white',
                      }}
                    />
                  )}
                  {participant.blacklistDetails.reportedToThreatDatabase && (
                    <Chip
                      icon={<SecurityIcon sx={{ color: 'white !important' }} />}
                      label="Reported to Threat Database"
                      sx={{
                        background: `linear-gradient(135deg, ${brandColors.primary.threatRed} 0%, #8B2525 100%)`,
                        color: 'white',
                      }}
                    />
                  )}
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Meeting History */}
      {participant.meetingHistory && participant.meetingHistory.length > 0 && (
        <Card
          sx={{
            background: isDark
              ? theme.gradients.deepOcean
              : theme.gradients.blueGlass,
          }}
        >
          <CardContent>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                mb: 2,
                fontFamily: '"Space Grotesk", sans-serif',
              }}
            >
              Meeting History
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>MEETING ID</TableCell>
                    <TableCell>MEETING NAME</TableCell>
                    <TableCell>DATE</TableCell>
                    <TableCell>ROLE</TableCell>
                    <TableCell align="center">RISK SCORE</TableCell>
                    <TableCell align="center">DURATION</TableCell>
                    <TableCell>INCIDENT</TableCell>
                    <TableCell align="center">ACTIONS</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {participant.meetingHistory.map((meeting) => (
                    <TableRow
                      key={meeting.meetingId}
                      hover
                      sx={{
                        cursor: 'pointer',
                        backgroundColor: meeting.incidentDetected
                          ? isDark
                            ? 'rgba(214, 69, 69, 0.1)'
                            : 'rgba(214, 69, 69, 0.05)'
                          : 'transparent',
                        '&:hover': {
                          backgroundColor: meeting.incidentDetected
                            ? isDark
                              ? 'rgba(214, 69, 69, 0.15)'
                              : 'rgba(214, 69, 69, 0.08)'
                            : isDark
                              ? 'rgba(31, 182, 166, 0.06)'
                              : 'rgba(31, 60, 136, 0.03)',
                        },
                      }}
                      onClick={() => navigate(`/app/meetings/${meeting.meetingId}`)}
                    >
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 500,
                            fontFamily: '"JetBrains Mono", monospace',
                            fontSize: '0.8125rem',
                          }}
                        >
                          {meeting.meetingId}
                        </Typography>
                      </TableCell>
                      <TableCell>{meeting.meetingName}</TableCell>
                      <TableCell>{formatShortDate(meeting.meetingDate)}</TableCell>
                      <TableCell>
                        <Chip
                          label={meeting.role.toUpperCase()}
                          size="small"
                          variant="outlined"
                          sx={{
                            fontSize: '0.7rem',
                            borderColor: theme.customColors.borderColor,
                          }}
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 700,
                            fontFamily: '"JetBrains Mono", monospace',
                            color:
                              meeting.riskScore >= 86
                                ? brandColors.primary.threatRed
                                : meeting.riskScore >= 60
                                  ? statusColors.error
                                  : 'inherit',
                          }}
                        >
                          {meeting.riskScore}%
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Typography
                          variant="body2"
                          sx={{ fontFamily: '"JetBrains Mono", monospace' }}
                        >
                          {meeting.minutesInMeeting} min
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {meeting.incidentDetected ? (
                          <Box>
                            <Chip
                              label={meeting.incidentType}
                              size="small"
                              sx={{
                                background: isDark
                                  ? 'linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(214, 69, 69, 0.3) 100%)'
                                  : 'rgba(214, 69, 69, 0.1)',
                                color: statusColors.error,
                                fontWeight: 600,
                                fontSize: '0.7rem',
                                border: `1px solid ${isDark ? 'rgba(255, 107, 107, 0.3)' : 'rgba(214, 69, 69, 0.3)'}`,
                              }}
                            />
                            {meeting.outcome && (
                              <Typography
                                variant="caption"
                                display="block"
                                sx={{ color: statusColors.success, mt: 0.5 }}
                              >
                                {meeting.outcome}
                              </Typography>
                            )}
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            None
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="View Meeting">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/app/meetings/${meeting.meetingId}`);
                            }}
                            sx={{
                              color: brandColors.primary.signalTeal,
                              '&:hover': {
                                backgroundColor: isDark
                                  ? 'rgba(31, 182, 166, 0.1)'
                                  : 'rgba(31, 60, 136, 0.05)',
                              },
                            }}
                          >
                            <ViewIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ParticipantProfilePage;
