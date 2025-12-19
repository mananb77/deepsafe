import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility as ViewIcon,
  FileDownload as ExportIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useThemeMode } from '../../context/ThemeContext';
import { MetricCard, RiskBadge } from '../../components/common';
import { brandColors } from '../../theme/colors';
import { allMeetings, filterMeetings } from '../../data';

export const MeetingsPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const { isDark } = useThemeMode();
  const [searchParams] = useSearchParams();

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<string>('compromised');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [startDate, setStartDate] = useState('2024-03-10');
  const [endDate, setEndDate] = useState('2024-04-10');

  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  // Apply filters
  const filteredMeetings = useMemo(() => {
    let meetings = filterMeetings(allMeetings, {
      startDate,
      endDate,
      riskCategory: riskFilter !== 'all' ? riskFilter : undefined,
      searchQuery: searchQuery || undefined,
      isCompromised: searchParams.get('filter') === 'compromised' ? true : undefined,
    });

    // Sort
    meetings = [...meetings].sort((a, b) => {
      switch (sortBy) {
        case 'compromised':
          if (a.isCompromised !== b.isCompromised) {
            return a.isCompromised ? -1 : 1;
          }
          return b.riskScore - a.riskScore;
        case 'riskScore':
          return b.riskScore - a.riskScore;
        case 'date':
          return new Date(b.meetingDate).getTime() - new Date(a.meetingDate).getTime();
        case 'name':
          return a.meetingName.localeCompare(b.meetingName);
        default:
          return 0;
      }
    });

    return meetings;
  }, [allMeetings, startDate, endDate, riskFilter, searchQuery, sortBy, searchParams]);

  // Pagination
  const paginatedMeetings = filteredMeetings.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // Calculate summary stats
  const stats = useMemo(() => {
    const compromised = filteredMeetings.filter((m) => m.isCompromised).length;
    const uniqueParticipants = new Set(
      filteredMeetings.flatMap((m) => m.participants.map((p) => p.id))
    ).size;
    const suspicious = new Set(
      filteredMeetings.flatMap((m) =>
        m.participants.filter((p) => p.isFlagged).map((p) => p.id)
      )
    ).size;

    return {
      total: filteredMeetings.length,
      uniqueParticipants,
      compromised,
      suspicious,
    };
  }, [filteredMeetings]);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'numeric',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const handleRowClick = (meetingId: string) => {
    navigate(`/app/meetings/${meetingId}`);
  };

  return (
    <Box>
      {/* Page Header */}
      <Typography
        variant="h4"
        sx={{
          fontFamily: '"Space Grotesk", sans-serif',
          fontWeight: 700,
          mb: 3,
          background: isDark
            ? `linear-gradient(90deg, ${brandColors.darkText.primary} 0%, ${brandColors.primary.signalTeal} 100%)`
            : `linear-gradient(90deg, ${brandColors.lightText.primary} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}
      >
        Meeting History
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 6, sm: 3 }}>
          <MetricCard title="Total Meetings Last Month" value={stats.total} />
        </Grid>
        <Grid size={{ xs: 6, sm: 3 }}>
          <MetricCard
            title="Total Unique Meeting Participants"
            value={stats.uniqueParticipants.toLocaleString()}
          />
        </Grid>
        <Grid size={{ xs: 6, sm: 3 }}>
          <MetricCard
            title="Total Compromised Meetings"
            value={stats.compromised}
            isAlert={stats.compromised > 0}
          />
        </Grid>
        <Grid size={{ xs: 6, sm: 3 }}>
          <MetricCard
            title="# Suspicious Users Detected"
            value={stats.suspicious}
            isAlert={stats.suspicious > 0}
          />
        </Grid>
      </Grid>

      {/* Filters */}
      <Card
        sx={{
          mb: 3,
          background: isDark
            ? theme.gradients.deepOcean
            : theme.gradients.blueGlass,
        }}
      >
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid size={{ xs: 12, sm: 4 }}>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <TextField
                  size="small"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  sx={{ width: 150 }}
                />
                <Typography color="text.secondary">To</Typography>
                <TextField
                  size="small"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  sx={{ width: 150 }}
                />
              </Box>
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
              <FormControl size="small" fullWidth>
                <InputLabel>Sort by</InputLabel>
                <Select
                  value={sortBy}
                  label="Sort by"
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <MenuItem value="compromised">Compromised Meetings</MenuItem>
                  <MenuItem value="riskScore">Risk Score (High-Low)</MenuItem>
                  <MenuItem value="date">Date (Newest First)</MenuItem>
                  <MenuItem value="name">Meeting Name (A-Z)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
              <FormControl size="small" fullWidth>
                <InputLabel>Filter by Risk</InputLabel>
                <Select
                  value={riskFilter}
                  label="Filter by Risk"
                  onChange={(e) => setRiskFilter(e.target.value)}
                >
                  <MenuItem value="all">All Risks</MenuItem>
                  <MenuItem value="critical">Critical (86-100%)</MenuItem>
                  <MenuItem value="high">High (61-85%)</MenuItem>
                  <MenuItem value="medium">Medium (31-60%)</MenuItem>
                  <MenuItem value="low">Low (0-30%)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, sm: 2 }}>
              <TextField
                size="small"
                placeholder="Search meetings..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon fontSize="small" />
                    </InputAdornment>
                  ),
                }}
                fullWidth
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Meetings Table */}
      <Card
        sx={{
          background: isDark
            ? theme.gradients.deepOcean
            : theme.gradients.blueGlass,
        }}
      >
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell width={40}></TableCell>
                <TableCell>MEETING ID</TableCell>
                <TableCell>MEETING NAME</TableCell>
                <TableCell>MEETING DATE</TableCell>
                <TableCell align="center">RISK SCORE</TableCell>
                <TableCell align="center">RISK CATEGORY</TableCell>
                <TableCell align="center">ACTIONS</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedMeetings.map((meeting) => (
                <TableRow
                  key={meeting.id}
                  hover
                  onClick={() => handleRowClick(meeting.id)}
                  sx={{
                    cursor: 'pointer',
                    backgroundColor: meeting.isCompromised
                      ? isDark
                        ? 'rgba(214, 69, 69, 0.1)'
                        : 'rgba(214, 69, 69, 0.05)'
                      : 'transparent',
                    '&:hover': {
                      backgroundColor: meeting.isCompromised
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
                    {(meeting.riskCategory === 'high' ||
                      meeting.riskCategory === 'critical') && (
                      <WarningIcon
                        sx={{
                          color:
                            meeting.riskCategory === 'critical'
                              ? brandColors.primary.threatRed
                              : statusColors.warning,
                          fontSize: 20,
                        }}
                      />
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: 500,
                        fontFamily: '"JetBrains Mono", monospace',
                        fontSize: '0.8125rem',
                      }}
                    >
                      {meeting.id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{meeting.meetingName}</Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{formatDate(meeting.meetingDate)}</Typography>
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
                    <RiskBadge category={meeting.riskCategory} />
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="View Details">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRowClick(meeting.id);
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
                    <Tooltip title="Export">
                      <IconButton
                        size="small"
                        onClick={(e) => e.stopPropagation()}
                        sx={{
                          color: 'text.secondary',
                          '&:hover': {
                            backgroundColor: isDark
                              ? 'rgba(255, 255, 255, 0.05)'
                              : 'rgba(0, 0, 0, 0.03)',
                          },
                        }}
                      >
                        <ExportIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={filteredMeetings.length}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          rowsPerPageOptions={[5, 10, 20, 50]}
          sx={{
            borderTop: `1px solid ${theme.customColors.borderColor}`,
          }}
        />
      </Card>
    </Box>
  );
};

export default MeetingsPage;
