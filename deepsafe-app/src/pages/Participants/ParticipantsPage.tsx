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
  Chip,
  useTheme,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useThemeMode } from '../../context/ThemeContext';
import { TrustBadge, RiskIndicator } from '../../components/common';
import { brandColors } from '../../theme/colors';
import { allParticipants, filterParticipants } from '../../data';
import type { ParticipantStatus } from '../../types';

const getStatusChip = (status: ParticipantStatus, isDark: boolean) => {
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  switch (status) {
    case 'blacklisted':
      return (
        <Chip
          label="BLACKLISTED"
          size="small"
          sx={{
            background: `linear-gradient(135deg, ${brandColors.primary.threatRed} 0%, #8B2525 100%)`,
            color: 'white',
            fontWeight: 600,
            fontSize: '0.6875rem',
          }}
        />
      );
    case 'verified':
      return (
        <Chip
          label="VERIFIED"
          size="small"
          sx={{
            background: isDark
              ? 'linear-gradient(135deg, rgba(58, 214, 163, 0.2) 0%, rgba(45, 190, 139, 0.3) 100%)'
              : 'rgba(45, 190, 139, 0.15)',
            color: statusColors.success,
            fontWeight: 600,
            fontSize: '0.6875rem',
            border: `1px solid ${isDark ? 'rgba(58, 214, 163, 0.3)' : 'rgba(45, 190, 139, 0.3)'}`,
          }}
        />
      );
    case 'flagged':
      return (
        <Chip
          label="FLAGGED"
          size="small"
          sx={{
            background: isDark
              ? 'linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(214, 69, 69, 0.3) 100%)'
              : 'rgba(214, 69, 69, 0.1)',
            color: statusColors.error,
            fontWeight: 600,
            fontSize: '0.6875rem',
            border: `1px solid ${isDark ? 'rgba(255, 107, 107, 0.3)' : 'rgba(214, 69, 69, 0.3)'}`,
          }}
        />
      );
    case 'external':
      return (
        <Chip
          label="EXTERNAL"
          size="small"
          sx={{
            background: isDark
              ? 'rgba(255, 255, 255, 0.1)'
              : 'rgba(0, 0, 0, 0.08)',
            color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
            fontWeight: 600,
            fontSize: '0.6875rem',
            border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.12)'}`,
          }}
        />
      );
    case 'guest':
    default:
      return (
        <Chip
          label="GUEST"
          size="small"
          sx={{
            background: isDark
              ? 'linear-gradient(135deg, rgba(255, 200, 87, 0.2) 0%, rgba(245, 166, 35, 0.3) 100%)'
              : 'rgba(245, 166, 35, 0.15)',
            color: statusColors.warning,
            fontWeight: 600,
            fontSize: '0.6875rem',
            border: `1px solid ${isDark ? 'rgba(255, 200, 87, 0.3)' : 'rgba(245, 166, 35, 0.3)'}`,
          }}
        />
      );
  }
};

export const ParticipantsPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const { isDark } = useThemeMode();
  const [searchParams] = useSearchParams();

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<string>('riskScore');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  // Apply filters
  const filteredParticipants = useMemo(() => {
    let participants = filterParticipants(allParticipants, {
      status: statusFilter !== 'all' ? statusFilter : undefined,
      searchQuery: searchQuery || undefined,
      hasIncidents: searchParams.get('filter') === 'flagged' ? true : undefined,
    });

    // Sort
    participants = [...participants].sort((a, b) => {
      switch (sortBy) {
        case 'riskScore':
          return b.riskScore - a.riskScore;
        case 'trustScore':
          return a.trustScore - b.trustScore;
        case 'name':
          return a.name.localeCompare(b.name);
        case 'totalMeetings':
          return b.totalMeetings - a.totalMeetings;
        case 'lastSeen':
          return new Date(b.lastSeen).getTime() - new Date(a.lastSeen).getTime();
        default:
          return 0;
      }
    });

    return participants;
  }, [allParticipants, statusFilter, searchQuery, sortBy, searchParams]);

  // Pagination
  const paginatedParticipants = filteredParticipants.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const handleRowClick = (participantId: string) => {
    navigate(`/participants/${participantId}`);
  };

  return (
    <Box>
      {/* Page Header */}
      <Typography
        variant="h4"
        sx={{
          fontFamily: '"Space Grotesk", sans-serif',
          fontWeight: 700,
          mb: 1,
          background: isDark
            ? `linear-gradient(90deg, ${brandColors.darkText.primary} 0%, ${brandColors.primary.signalTeal} 100%)`
            : `linear-gradient(90deg, ${brandColors.lightText.primary} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}
      >
        Participant History
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Track and analyze individual participant behavior
      </Typography>

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
              <TextField
                size="small"
                placeholder="Search by name, email, or ID..."
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
            <Grid size={{ xs: 12, sm: 3 }}>
              <FormControl size="small" fullWidth>
                <InputLabel>Filter by Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Filter by Status"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="all">All Participants</MenuItem>
                  <MenuItem value="verified">Verified</MenuItem>
                  <MenuItem value="blacklisted">Blacklisted</MenuItem>
                  <MenuItem value="flagged">Flagged</MenuItem>
                  <MenuItem value="external">External</MenuItem>
                  <MenuItem value="guest">Guest</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
              <FormControl size="small" fullWidth>
                <InputLabel>Sort by</InputLabel>
                <Select
                  value={sortBy}
                  label="Sort by"
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <MenuItem value="riskScore">Risk Score (High-Low)</MenuItem>
                  <MenuItem value="trustScore">Trust Score (Low-High)</MenuItem>
                  <MenuItem value="name">Name (A-Z)</MenuItem>
                  <MenuItem value="totalMeetings">Meeting Count</MenuItem>
                  <MenuItem value="lastSeen">Last Seen</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Participants List */}
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
                <TableCell>STATUS</TableCell>
                <TableCell>PARTICIPANT</TableCell>
                <TableCell align="center">RISK SCORE</TableCell>
                <TableCell align="center">MEETINGS</TableCell>
                <TableCell align="center">INCIDENTS</TableCell>
                <TableCell>LAST SEEN</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedParticipants.map((participant) => (
                <TableRow
                  key={participant.id}
                  hover
                  onClick={() => handleRowClick(participant.id)}
                  sx={{
                    cursor: 'pointer',
                    backgroundColor:
                      participant.status === 'blacklisted' ||
                      participant.status === 'flagged'
                        ? isDark
                          ? 'rgba(214, 69, 69, 0.1)'
                          : 'rgba(214, 69, 69, 0.05)'
                        : 'transparent',
                    '&:hover': {
                      backgroundColor:
                        participant.status === 'blacklisted' ||
                        participant.status === 'flagged'
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
                    <TrustBadge status={participant.status} />
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight={600}>
                        {participant.name}
                        {participant.status === 'blacklisted' && ' '}
                        {participant.status === 'blacklisted' &&
                          getStatusChip(participant.status, isDark)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {participant.email}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'center' }}>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 700,
                          fontFamily: '"JetBrains Mono", monospace',
                          color:
                            participant.riskScore >= 86
                              ? brandColors.primary.threatRed
                              : participant.riskScore >= 60
                                ? statusColors.error
                                : 'inherit',
                        }}
                      >
                        {participant.riskScore}%
                      </Typography>
                      <Box sx={{ width: 60 }}>
                        <RiskIndicator
                          score={participant.riskScore}
                          showLabel={false}
                          showPercentage={false}
                          size="small"
                        />
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Typography
                      variant="body2"
                      sx={{ fontFamily: '"JetBrains Mono", monospace' }}
                    >
                      {participant.totalMeetings}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    {participant.compromisedMeetings > 0 ? (
                      <Chip
                        label={participant.compromisedMeetings}
                        size="small"
                        sx={{
                          background: isDark
                            ? 'linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(214, 69, 69, 0.3) 100%)'
                            : 'rgba(214, 69, 69, 0.1)',
                          color: statusColors.error,
                          fontWeight: 600,
                          fontFamily: '"JetBrains Mono", monospace',
                          border: `1px solid ${isDark ? 'rgba(255, 107, 107, 0.3)' : 'rgba(214, 69, 69, 0.3)'}`,
                        }}
                      />
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        0
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>{formatDate(participant.lastSeen)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={filteredParticipants.length}
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

export default ParticipantsPage;
