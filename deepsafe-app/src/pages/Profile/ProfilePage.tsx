import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Avatar,
  Chip,
  Divider,
  Button,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Visibility as VisibilityIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  Timer as TimerIcon,
  CalendarToday as CalendarIcon,
  Computer as ComputerIcon,
  LocationOn as LocationIcon,
  TrendingUp as TrendingUpIcon,
  Shield as ShieldIcon,
  NotificationsActive as AlertIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useThemeMode } from '../../context/ThemeContext';
import { brandColors } from '../../theme/colors';
import { currentUser } from '../../data/user';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: string;
  color?: string;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, icon, trend, color }) => {
  const { isDark } = useThemeMode();

  return (
    <Paper
      sx={{
        p: 2.5,
        background: isDark
          ? 'linear-gradient(180deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.6) 100%)'
          : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.8) 100%)',
        backdropFilter: 'blur(10px)',
        border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
        borderRadius: 3,
        height: '100%',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', letterSpacing: 0.5 }}>
            {label}
          </Typography>
          <Typography
            variant="h4"
            sx={{
              fontFamily: '"JetBrains Mono", monospace',
              fontWeight: 700,
              color: color || (isDark ? brandColors.darkText.primary : brandColors.lightText.primary),
              mt: 0.5,
            }}
          >
            {value}
          </Typography>
          {trend && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
              <TrendingUpIcon sx={{ fontSize: 14, color: brandColors.statusDark.success }} />
              <Typography variant="caption" sx={{ color: brandColors.statusDark.success }}>
                {trend}
              </Typography>
            </Box>
          )}
        </Box>
        <Box
          sx={{
            p: 1,
            borderRadius: 2,
            background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}40 0%, ${brandColors.primary.signalTeal}40 100%)`,
          }}
        >
          {icon}
        </Box>
      </Box>
    </Paper>
  );
};

export const ProfilePage: React.FC = () => {
  const { isDark } = useThemeMode();
  const navigate = useNavigate();
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'view':
        return <VisibilityIcon fontSize="small" />;
      case 'report':
        return <AssessmentIcon fontSize="small" />;
      case 'setting':
        return <SettingsIcon fontSize="small" />;
      case 'action':
        return <CheckCircleIcon fontSize="small" />;
      default:
        return <VisibilityIcon fontSize="small" />;
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const date = new Date(timestamp);
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000 / 60);

    if (diff < 60) return `${diff} minutes ago`;
    if (diff < 1440) return `${Math.floor(diff / 60)} hours ago`;
    return `${Math.floor(diff / 1440)} days ago`;
  };

  return (
    <Box
      sx={{
        p: { xs: 2, md: 4 },
        maxWidth: 1200,
        mx: 'auto',
      }}
    >
      {/* Profile Header */}
      <Paper
        sx={{
          p: 4,
          mb: 3,
          background: isDark
            ? 'linear-gradient(135deg, rgba(31, 60, 136, 0.3) 0%, rgba(31, 182, 166, 0.2) 100%)'
            : 'linear-gradient(135deg, rgba(31, 60, 136, 0.1) 0%, rgba(31, 182, 166, 0.08) 100%)',
          backdropFilter: 'blur(10px)',
          border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.06)'}`,
          borderRadius: 4,
        }}
      >
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, alignItems: { xs: 'center', md: 'flex-start' }, gap: 3 }}>
          <Avatar
            sx={{
              width: 120,
              height: 120,
              fontSize: '2.5rem',
              fontWeight: 700,
              background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
              border: `4px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
              boxShadow: `0 8px 32px ${brandColors.primary.deepSafeBlue}40`,
            }}
          >
            {currentUser.initials}
          </Avatar>

          <Box sx={{ flex: 1, textAlign: { xs: 'center', md: 'left' } }}>
            <Typography
              variant="h4"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 700,
                mb: 0.5,
              }}
            >
              {currentUser.name}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
              {currentUser.email}
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: { xs: 'center', md: 'flex-start' }, mb: 2 }}>
              <Chip
                label={currentUser.role}
                size="small"
                sx={{
                  background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}30 0%, ${brandColors.primary.signalTeal}30 100%)`,
                  color: brandColors.primary.signalTeal,
                  fontWeight: 500,
                }}
              />
              <Chip
                label={currentUser.department}
                size="small"
                variant="outlined"
                sx={{ borderColor: isDark ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)' }}
              />
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap', justifyContent: { xs: 'center', md: 'flex-start' } }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <CalendarIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary">
                  Joined {new Date(currentUser.joinDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <TimerIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary">
                  Last login: {formatTimeAgo(currentUser.lastLogin)}
                </Typography>
              </Box>
            </Box>
          </Box>

          <Button
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={() => navigate('/app/settings')}
            sx={{
              borderColor: brandColors.primary.signalTeal,
              color: brandColors.primary.signalTeal,
              '&:hover': {
                borderColor: brandColors.primary.signalTeal,
                backgroundColor: `${brandColors.primary.signalTeal}10`,
              },
            }}
          >
            Edit Profile
          </Button>
        </Box>
      </Paper>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            label="Meetings Monitored"
            value={currentUser.stats.meetingsMonitored}
            icon={<VisibilityIcon sx={{ color: brandColors.primary.signalTeal }} />}
            trend="+12% this month"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            label="Incidents Detected"
            value={currentUser.stats.incidentsDetected}
            icon={<WarningIcon sx={{ color: brandColors.primary.alertAmber }} />}
            color={brandColors.primary.alertAmber}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            label="Avg Response Time"
            value={currentUser.stats.avgResponseTime}
            icon={<TimerIcon sx={{ color: brandColors.primary.signalTeal }} />}
            trend="2min faster than avg"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            label="Risk Alerts Handled"
            value={currentUser.stats.riskAlertsHandled}
            icon={<AlertIcon sx={{ color: brandColors.primary.deepSafeBlue }} />}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Activity */}
        <Grid size={{ xs: 12, md: 7 }}>
          <Paper
            sx={{
              p: 3,
              background: isDark
                ? 'linear-gradient(180deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.6) 100%)'
                : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.8) 100%)',
              backdropFilter: 'blur(10px)',
              border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
              borderRadius: 3,
              height: '100%',
            }}
          >
            <Typography
              variant="h6"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                mb: 2,
              }}
            >
              Recent Activity
            </Typography>
            <List disablePadding>
              {currentUser.recentActivity.map((activity, index) => (
                <React.Fragment key={activity.id}>
                  <ListItem
                    sx={{
                      px: 0,
                      py: 1.5,
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <Box
                        sx={{
                          p: 1,
                          borderRadius: 2,
                          background: isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.04)',
                        }}
                      >
                        {getActivityIcon(activity.type)}
                      </Box>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body2" fontWeight={500}>
                          {activity.action}
                        </Typography>
                      }
                      secondary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            {activity.target}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatTimeAgo(activity.timestamp)}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < currentUser.recentActivity.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Security Status */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Paper
            sx={{
              p: 3,
              background: isDark
                ? 'linear-gradient(180deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.6) 100%)'
                : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.8) 100%)',
              backdropFilter: 'blur(10px)',
              border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
              borderRadius: 3,
              mb: 3,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
              <Box
                sx={{
                  p: 1,
                  borderRadius: 2,
                  background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                }}
              >
                <ShieldIcon sx={{ color: '#fff', fontSize: 20 }} />
              </Box>
              <Typography
                variant="h6"
                sx={{
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 600,
                }}
              >
                Security Status
              </Typography>
            </Box>

            {/* Security Score */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Account Security
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    fontFamily: '"JetBrains Mono", monospace',
                    fontWeight: 600,
                    color: statusColors.success,
                  }}
                >
                  Strong
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={85}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 4,
                    background: `linear-gradient(90deg, ${brandColors.primary.signalTeal} 0%, ${statusColors.success} 100%)`,
                  },
                }}
              />
            </Box>

            {/* Security Items */}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SecurityIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                  <Typography variant="body2">Two-Factor Auth</Typography>
                </Box>
                <Chip
                  icon={<CheckCircleIcon sx={{ fontSize: 14 }} />}
                  label="Enabled"
                  size="small"
                  sx={{
                    backgroundColor: `${statusColors.success}20`,
                    color: statusColors.success,
                    '& .MuiChip-icon': { color: statusColors.success },
                  }}
                />
              </Box>

              <Divider />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CalendarIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                  <Typography variant="body2">Password Changed</Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {new Date(currentUser.security.lastPasswordChange).toLocaleDateString()}
                </Typography>
              </Box>

              <Divider />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ComputerIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                  <Typography variant="body2">Active Sessions</Typography>
                </Box>
                <Chip
                  label={`${currentUser.security.activeSessions} devices`}
                  size="small"
                  variant="outlined"
                  sx={{ borderColor: isDark ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)' }}
                />
              </Box>
            </Box>
          </Paper>

          {/* Login History */}
          <Paper
            sx={{
              p: 3,
              background: isDark
                ? 'linear-gradient(180deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.6) 100%)'
                : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.8) 100%)',
              backdropFilter: 'blur(10px)',
              border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
              borderRadius: 3,
            }}
          >
            <Typography
              variant="h6"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                mb: 2,
              }}
            >
              Login History
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {currentUser.security.loginHistory.map((login, index) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    p: 1.5,
                    borderRadius: 2,
                    background: login.status === 'failed'
                      ? `${brandColors.primary.threatRed}10`
                      : isDark ? 'rgba(255, 255, 255, 0.03)' : 'rgba(0, 0, 0, 0.02)',
                    border: `1px solid ${
                      login.status === 'failed'
                        ? `${brandColors.primary.threatRed}30`
                        : isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)'
                    }`,
                  }}
                >
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <ComputerIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                      <Typography variant="caption" fontWeight={500}>
                        {login.device}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                      <LocationIcon sx={{ fontSize: 12, color: 'text.secondary' }} />
                      <Typography variant="caption" color="text.secondary">
                        {login.location}
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ textAlign: 'right' }}>
                    <Tooltip title={login.status === 'failed' ? 'Failed login attempt' : 'Successful login'}>
                      {login.status === 'success' ? (
                        <CheckCircleIcon sx={{ fontSize: 16, color: statusColors.success }} />
                      ) : (
                        <WarningIcon sx={{ fontSize: 16, color: brandColors.primary.threatRed }} />
                      )}
                    </Tooltip>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {formatTimeAgo(login.timestamp)}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProfilePage;
