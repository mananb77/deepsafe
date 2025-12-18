import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Box,
  Divider,
  ListItemIcon,
  ListItemText,
  Popover,
  List,
  ListItem,
  ListItemButton,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useThemeMode } from '../../context/ThemeContext';
import { brandColors } from '../../theme/colors';
import type { Alert } from '../../types';
import { alerts } from '../../data';

// DeepSafe Logo component
const DeepSafeLogo: React.FC = () => {
  const { isDark } = useThemeMode();

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
      <Box
        sx={{
          width: 40,
          height: 40,
          borderRadius: '12px',
          background: isDark
            ? 'linear-gradient(135deg, #1F3C88 0%, #1FB6A6 100%)'
            : 'linear-gradient(135deg, #1F3C88 0%, #3A6EDC 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: isDark
            ? '0 4px 12px rgba(31, 60, 136, 0.4)'
            : '0 2px 8px rgba(31, 60, 136, 0.2)',
        }}
      >
        <SecurityIcon sx={{ color: '#FFFFFF', fontSize: 22 }} />
      </Box>
      <Typography
        variant="h6"
        sx={{
          fontFamily: '"Space Grotesk", sans-serif',
          fontWeight: 700,
          fontSize: '1.25rem',
          letterSpacing: '-0.02em',
          background: isDark
            ? 'linear-gradient(90deg, #E6ECF5 0%, #B8C3D9 100%)'
            : 'linear-gradient(90deg, #0B1B3A 0%, #1F3C88 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}
      >
        DeepSafe
      </Typography>
    </Box>
  );
};

interface NavLinkProps {
  label: string;
  path: string;
  isActive: boolean;
  onClick: () => void;
}

const NavLink: React.FC<NavLinkProps> = ({ label, isActive, onClick }) => {
  const { isDark } = useThemeMode();

  return (
    <Box
      onClick={onClick}
      sx={{
        px: 2,
        py: 1,
        cursor: 'pointer',
        borderRadius: '8px',
        position: 'relative',
        color: isDark
          ? isActive ? brandColors.darkText.primary : brandColors.darkText.secondary
          : isActive ? brandColors.lightText.primary : brandColors.lightText.secondary,
        fontWeight: isActive ? 600 : 500,
        fontSize: '0.9375rem',
        transition: 'all 0.2s ease',
        '&::after': {
          content: '""',
          position: 'absolute',
          bottom: -2,
          left: '50%',
          transform: 'translateX(-50%)',
          width: isActive ? '60%' : '0%',
          height: 2,
          background: `linear-gradient(90deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
          borderRadius: 1,
          transition: 'width 0.2s ease',
        },
        '&:hover': {
          color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
          backgroundColor: isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.04)',
          '&::after': {
            width: '60%',
          },
        },
      }}
    >
      {label}
    </Box>
  );
};

const getAlertIcon = (type: Alert['type'], isDark: boolean) => {
  const colors = isDark ? brandColors.statusDark : brandColors.statusLight;

  switch (type) {
    case 'critical':
      return <ErrorIcon sx={{ color: brandColors.primary.threatRed }} />;
    case 'warning':
      return <WarningIcon sx={{ color: colors.warning }} />;
    case 'success':
      return <CheckCircleIcon sx={{ color: colors.success }} />;
    default:
      return <InfoIcon sx={{ color: colors.info }} />;
  }
};

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const { toggleTheme, isDark } = useThemeMode();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationAnchorEl, setNotificationAnchorEl] = useState<null | HTMLElement>(null);

  const currentPath = window.location.pathname;

  const navLinks = [
    { label: 'Summary', path: '/' },
    { label: 'Meeting History', path: '/meetings' },
    { label: 'Participant History', path: '/participants' },
    { label: 'Support', path: '/support' },
  ];

  const handleProfileClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchorEl(event.currentTarget);
  };

  const handleNotificationClose = () => {
    setNotificationAnchorEl(null);
  };

  const unreadCount = alerts.filter((a) => !a.isRead).length;

  return (
    <AppBar
      position="fixed"
      sx={{
        background: theme.gradients.header,
        zIndex: (t) => t.zIndex.drawer + 1,
        backdropFilter: 'blur(10px)',
        borderBottom: `1px solid ${theme.customColors.borderColor}`,
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, md: 3 } }}>
        {/* Left side - Logo and Navigation */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <Box
            onClick={() => navigate('/')}
            sx={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          >
            <DeepSafeLogo />
          </Box>

          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 0.5 }}>
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                label={link.label}
                path={link.path}
                isActive={
                  link.path === '/'
                    ? currentPath === '/' || currentPath === '/dashboard'
                    : currentPath.startsWith(link.path)
                }
                onClick={() => navigate(link.path === '/' ? '/dashboard' : link.path)}
              />
            ))}
          </Box>
        </Box>

        {/* Right side - Theme Toggle, Notifications, and Profile */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Theme Toggle Button */}
          <Tooltip title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}>
            <IconButton
              onClick={toggleTheme}
              sx={{
                color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                background: isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.04)',
                borderRadius: '10px',
                transition: 'all 0.2s ease',
                '&:hover': {
                  background: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)',
                  color: brandColors.primary.signalTeal,
                  transform: 'rotate(15deg)',
                },
              }}
            >
              {isDark ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>

          {/* Notifications */}
          <IconButton
            onClick={handleNotificationClick}
            sx={{
              color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
              '&:hover': {
                backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)',
              },
            }}
          >
            <Badge
              badgeContent={unreadCount}
              sx={{
                '& .MuiBadge-badge': {
                  backgroundColor: brandColors.primary.threatRed,
                  color: '#FFFFFF',
                },
              }}
            >
              <NotificationsIcon />
            </Badge>
          </IconButton>

          {/* Profile */}
          <Box
            onClick={handleProfileClick}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              cursor: 'pointer',
              p: 0.5,
              borderRadius: '12px',
              transition: 'all 0.2s ease',
              '&:hover': {
                backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)',
              },
            }}
          >
            <Avatar
              sx={{
                width: 36,
                height: 36,
                background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                fontWeight: 600,
                fontSize: '0.875rem',
              }}
            >
              MB
            </Avatar>
          </Box>
        </Box>

        {/* Notifications Popover */}
        <Popover
          open={Boolean(notificationAnchorEl)}
          anchorEl={notificationAnchorEl}
          onClose={handleNotificationClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          transformOrigin={{ vertical: 'top', horizontal: 'right' }}
          PaperProps={{
            sx: {
              width: 380,
              maxHeight: 480,
              mt: 1,
              background: isDark ? brandColors.dark.elevated : brandColors.light.surface,
              border: `1px solid ${theme.customColors.borderColor}`,
              borderRadius: 3,
            },
          }}
        >
          <Box sx={{ p: 2, borderBottom: `1px solid ${theme.customColors.borderColor}` }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Notifications
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: brandColors.primary.signalTeal,
                  cursor: 'pointer',
                  fontWeight: 500,
                  '&:hover': { textDecoration: 'underline' },
                }}
              >
                Mark all as read
              </Typography>
            </Box>
          </Box>
          <List sx={{ p: 0 }}>
            {alerts.map((alert) => (
              <ListItem key={alert.id} disablePadding>
                <ListItemButton
                  onClick={() => {
                    if (alert.actionUrl) navigate(alert.actionUrl);
                    handleNotificationClose();
                  }}
                  sx={{
                    py: 1.5,
                    px: 2,
                    backgroundColor: alert.isRead
                      ? 'transparent'
                      : isDark
                        ? 'rgba(31, 182, 166, 0.08)'
                        : 'rgba(31, 60, 136, 0.04)',
                    '&:hover': {
                      backgroundColor: isDark
                        ? 'rgba(255, 255, 255, 0.05)'
                        : 'rgba(0, 0, 0, 0.04)',
                    },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40 }}>
                    {getAlertIcon(alert.type, isDark)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" fontWeight={600}>
                          {alert.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(alert.timestamp).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        {alert.message}
                      </Typography>
                    }
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Popover>

        {/* Profile Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleProfileClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          transformOrigin={{ vertical: 'top', horizontal: 'right' }}
          PaperProps={{
            sx: {
              width: 240,
              mt: 1,
              borderRadius: 3,
            },
          }}
        >
          <Box sx={{ px: 2, py: 1.5 }}>
            <Typography variant="subtitle1" fontWeight={600}>
              Manan Bhargava
            </Typography>
            <Typography variant="caption" color="text.secondary">
              manan@company.com
            </Typography>
          </Box>
          <Divider />
          <MenuItem
            onClick={() => {
              navigate('/settings');
              handleProfileClose();
            }}
            sx={{ py: 1.5 }}
          >
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Settings</ListItemText>
          </MenuItem>
          <MenuItem
            onClick={() => {
              navigate('/profile');
              handleProfileClose();
            }}
            sx={{ py: 1.5 }}
          >
            <ListItemIcon>
              <PersonIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>My Profile</ListItemText>
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleProfileClose} sx={{ py: 1.5 }}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Sign Out</ListItemText>
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
