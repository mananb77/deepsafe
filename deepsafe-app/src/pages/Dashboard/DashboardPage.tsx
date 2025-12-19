import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  Button,
  useTheme,
} from '@mui/material';
import {
  Search as SearchIcon,
  FileDownload as ExportIcon,
  Settings as SettingsIcon,
  VideoCall as VideoCallIcon,
  People as PeopleIcon,
  AttachMoney as MoneyIcon,
  Timer as TimerIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useThemeMode } from '../../context/ThemeContext';
import { MetricCard } from '../../components/common';
import { RiskTrendChart, RecentIncidents } from '../../components/features/dashboard';
import { brandColors } from '../../theme/colors';
import { dashboardMetrics, riskTrendData, recentIncidents, dateRangePresets } from '../../data';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const { isDark } = useThemeMode();
  const [dateRange, setDateRange] = useState('30');

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <Box>
      {/* Page Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
        }}
      >
        <Box>
          <Typography
            variant="h4"
            sx={{
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 700,
              background: isDark
                ? `linear-gradient(90deg, ${brandColors.darkText.primary} 0%, ${brandColors.primary.signalTeal} 100%)`
                : `linear-gradient(90deg, ${brandColors.lightText.primary} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            Overview
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Monitor your organization's security posture
          </Typography>
        </Box>
        <FormControl
          size="small"
          sx={{
            minWidth: 160,
            '& .MuiOutlinedInput-root': {
              backgroundColor: isDark
                ? 'rgba(255, 255, 255, 0.05)'
                : 'rgba(255, 255, 255, 0.8)',
              backdropFilter: 'blur(10px)',
              '& fieldset': {
                borderColor: theme.customColors.borderColor,
              },
            },
          }}
        >
          <Select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
          >
            {dateRangePresets.map((preset) => (
              <MenuItem key={preset.label} value={preset.days.toString()}>
                {preset.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }} data-walkthrough="metrics">
        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <Box data-walkthrough="metric-total-meetings" sx={{ height: '100%' }}>
            <MetricCard
              title="Total Meetings Last Month"
              value={dashboardMetrics.totalMeetings}
              trend={{
                value: dashboardMetrics.totalMeetingsTrend,
                direction: dashboardMetrics.totalMeetingsTrend > 0 ? 'up' : 'down',
                label: 'vs prev',
                isPositive: true,
              }}
              icon={<VideoCallIcon />}
              onClick={() => navigate('/app/meetings')}
            />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <MetricCard
            title="Unique Participants"
            value={dashboardMetrics.uniqueParticipants.toLocaleString()}
            trend={{
              value: dashboardMetrics.uniqueParticipantsTrend,
              direction: dashboardMetrics.uniqueParticipantsTrend > 0 ? 'up' : 'down',
              label: '% vs prev',
              isPositive: true,
            }}
            icon={<PeopleIcon />}
            onClick={() => navigate('/app/participants')}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <Box data-walkthrough="metric-compromised" sx={{ height: '100%' }}>
            <MetricCard
              title="Compromised Meetings"
              value={dashboardMetrics.compromisedMeetings}
              isAlert={dashboardMetrics.compromisedMeetings > 0}
              trend={{
                value: dashboardMetrics.compromisedMeetingsTrend,
                direction: dashboardMetrics.compromisedMeetingsTrend > 0 ? 'up' : 'down',
                label: 'vs prev',
                isPositive: dashboardMetrics.compromisedMeetingsTrend <= 0,
              }}
              onClick={() => navigate('/app/meetings?filter=compromised')}
            />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <MetricCard
            title="Suspicious Users"
            value={dashboardMetrics.suspiciousUsers}
            isAlert={dashboardMetrics.suspiciousUsers > 0}
            trend={{
              value: dashboardMetrics.suspiciousUsersTrend,
              direction: dashboardMetrics.suspiciousUsersTrend > 0 ? 'up' : 'down',
              label: 'vs prev',
              isPositive: dashboardMetrics.suspiciousUsersTrend <= 0,
            }}
            onClick={() => navigate('/app/participants?filter=flagged')}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <Box data-walkthrough="metric-money" sx={{ height: '100%' }}>
            <MetricCard
              title="Money Protected"
              value={formatCurrency(dashboardMetrics.totalMoneyProtected)}
              trend={{
                value: Number((dashboardMetrics.totalMoneyProtectedTrend / 1000).toFixed(0)),
                direction: 'up',
                label: 'K',
                isPositive: true,
              }}
              icon={<MoneyIcon />}
            />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <MetricCard
            title="Avg Response Time"
            value={`${dashboardMetrics.avgResponseTime} min`}
            trend={{
              value: dashboardMetrics.avgResponseTimeTrend,
              direction: dashboardMetrics.avgResponseTimeTrend < 0 ? 'down' : 'up',
              label: 'min',
              isPositive: dashboardMetrics.avgResponseTimeTrend < 0,
            }}
            icon={<TimerIcon />}
          />
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, lg: 8 }}>
          <Card
            data-walkthrough="chart"
            sx={{
              background: isDark
                ? theme.gradients.deepOcean
                : theme.gradients.blueGlass,
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 600,
                  mb: 1,
                  fontFamily: '"Space Grotesk", sans-serif',
                }}
              >
                Risk Trend Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Average risk score over time with critical alerts highlighted
              </Typography>
              <RiskTrendChart data={riskTrendData} height={320} />
              <Box
                sx={{
                  display: 'flex',
                  gap: 4,
                  mt: 3,
                  justifyContent: 'center',
                  p: 2,
                  borderRadius: 2,
                  background: isDark
                    ? 'rgba(255, 255, 255, 0.03)'
                    : 'rgba(0, 0, 0, 0.02)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
                      boxShadow: `0 0 8px ${brandColors.primary.signalTeal}60`,
                    }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    Avg Risk Score
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      backgroundColor: brandColors.primary.threatRed,
                      boxShadow: `0 0 8px ${brandColors.primary.threatRed}60`,
                    }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    Critical Alerts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, lg: 4 }}>
          <Box data-walkthrough="incidents">
            <RecentIncidents incidents={recentIncidents} />
          </Box>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Card
        sx={{
          background: isDark
            ? theme.gradients.deepOcean
            : theme.gradients.blueGlass,
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 600,
              mb: 2.5,
              fontFamily: '"Space Grotesk", sans-serif',
            }}
          >
            Quick Actions
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="outlined"
              startIcon={<SearchIcon />}
              onClick={() => navigate('/app/meetings')}
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
              Search Meetings
            </Button>
            <Button
              variant="outlined"
              startIcon={<ExportIcon />}
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
              Export Report
            </Button>
            <Button
              variant="outlined"
              startIcon={<SettingsIcon />}
              onClick={() => navigate('/app/settings')}
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
              Configure Alerts
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DashboardPage;
