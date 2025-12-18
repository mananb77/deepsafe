import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Divider,
  Slider,
  Chip,
  IconButton,
  Alert,
  Snackbar,
  Tooltip,
  InputAdornment,
  FormControl,
  InputLabel,
  Grid,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Palette as PaletteIcon,
  IntegrationInstructions as IntegrationsIcon,
  Person as PersonIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  ContentCopy as CopyIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Link as LinkIcon,
  LinkOff as LinkOffIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../context/ThemeContext';
import { brandColors } from '../../theme/colors';
import { currentUser } from '../../data/user';

interface SettingsSectionProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}

const SettingsSection: React.FC<SettingsSectionProps> = ({ title, icon, children }) => {
  const { isDark } = useThemeMode();

  return (
    <Paper
      sx={{
        p: 3,
        mb: 3,
        background: isDark
          ? 'linear-gradient(180deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.6) 100%)'
          : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.8) 100%)',
        backdropFilter: 'blur(10px)',
        border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
        borderRadius: 3,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <Box
          sx={{
            p: 1,
            borderRadius: 2,
            background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {icon}
        </Box>
        <Typography
          variant="h6"
          sx={{
            fontFamily: '"Space Grotesk", sans-serif',
            fontWeight: 600,
          }}
        >
          {title}
        </Typography>
      </Box>
      {children}
    </Paper>
  );
};

export const SettingsPage: React.FC = () => {
  const { isDark, toggleTheme } = useThemeMode();

  // Local state for settings
  const [settings, setSettings] = useState({
    // Notification settings
    emailCritical: currentUser.preferences.emailNotifications.criticalIncidents,
    emailDaily: currentUser.preferences.emailNotifications.dailySummary,
    emailWeekly: currentUser.preferences.emailNotifications.weeklyReports,
    emailUpdates: currentUser.preferences.emailNotifications.systemUpdates,
    inAppNotifications: currentUser.preferences.inAppNotifications,
    alertThreshold: currentUser.preferences.alertThreshold,

    // Security settings
    twoFactorEnabled: currentUser.security.twoFactorEnabled,
    sessionTimeout: 30,

    // Display settings
    dateFormat: currentUser.preferences.dateFormat,
    defaultView: currentUser.preferences.defaultDashboardView,
  });

  const [showApiKey, setShowApiKey] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  const apiKey = 'ds_live_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx';

  const handleSwitchChange = (key: keyof typeof settings) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setSettings((prev) => ({ ...prev, [key]: event.target.checked }));
  };

  const handleSelectChange = (key: keyof typeof settings) => (event: { target: { value: string } }) => {
    setSettings((prev) => ({ ...prev, [key]: event.target.value }));
  };

  const handleSliderChange = (_: Event, value: number | number[]) => {
    setSettings((prev) => ({ ...prev, alertThreshold: value as number }));
  };

  const handleSave = () => {
    setSnackbar({ open: true, message: 'Settings saved successfully', severity: 'success' });
  };

  const handleCopyApiKey = () => {
    navigator.clipboard.writeText(apiKey);
    setSnackbar({ open: true, message: 'API key copied to clipboard', severity: 'success' });
  };

  const integrations = [
    { name: 'Zoom', connected: currentUser.integrations.zoom.connected, lastSync: currentUser.integrations.zoom.lastSync },
    { name: 'Microsoft Teams', connected: currentUser.integrations.teams.connected, lastSync: currentUser.integrations.teams.lastSync },
    { name: 'Google Meet', connected: currentUser.integrations.googleMeet.connected, lastSync: currentUser.integrations.googleMeet.lastSync },
    { name: 'Slack', connected: currentUser.integrations.slack.connected, lastSync: currentUser.integrations.slack.lastSync },
  ];

  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  return (
    <Box
      sx={{
        p: { xs: 2, md: 4 },
        maxWidth: 900,
        mx: 'auto',
      }}
    >
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          sx={{
            fontFamily: '"Space Grotesk", sans-serif',
            fontWeight: 700,
            mb: 1,
            background: isDark
              ? 'linear-gradient(90deg, #E6ECF5 0%, #B8C3D9 100%)'
              : 'linear-gradient(90deg, #0B1B3A 0%, #1F3C88 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your account preferences and security settings
        </Typography>
      </Box>

      {/* Profile Settings */}
      <SettingsSection title="Profile Settings" icon={<PersonIcon sx={{ color: '#fff', fontSize: 20 }} />}>
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Display Name"
              defaultValue={currentUser.name}
              variant="outlined"
              size="small"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Email"
              defaultValue={currentUser.email}
              variant="outlined"
              size="small"
              disabled
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Role"
              defaultValue={currentUser.role}
              variant="outlined"
              size="small"
              disabled
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Department"
              defaultValue={currentUser.department}
              variant="outlined"
              size="small"
              disabled
            />
          </Grid>
        </Grid>
      </SettingsSection>

      {/* Notification Settings */}
      <SettingsSection title="Notification Settings" icon={<NotificationsIcon sx={{ color: '#fff', fontSize: 20 }} />}>
        <Typography variant="subtitle2" sx={{ mb: 2, color: 'text.secondary' }}>
          Email Notifications
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.emailCritical}
                onChange={handleSwitchChange('emailCritical')}
                color="primary"
              />
            }
            label={
              <Box>
                <Typography variant="body2">Critical Incidents</Typography>
                <Typography variant="caption" color="text.secondary">
                  Immediate alerts for high-risk detections
                </Typography>
              </Box>
            }
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.emailDaily}
                onChange={handleSwitchChange('emailDaily')}
                color="primary"
              />
            }
            label={
              <Box>
                <Typography variant="body2">Daily Summary</Typography>
                <Typography variant="caption" color="text.secondary">
                  Daily digest of all monitored meetings
                </Typography>
              </Box>
            }
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.emailWeekly}
                onChange={handleSwitchChange('emailWeekly')}
                color="primary"
              />
            }
            label={
              <Box>
                <Typography variant="body2">Weekly Reports</Typography>
                <Typography variant="caption" color="text.secondary">
                  Weekly analytics and trend reports
                </Typography>
              </Box>
            }
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.emailUpdates}
                onChange={handleSwitchChange('emailUpdates')}
                color="primary"
              />
            }
            label={
              <Box>
                <Typography variant="body2">System Updates</Typography>
                <Typography variant="caption" color="text.secondary">
                  Product updates and new features
                </Typography>
              </Box>
            }
          />
        </Box>

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" sx={{ mb: 2, color: 'text.secondary' }}>
          In-App Notifications
        </Typography>
        <FormControlLabel
          control={
            <Switch
              checked={settings.inAppNotifications}
              onChange={handleSwitchChange('inAppNotifications')}
              color="primary"
            />
          }
          label="Enable in-app notifications"
        />

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" sx={{ mb: 2, color: 'text.secondary' }}>
          Alert Threshold
        </Typography>
        <Box sx={{ px: 2 }}>
          <Slider
            value={settings.alertThreshold}
            onChange={handleSliderChange}
            min={0}
            max={100}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value}%`}
            marks={[
              { value: 0, label: '0%' },
              { value: 50, label: '50%' },
              { value: 100, label: '100%' },
            ]}
            sx={{
              '& .MuiSlider-thumb': {
                background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
              },
              '& .MuiSlider-track': {
                background: `linear-gradient(90deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
              },
            }}
          />
          <Typography variant="caption" color="text.secondary">
            You'll receive alerts when risk confidence exceeds this threshold
          </Typography>
        </Box>
      </SettingsSection>

      {/* Security Settings */}
      <SettingsSection title="Security Settings" icon={<SecurityIcon sx={{ color: '#fff', fontSize: 20 }} />}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="body2" fontWeight={500}>
                Two-Factor Authentication
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Add an extra layer of security to your account
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {settings.twoFactorEnabled && (
                <Chip
                  icon={<CheckCircleIcon sx={{ fontSize: 16 }} />}
                  label="Enabled"
                  size="small"
                  sx={{
                    backgroundColor: `${statusColors.success}20`,
                    color: statusColors.success,
                  }}
                />
              )}
              <Switch
                checked={settings.twoFactorEnabled}
                onChange={handleSwitchChange('twoFactorEnabled')}
                color="primary"
              />
            </Box>
          </Box>

          <Divider />

          <Box>
            <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
              Session Timeout
            </Typography>
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Timeout Duration</InputLabel>
              <Select
                value={settings.sessionTimeout}
                label="Timeout Duration"
                onChange={(e) => setSettings((prev) => ({ ...prev, sessionTimeout: e.target.value as number }))}
              >
                <MenuItem value={15}>15 minutes</MenuItem>
                <MenuItem value={30}>30 minutes</MenuItem>
                <MenuItem value={60}>1 hour</MenuItem>
                <MenuItem value={120}>2 hours</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Divider />

          <Box>
            <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
              API Key
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                size="small"
                type={showApiKey ? 'text' : 'password'}
                value={apiKey}
                InputProps={{
                  readOnly: true,
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton size="small" onClick={() => setShowApiKey(!showApiKey)}>
                        {showApiKey ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
                      </IconButton>
                    </InputAdornment>
                  ),
                  sx: { fontFamily: '"JetBrains Mono", monospace', fontSize: '0.875rem' },
                }}
              />
              <Tooltip title="Copy API key">
                <IconButton onClick={handleCopyApiKey}>
                  <CopyIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Regenerate API key">
                <IconButton>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              Use this key to authenticate API requests
            </Typography>
          </Box>
        </Box>
      </SettingsSection>

      {/* Display Preferences */}
      <SettingsSection title="Display Preferences" icon={<PaletteIcon sx={{ color: '#fff', fontSize: 20 }} />}>
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="body2" fontWeight={500}>
                  Dark Mode
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Switch between light and dark themes
                </Typography>
              </Box>
              <Switch
                checked={isDark}
                onChange={toggleTheme}
                color="primary"
              />
            </Box>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Date Format</InputLabel>
              <Select
                value={settings.dateFormat}
                label="Date Format"
                onChange={handleSelectChange('dateFormat')}
              >
                <MenuItem value="MM/DD/YYYY">MM/DD/YYYY</MenuItem>
                <MenuItem value="DD/MM/YYYY">DD/MM/YYYY</MenuItem>
                <MenuItem value="YYYY-MM-DD">YYYY-MM-DD</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Default Dashboard View</InputLabel>
              <Select
                value={settings.defaultView}
                label="Default Dashboard View"
                onChange={handleSelectChange('defaultView')}
              >
                <MenuItem value="overview">Overview</MenuItem>
                <MenuItem value="meetings">Meetings</MenuItem>
                <MenuItem value="incidents">Incidents</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </SettingsSection>

      {/* Integration Settings */}
      <SettingsSection title="Integrations" icon={<IntegrationsIcon sx={{ color: '#fff', fontSize: 20 }} />}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {integrations.map((integration) => (
            <Box
              key={integration.name}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                p: 2,
                borderRadius: 2,
                background: isDark ? 'rgba(255, 255, 255, 0.03)' : 'rgba(0, 0, 0, 0.02)',
                border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)'}`,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {integration.connected ? (
                  <LinkIcon sx={{ color: statusColors.success }} />
                ) : (
                  <LinkOffIcon sx={{ color: 'text.secondary' }} />
                )}
                <Box>
                  <Typography variant="body2" fontWeight={500}>
                    {integration.name}
                  </Typography>
                  {integration.connected && integration.lastSync && (
                    <Typography variant="caption" color="text.secondary">
                      Last synced: {new Date(integration.lastSync).toLocaleString()}
                    </Typography>
                  )}
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {integration.connected ? (
                  <>
                    <Chip
                      label="Connected"
                      size="small"
                      sx={{
                        backgroundColor: `${statusColors.success}20`,
                        color: statusColors.success,
                      }}
                    />
                    <Button size="small" color="error" variant="outlined">
                      Disconnect
                    </Button>
                  </>
                ) : (
                  <Button
                    size="small"
                    variant="contained"
                    sx={{
                      background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                    }}
                  >
                    Connect
                  </Button>
                )}
              </Box>
            </Box>
          ))}
        </Box>

        <Divider sx={{ my: 3 }} />

        <Box>
          <Typography variant="subtitle2" sx={{ mb: 2, color: 'text.secondary' }}>
            Webhook URL
          </Typography>
          <TextField
            fullWidth
            size="small"
            placeholder="https://your-webhook-endpoint.com/deepsafe"
            InputProps={{
              sx: { fontFamily: '"JetBrains Mono", monospace', fontSize: '0.875rem' },
            }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
            Receive real-time alerts via webhook
          </Typography>
        </Box>

        <Divider sx={{ my: 3 }} />

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" fontWeight={500}>
              SSO Configuration
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Single Sign-On is configured for your organization
            </Typography>
          </Box>
          <Chip
            icon={<CheckCircleIcon sx={{ fontSize: 16 }} />}
            label="Active"
            size="small"
            sx={{
              backgroundColor: `${statusColors.success}20`,
              color: statusColors.success,
            }}
          />
        </Box>
      </SettingsSection>

      {/* Save Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 2 }}>
        <Button variant="outlined">Cancel</Button>
        <Button
          variant="contained"
          onClick={handleSave}
          sx={{
            background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
            '&:hover': {
              background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
            },
          }}
        >
          Save Changes
        </Button>
      </Box>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          severity={snackbar.severity}
          onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SettingsPage;
