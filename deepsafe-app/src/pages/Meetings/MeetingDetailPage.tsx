import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Tabs,
  Tab,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Breadcrumbs,
  Link,
  useTheme,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Download as DownloadIcon,
  PlayArrow as PlayIcon,
  Share as ShareIcon,
  Report as ReportIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import { useThemeMode } from '../../context/ThemeContext';
import { RiskBadge, RiskIndicator, TrustBadge } from '../../components/common';
import { brandColors } from '../../theme/colors';
import { getMeetingById } from '../../data';
import type { TimelineEvent, TranscriptEntry } from '../../types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <Box role="tabpanel" hidden={value !== index} sx={{ pt: 3 }}>
    {value === index && children}
  </Box>
);

const TimelineView: React.FC<{ events: TimelineEvent[] }> = ({ events }) => {
  const { isDark } = useThemeMode();
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  const getEventIcon = (_type: TimelineEvent['type'], severity?: string) => {
    switch (severity) {
      case 'error':
        return <ErrorIcon sx={{ color: brandColors.primary.threatRed }} />;
      case 'warning':
        return <WarningIcon sx={{ color: statusColors.warning }} />;
      case 'success':
        return <CheckCircleIcon sx={{ color: statusColors.success }} />;
      default:
        return <SecurityIcon sx={{ color: brandColors.primary.signalTeal }} />;
    }
  };

  return (
    <Box sx={{ pl: 2 }}>
      {events.map((event, index) => (
        <Box
          key={event.id}
          sx={{
            display: 'flex',
            gap: 2,
            pb: 3,
            position: 'relative',
            '&::before': index < events.length - 1 ? {
              content: '""',
              position: 'absolute',
              left: 11,
              top: 28,
              bottom: 0,
              width: 2,
              backgroundColor: isDark
                ? 'rgba(255, 255, 255, 0.1)'
                : 'rgba(0, 0, 0, 0.1)',
            } : undefined,
          }}
        >
          <Box sx={{ zIndex: 1 }}>
            {getEventIcon(event.type, event.severity)}
          </Box>
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'baseline' }}>
              <Typography variant="caption" color="text.secondary">
                {new Date(event.timestamp).toLocaleTimeString('en-US', {
                  hour: 'numeric',
                  minute: '2-digit',
                  hour12: true,
                })}
              </Typography>
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: 600,
                  fontFamily: '"Space Grotesk", sans-serif',
                }}
              >
                {event.title}
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              {event.description}
            </Typography>
            {event.riskScore !== undefined && (
              <Chip
                size="small"
                label={`Risk: ${event.riskScore}%`}
                sx={{
                  mt: 1,
                  fontFamily: '"JetBrains Mono", monospace',
                  fontWeight: 600,
                  background: event.riskScore >= 60
                    ? isDark
                      ? 'linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(214, 69, 69, 0.3) 100%)'
                      : 'rgba(214, 69, 69, 0.1)'
                    : isDark
                      ? 'linear-gradient(135deg, rgba(58, 214, 163, 0.2) 0%, rgba(45, 190, 139, 0.3) 100%)'
                      : 'rgba(45, 190, 139, 0.1)',
                  color: event.riskScore >= 60 ? statusColors.error : statusColors.success,
                  border: `1px solid ${event.riskScore >= 60
                    ? isDark ? 'rgba(255, 107, 107, 0.3)' : 'rgba(214, 69, 69, 0.3)'
                    : isDark ? 'rgba(58, 214, 163, 0.3)' : 'rgba(45, 190, 139, 0.3)'
                  }`,
                }}
              />
            )}
          </Box>
        </Box>
      ))}
    </Box>
  );
};

const TranscriptView: React.FC<{ entries: TranscriptEntry[] }> = ({ entries }) => {
  const theme = useTheme();
  const { isDark } = useThemeMode();
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  return (
    <Box>
      {entries.map((entry) => (
        <Paper
          key={entry.id}
          sx={{
            p: 2,
            mb: 2,
            background: entry.isFlagged
              ? isDark
                ? 'linear-gradient(135deg, rgba(214, 69, 69, 0.1) 0%, rgba(26, 39, 64, 0.95) 100%)'
                : 'linear-gradient(135deg, rgba(214, 69, 69, 0.05) 0%, rgba(255, 255, 255, 0.95) 100%)'
              : isDark
                ? theme.gradients.deepOcean
                : theme.gradients.blueGlass,
            border: entry.isFlagged
              ? `1px solid ${brandColors.primary.threatRed}`
              : `1px solid ${theme.customColors.borderColor}`,
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography
              variant="subtitle2"
              sx={{
                fontWeight: 600,
                fontFamily: '"JetBrains Mono", monospace',
              }}
            >
              [{new Date(entry.timestamp).toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
                second: '2-digit',
              })}] {entry.speaker}
            </Typography>
            <Chip
              size="small"
              label={`Risk: ${entry.riskScore}%`}
              sx={{
                fontFamily: '"JetBrains Mono", monospace',
                fontWeight: 600,
                background:
                  entry.riskScore >= 60
                    ? isDark
                      ? 'linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(214, 69, 69, 0.3) 100%)'
                      : 'rgba(214, 69, 69, 0.1)'
                    : entry.riskScore >= 30
                      ? isDark
                        ? 'linear-gradient(135deg, rgba(255, 200, 87, 0.2) 0%, rgba(245, 166, 35, 0.3) 100%)'
                        : 'rgba(245, 166, 35, 0.1)'
                      : isDark
                        ? 'linear-gradient(135deg, rgba(58, 214, 163, 0.2) 0%, rgba(45, 190, 139, 0.3) 100%)'
                        : 'rgba(45, 190, 139, 0.1)',
                color:
                  entry.riskScore >= 60
                    ? statusColors.error
                    : entry.riskScore >= 30
                      ? statusColors.warning
                      : statusColors.success,
                border: `1px solid ${
                  entry.riskScore >= 60
                    ? isDark ? 'rgba(255, 107, 107, 0.3)' : 'rgba(214, 69, 69, 0.3)'
                    : entry.riskScore >= 30
                      ? isDark ? 'rgba(255, 200, 87, 0.3)' : 'rgba(245, 166, 35, 0.3)'
                      : isDark ? 'rgba(58, 214, 163, 0.3)' : 'rgba(45, 190, 139, 0.3)'
                }`,
              }}
            />
          </Box>
          <Typography variant="body2" sx={{ mb: entry.riskIndicators ? 1 : 0 }}>
            "{entry.text}"
          </Typography>
          {entry.riskIndicators && entry.riskIndicators.length > 0 && (
            <Box sx={{ mt: 1 }}>
              {entry.riskIndicators.map((indicator, idx) => (
                <Chip
                  key={idx}
                  size="small"
                  label={indicator}
                  sx={{
                    mr: 0.5,
                    mb: 0.5,
                    fontSize: '0.6875rem',
                    background: isDark
                      ? 'rgba(255, 255, 255, 0.1)'
                      : 'rgba(0, 0, 0, 0.06)',
                    border: `1px solid ${theme.customColors.borderColor}`,
                  }}
                />
              ))}
            </Box>
          )}
        </Paper>
      ))}
    </Box>
  );
};

export const MeetingDetailPage: React.FC = () => {
  const { meetingId } = useParams<{ meetingId: string }>();
  const navigate = useNavigate();
  const theme = useTheme();
  const { isDark } = useThemeMode();
  const [tabValue, setTabValue] = useState(0);

  const meeting = getMeetingById(meetingId || '');
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  if (!meeting) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography
          variant="h5"
          sx={{ fontFamily: '"Space Grotesk", sans-serif' }}
        >
          Meeting not found
        </Typography>
        <Button
          onClick={() => navigate('/app/meetings')}
          sx={{
            mt: 2,
            color: brandColors.primary.signalTeal,
            '&:hover': {
              backgroundColor: isDark
                ? 'rgba(31, 182, 166, 0.08)'
                : 'rgba(31, 60, 136, 0.04)',
            },
          }}
        >
          Back to Meeting History
        </Button>
      </Box>
    );
  }

  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });

  return (
    <Box>
      {/* Breadcrumb */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link
          component={RouterLink}
          to="/meetings"
          underline="hover"
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
            color: brandColors.primary.signalTeal,
            '&:hover': {
              color: isDark
                ? brandColors.darkText.primary
                : brandColors.primary.deepSafeBlue,
            },
          }}
        >
          <ArrowBackIcon fontSize="small" />
          Back to Meeting History
        </Link>
      </Breadcrumbs>

      {/* Page Header */}
      <Box sx={{ mb: 3 }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            fontFamily: '"Space Grotesk", sans-serif',
            background: isDark
              ? `linear-gradient(90deg, ${brandColors.darkText.primary} 0%, ${brandColors.primary.signalTeal} 100%)`
              : `linear-gradient(90deg, ${brandColors.lightText.primary} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          Meeting Details: {meeting.meetingName}
        </Typography>
      </Box>

      {/* Tabs */}
      <Card
        sx={{
          background: isDark
            ? theme.gradients.deepOcean
            : theme.gradients.blueGlass,
        }}
      >
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          sx={{
            borderBottom: `1px solid ${theme.customColors.borderColor}`,
            px: 2,
            '& .MuiTab-root': {
              color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
              '&.Mui-selected': {
                color: brandColors.primary.signalTeal,
              },
            },
            '& .MuiTabs-indicator': {
              backgroundColor: brandColors.primary.signalTeal,
            },
          }}
        >
          <Tab label="Overview" />
          <Tab label="Transcript" disabled={!meeting.transcript} />
          <Tab label="Participants" />
          <Tab label="Forensics" disabled={!meeting.forensics} />
          <Tab label="Actions" />
        </Tabs>

        <CardContent>
          {/* Overview Tab */}
          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              {/* Meeting Info */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 600,
                    mb: 2,
                    fontFamily: '"Space Grotesk", sans-serif',
                  }}
                >
                  Meeting Information
                </Typography>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    background: isDark
                      ? 'rgba(255, 255, 255, 0.02)'
                      : 'rgba(0, 0, 0, 0.01)',
                    borderColor: theme.customColors.borderColor,
                  }}
                >
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 6 }}>
                      <Typography variant="caption" color="text.secondary">
                        Meeting ID
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 500,
                          fontFamily: '"JetBrains Mono", monospace',
                        }}
                      >
                        {meeting.id}
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <Typography variant="caption" color="text.secondary">
                        Meeting Name
                      </Typography>
                      <Typography variant="body2" fontWeight={500}>
                        {meeting.meetingName}
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <Typography variant="caption" color="text.secondary">
                        Date & Time
                      </Typography>
                      <Typography variant="body2" fontWeight={500}>
                        {formatDate(meeting.meetingDate)}
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <Typography variant="caption" color="text.secondary">
                        Duration
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 500,
                          fontFamily: '"JetBrains Mono", monospace',
                        }}
                      >
                        {meeting.duration} minutes
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <Typography variant="caption" color="text.secondary">
                        Host
                      </Typography>
                      <Typography variant="body2" fontWeight={500}>
                        {meeting.host}
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <Typography variant="caption" color="text.secondary">
                        Platform
                      </Typography>
                      <Typography
                        variant="body2"
                        fontWeight={500}
                        sx={{ textTransform: 'capitalize' }}
                      >
                        {meeting.platform}
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 12 }}>
                      <Typography variant="caption" color="text.secondary">
                        Status
                      </Typography>
                      <Box sx={{ mt: 0.5 }}>
                        {meeting.incident ? (
                          <Chip
                            icon={<CheckCircleIcon sx={{ color: `${statusColors.success} !important` }} />}
                            label={`Incident ${meeting.incident.outcome === 'prevented' ? 'Resolved' : 'Detected'}`}
                            size="small"
                            sx={{
                              background: isDark
                                ? 'linear-gradient(135deg, rgba(58, 214, 163, 0.2) 0%, rgba(45, 190, 139, 0.3) 100%)'
                                : 'rgba(45, 190, 139, 0.1)',
                              color: statusColors.success,
                              border: `1px solid ${isDark ? 'rgba(58, 214, 163, 0.3)' : 'rgba(45, 190, 139, 0.3)'}`,
                            }}
                          />
                        ) : (
                          <Chip
                            label="Normal"
                            size="small"
                            sx={{
                              background: isDark
                                ? 'rgba(255, 255, 255, 0.1)'
                                : 'rgba(0, 0, 0, 0.06)',
                              border: `1px solid ${theme.customColors.borderColor}`,
                            }}
                          />
                        )}
                      </Box>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>

              {/* Risk Assessment */}
              <Grid size={{ xs: 12, md: 6 }}>
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
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    background: isDark
                      ? 'rgba(255, 255, 255, 0.02)'
                      : 'rgba(0, 0, 0, 0.01)',
                    borderColor: theme.customColors.borderColor,
                  }}
                >
                  <Box sx={{ mb: 3 }}>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                        mb: 2,
                      }}
                    >
                      <Typography variant="body1">Overall Risk Score:</Typography>
                      <RiskBadge category={meeting.riskCategory} showIcon />
                    </Box>
                    <RiskIndicator
                      score={meeting.riskScore}
                      category={meeting.riskCategory}
                      showLabel={false}
                    />
                  </Box>

                  {meeting.incident?.riskBreakdown && (
                    <Grid container spacing={2}>
                      <Grid size={{ xs: 4 }}>
                        <Paper
                          sx={{
                            p: 1.5,
                            textAlign: 'center',
                            background:
                              meeting.incident.riskBreakdown.audioRisk >= 60
                                ? isDark
                                  ? 'linear-gradient(135deg, rgba(214, 69, 69, 0.15) 0%, rgba(139, 37, 37, 0.2) 100%)'
                                  : 'rgba(214, 69, 69, 0.08)'
                                : isDark
                                  ? 'rgba(255, 255, 255, 0.03)'
                                  : 'rgba(0, 0, 0, 0.02)',
                            border: `1px solid ${theme.customColors.borderColor}`,
                          }}
                        >
                          <Typography variant="caption" color="text.secondary">
                            Audio Risk
                          </Typography>
                          <Typography
                            variant="h5"
                            sx={{
                              fontWeight: 700,
                              fontFamily: '"JetBrains Mono", monospace',
                              color:
                                meeting.incident.riskBreakdown.audioRisk >= 60
                                  ? brandColors.primary.threatRed
                                  : 'inherit',
                            }}
                          >
                            {meeting.incident.riskBreakdown.audioRisk}%
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid size={{ xs: 4 }}>
                        <Paper
                          sx={{
                            p: 1.5,
                            textAlign: 'center',
                            background:
                              meeting.incident.riskBreakdown.videoRisk >= 60
                                ? isDark
                                  ? 'linear-gradient(135deg, rgba(214, 69, 69, 0.15) 0%, rgba(139, 37, 37, 0.2) 100%)'
                                  : 'rgba(214, 69, 69, 0.08)'
                                : isDark
                                  ? 'rgba(255, 255, 255, 0.03)'
                                  : 'rgba(0, 0, 0, 0.02)',
                            border: `1px solid ${theme.customColors.borderColor}`,
                          }}
                        >
                          <Typography variant="caption" color="text.secondary">
                            Video Risk
                          </Typography>
                          <Typography
                            variant="h5"
                            sx={{
                              fontWeight: 700,
                              fontFamily: '"JetBrains Mono", monospace',
                              color:
                                meeting.incident.riskBreakdown.videoRisk >= 60
                                  ? brandColors.primary.threatRed
                                  : 'inherit',
                            }}
                          >
                            {meeting.incident.riskBreakdown.videoRisk}%
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid size={{ xs: 4 }}>
                        <Paper
                          sx={{
                            p: 1.5,
                            textAlign: 'center',
                            background:
                              meeting.incident.riskBreakdown.credentialRisk >= 60
                                ? isDark
                                  ? 'linear-gradient(135deg, rgba(214, 69, 69, 0.15) 0%, rgba(139, 37, 37, 0.2) 100%)'
                                  : 'rgba(214, 69, 69, 0.08)'
                                : isDark
                                  ? 'rgba(255, 255, 255, 0.03)'
                                  : 'rgba(0, 0, 0, 0.02)',
                            border: `1px solid ${theme.customColors.borderColor}`,
                          }}
                        >
                          <Typography variant="caption" color="text.secondary">
                            Credential Risk
                          </Typography>
                          <Typography
                            variant="h5"
                            sx={{
                              fontWeight: 700,
                              fontFamily: '"JetBrains Mono", monospace',
                              color:
                                meeting.incident.riskBreakdown.credentialRisk >= 60
                                  ? brandColors.primary.threatRed
                                  : 'inherit',
                            }}
                          >
                            {meeting.incident.riskBreakdown.credentialRisk}%
                          </Typography>
                        </Paper>
                      </Grid>
                    </Grid>
                  )}
                </Paper>
              </Grid>

              {/* Timeline */}
              {meeting.timeline && (
                <Grid size={{ xs: 12 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      mb: 2,
                      fontFamily: '"Space Grotesk", sans-serif',
                    }}
                  >
                    Threat Detection Timeline
                  </Typography>
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 2,
                      background: isDark
                        ? 'rgba(255, 255, 255, 0.02)'
                        : 'rgba(0, 0, 0, 0.01)',
                      borderColor: theme.customColors.borderColor,
                    }}
                  >
                    <TimelineView events={meeting.timeline} />
                  </Paper>
                </Grid>
              )}

              {/* Key Findings */}
              {meeting.incident && (
                <Grid size={{ xs: 12 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      mb: 2,
                      fontFamily: '"Space Grotesk", sans-serif',
                    }}
                  >
                    Key Findings
                  </Typography>
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 2,
                      background:
                        meeting.incident.outcome === 'prevented'
                          ? isDark
                            ? 'linear-gradient(135deg, rgba(58, 214, 163, 0.1) 0%, rgba(26, 39, 64, 0.95) 100%)'
                            : 'linear-gradient(135deg, rgba(45, 190, 139, 0.05) 0%, rgba(255, 255, 255, 0.95) 100%)'
                          : isDark
                            ? 'linear-gradient(135deg, rgba(214, 69, 69, 0.1) 0%, rgba(26, 39, 64, 0.95) 100%)'
                            : 'linear-gradient(135deg, rgba(214, 69, 69, 0.05) 0%, rgba(255, 255, 255, 0.95) 100%)',
                      borderColor: meeting.incident.outcome === 'prevented'
                        ? statusColors.success
                        : brandColors.primary.threatRed,
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      {meeting.incident.outcome === 'prevented' ? (
                        <CheckCircleIcon sx={{ color: statusColors.success }} />
                      ) : (
                        <WarningIcon sx={{ color: brandColors.primary.threatRed }} />
                      )}
                      <Typography
                        variant="subtitle1"
                        sx={{
                          fontWeight: 600,
                          fontFamily: '"Space Grotesk", sans-serif',
                          color: meeting.incident.outcome === 'prevented'
                            ? statusColors.success
                            : brandColors.primary.threatRed,
                        }}
                      >
                        Attack {meeting.incident.outcome === 'prevented' ? 'Successfully Prevented' : 'Detected'}
                      </Typography>
                    </Box>
                    <Grid container spacing={2}>
                      <Grid size={{ xs: 6, sm: 3 }}>
                        <Typography variant="caption" color="text.secondary">
                          Threat Type
                        </Typography>
                        <Typography variant="body2" fontWeight={500} sx={{ textTransform: 'capitalize' }}>
                          {meeting.incident.type.replace(/_/g, ' ')}
                        </Typography>
                      </Grid>
                      {meeting.incident.amountProtected && (
                        <Grid size={{ xs: 6, sm: 3 }}>
                          <Typography variant="caption" color="text.secondary">
                            Amount Protected
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{
                              fontWeight: 500,
                              fontFamily: '"JetBrains Mono", monospace',
                              color: statusColors.success,
                            }}
                          >
                            ${meeting.incident.amountProtected.toLocaleString()}
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                  </Paper>
                </Grid>
              )}
            </Grid>
          </TabPanel>

          {/* Transcript Tab */}
          <TabPanel value={tabValue} index={1}>
            {meeting.transcript && <TranscriptView entries={meeting.transcript} />}
          </TabPanel>

          {/* Participants Tab */}
          <TabPanel value={tabValue} index={2}>
            <TableContainer
              component={Paper}
              variant="outlined"
              sx={{
                background: isDark
                  ? 'rgba(255, 255, 255, 0.02)'
                  : 'rgba(0, 0, 0, 0.01)',
                borderColor: theme.customColors.borderColor,
              }}
            >
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>STATUS</TableCell>
                    <TableCell>PARTICIPANT</TableCell>
                    <TableCell>ROLE</TableCell>
                    <TableCell align="center">TRUST SCORE</TableCell>
                    <TableCell align="center">MINUTES IN MEETING</TableCell>
                    <TableCell align="center">ACTIONS</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {meeting.participants.map((participant) => (
                    <TableRow
                      key={participant.id}
                      sx={{
                        backgroundColor: participant.isFlagged
                          ? isDark
                            ? 'rgba(214, 69, 69, 0.1)'
                            : 'rgba(214, 69, 69, 0.05)'
                          : 'transparent',
                        '&:hover': {
                          backgroundColor: participant.isFlagged
                            ? isDark
                              ? 'rgba(214, 69, 69, 0.15)'
                              : 'rgba(214, 69, 69, 0.08)'
                            : isDark
                              ? 'rgba(31, 182, 166, 0.06)'
                              : 'rgba(31, 60, 136, 0.03)',
                        },
                      }}
                    >
                      <TableCell>
                        <TrustBadge
                          level={
                            participant.isFlagged
                              ? 'high-risk'
                              : participant.isVerified
                              ? 'verified'
                              : 'external'
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={500}>
                          {participant.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {participant.email}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ textTransform: 'capitalize' }}>
                        {participant.role}
                      </TableCell>
                      <TableCell align="center">
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 600,
                            fontFamily: '"JetBrains Mono", monospace',
                            color:
                              participant.trustScore < 50
                                ? brandColors.primary.threatRed
                                : 'inherit',
                          }}
                        >
                          {participant.trustScore}%
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Typography
                          variant="body2"
                          sx={{ fontFamily: '"JetBrains Mono", monospace' }}
                        >
                          {participant.minutesInMeeting}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Button
                          size="small"
                          onClick={() =>
                            navigate(`/app/participants/${participant.id}`)
                          }
                          sx={{
                            color: brandColors.primary.signalTeal,
                            '&:hover': {
                              backgroundColor: isDark
                                ? 'rgba(31, 182, 166, 0.08)'
                                : 'rgba(31, 60, 136, 0.04)',
                            },
                          }}
                        >
                          View Profile
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          {/* Forensics Tab */}
          <TabPanel value={tabValue} index={3}>
            {meeting.forensics && (
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      mb: 2,
                      fontFamily: '"Space Grotesk", sans-serif',
                    }}
                  >
                    Video Analysis
                  </Typography>
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 2,
                      background: isDark
                        ? 'rgba(255, 255, 255, 0.02)'
                        : 'rgba(0, 0, 0, 0.01)',
                      borderColor: theme.customColors.borderColor,
                    }}
                  >
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Deepfake Confidence
                      </Typography>
                      <Typography
                        variant="h4"
                        sx={{
                          fontWeight: 700,
                          fontFamily: '"JetBrains Mono", monospace',
                          color: brandColors.primary.threatRed,
                        }}
                      >
                        {meeting.forensics.videoAnalysis.deepfakeConfidence}%
                      </Typography>
                    </Box>
                    <Typography
                      variant="subtitle2"
                      sx={{
                        mb: 1,
                        fontFamily: '"Space Grotesk", sans-serif',
                      }}
                    >
                      Detection Methods:
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText
                          primary={`Facial landmark inconsistencies: ${meeting.forensics.videoAnalysis.facialLandmarkInconsistencies} detected`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary={`Micro-expression anomalies: ${meeting.forensics.videoAnalysis.microExpressionAnomalies ? 'Yes' : 'No'}`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary={`Lighting inconsistencies: ${meeting.forensics.videoAnalysis.lightingInconsistencies} instances`}
                        />
                      </ListItem>
                    </List>
                  </Paper>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      mb: 2,
                      fontFamily: '"Space Grotesk", sans-serif',
                    }}
                  >
                    Audio Analysis
                  </Typography>
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 2,
                      background: isDark
                        ? 'rgba(255, 255, 255, 0.02)'
                        : 'rgba(0, 0, 0, 0.01)',
                      borderColor: theme.customColors.borderColor,
                    }}
                  >
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Voice Cloning Confidence
                      </Typography>
                      <Typography
                        variant="h4"
                        sx={{
                          fontWeight: 700,
                          fontFamily: '"JetBrains Mono", monospace',
                          color: statusColors.warning,
                        }}
                      >
                        {meeting.forensics.audioAnalysis.voiceCloningConfidence}%
                      </Typography>
                    </Box>
                    <Typography
                      variant="subtitle2"
                      sx={{
                        mb: 1,
                        fontFamily: '"Space Grotesk", sans-serif',
                      }}
                    >
                      Detection Methods:
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText
                          primary={`Spectral anomalies: ${meeting.forensics.audioAnalysis.spectralAnomalies ? 'Detected' : 'Not detected'}`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary={`Audio-video desync: ${meeting.forensics.audioAnalysis.audioVideoDesync}ms`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary={`Voice fingerprint match: ${meeting.forensics.audioAnalysis.voiceFingerprintMatch ? 'Yes' : 'No match'}`}
                        />
                      </ListItem>
                    </List>
                  </Paper>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      mb: 2,
                      fontFamily: '"Space Grotesk", sans-serif',
                    }}
                  >
                    Network & Device Analysis
                  </Typography>
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 2,
                      background: isDark
                        ? 'rgba(255, 255, 255, 0.02)'
                        : 'rgba(0, 0, 0, 0.01)',
                      borderColor: theme.customColors.borderColor,
                    }}
                  >
                    <Grid container spacing={1}>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" color="text.secondary">
                          IP Address
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 500,
                            fontFamily: '"JetBrains Mono", monospace',
                          }}
                        >
                          {meeting.forensics.networkAnalysis.ipAddress}
                        </Typography>
                      </Grid>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" color="text.secondary">
                          Location
                        </Typography>
                        <Typography variant="body2" fontWeight={500}>
                          {meeting.forensics.networkAnalysis.location}
                        </Typography>
                      </Grid>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" color="text.secondary">
                          VPN Detected
                        </Typography>
                        <Typography variant="body2" fontWeight={500}>
                          {meeting.forensics.networkAnalysis.vpnDetected
                            ? `Yes (${meeting.forensics.networkAnalysis.vpnProvider})`
                            : 'No'}
                        </Typography>
                      </Grid>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" color="text.secondary">
                          Virtual Camera
                        </Typography>
                        <Typography variant="body2" fontWeight={500}>
                          {meeting.forensics.networkAnalysis.virtualCameraDetected
                            ? meeting.forensics.networkAnalysis.virtualCameraName
                            : 'Not detected'}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Paper>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      mb: 2,
                      fontFamily: '"Space Grotesk", sans-serif',
                    }}
                  >
                    Behavioral Analysis
                  </Typography>
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 2,
                      background: isDark
                        ? 'rgba(255, 255, 255, 0.02)'
                        : 'rgba(0, 0, 0, 0.01)',
                      borderColor: theme.customColors.borderColor,
                    }}
                  >
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Social Engineering Score
                      </Typography>
                      <Typography
                        variant="h4"
                        sx={{
                          fontWeight: 700,
                          fontFamily: '"JetBrains Mono", monospace',
                          color: brandColors.primary.threatRed,
                        }}
                      >
                        {meeting.forensics.behavioralAnalysis.socialEngineeringScore}%
                      </Typography>
                    </Box>
                    <Grid container spacing={1}>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" color="text.secondary">
                          Authority Bypass
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 500,
                            fontFamily: '"JetBrains Mono", monospace',
                          }}
                        >
                          {meeting.forensics.behavioralAnalysis.authorityBypass}%
                        </Typography>
                      </Grid>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" color="text.secondary">
                          Urgency Tactics
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 500,
                            fontFamily: '"JetBrains Mono", monospace',
                          }}
                        >
                          {meeting.forensics.behavioralAnalysis.urgencyTactics}%
                        </Typography>
                      </Grid>
                    </Grid>
                    <Typography variant="body2" sx={{ mt: 2 }}>
                      {meeting.forensics.behavioralAnalysis.knownAttackPatternSimilarity}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            )}
          </TabPanel>

          {/* Actions Tab */}
          <TabPanel value={tabValue} index={4}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                mb: 3,
                fontFamily: '"Space Grotesk", sans-serif',
              }}
            >
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                sx={{
                  background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                  '&:hover': {
                    background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
                  },
                }}
              >
                Download Full Report
              </Button>
              <Button
                variant="outlined"
                startIcon={<PlayIcon />}
                sx={{
                  borderColor: brandColors.primary.signalTeal,
                  color: brandColors.primary.signalTeal,
                  '&:hover': {
                    borderColor: brandColors.primary.signalTeal,
                    backgroundColor: isDark
                      ? 'rgba(31, 182, 166, 0.08)'
                      : 'rgba(31, 60, 136, 0.04)',
                  },
                }}
              >
                Play Recording
              </Button>
              <Button
                variant="outlined"
                startIcon={<ShareIcon />}
                sx={{
                  borderColor: isDark
                    ? brandColors.primary.signalTeal
                    : brandColors.primary.deepSafeBlue,
                  color: isDark
                    ? brandColors.primary.signalTeal
                    : brandColors.primary.deepSafeBlue,
                  backgroundColor: isDark
                    ? 'rgba(31, 182, 166, 0.1)'
                    : 'rgba(31, 60, 136, 0.05)',
                  '&:hover': {
                    borderColor: brandColors.primary.signalTeal,
                    backgroundColor: isDark
                      ? 'rgba(31, 182, 166, 0.2)'
                      : 'rgba(31, 60, 136, 0.1)',
                  },
                }}
              >
                Share with Team
              </Button>
              <Button
                variant="outlined"
                startIcon={<ReportIcon />}
                sx={{
                  borderColor: brandColors.primary.threatRed,
                  color: brandColors.primary.threatRed,
                  '&:hover': {
                    borderColor: brandColors.primary.threatRed,
                    backgroundColor: isDark
                      ? 'rgba(214, 69, 69, 0.08)'
                      : 'rgba(214, 69, 69, 0.04)',
                  },
                }}
              >
                Report to Authorities
              </Button>
            </Box>
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
};

export default MeetingDetailPage;
