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
  Drawer,
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
  Menu as MenuIcon,
  Close as CloseIcon,
  Dashboard as DashboardIcon,
  VideoCall as VideoCallIcon,
  People as PeopleIcon,
  Help as HelpIcon,
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
  dataWalkthrough?: string;
}

const NavLink: React.FC<NavLinkProps> = ({ label, isActive, onClick, dataWalkthrough }) => {
  const { isDark } = useThemeMode();

  return (
    <Box
      onClick={onClick}
      data-walkthrough={dataWalkthrough}
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
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  const currentPath = window.location.pathname;

  const navLinks = [
    { label: 'Summary', path: '/app/dashboard', dataWalkthrough: 'nav-dashboard', icon: <DashboardIcon /> },
    { label: 'Meeting History', path: '/app/meetings', dataWalkthrough: 'nav-meetings', icon: <VideoCallIcon /> },
    { label: 'Participant History', path: '/app/participants', dataWalkthrough: 'nav-participants', icon: <PeopleIcon /> },
    { label: 'Support', path: '/app/support', dataWalkthrough: 'nav-support', icon: <HelpIcon /> },
  ];

  const handleMobileDrawerToggle = () => {
    setMobileDrawerOpen(!mobileDrawerOpen);
  };

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
        <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, md: 4 } }}>
          {/* Mobile Menu Button */}
          <IconButton
            onClick={handleMobileDrawerToggle}
            sx={{
              display: { xs: 'flex', md: 'none' },
              color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
            }}
          >
            <MenuIcon />
          </IconButton>

          <Box
            onClick={() => navigate('/app/dashboard')}
            sx={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          >
            <DeepSafeLogo />
          </Box>

          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 0.5 }} data-walkthrough="header">
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                label={link.label}
                path={link.path}
                isActive={
                  link.path === '/app/dashboard'
                    ? currentPath === '/app' || currentPath === '/app/dashboard'
                    : currentPath.startsWith(link.path)
                }
                onClick={() => navigate(link.path)}
                dataWalkthrough={link.dataWalkthrough}
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
              data-walkthrough="theme-toggle"
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
              navigate('/app/settings');
              handleProfileClose();
            }}
            sx={{ py: 1.5 }}
            data-walkthrough="nav-settings"
          >
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Settings</ListItemText>
          </MenuItem>
          <MenuItem
            onClick={() => {
              navigate('/app/profile');
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

      {/* Mobile Navigation Drawer */}
      <Drawer
        anchor="left"
        open={mobileDrawerOpen}
        onClose={handleMobileDrawerToggle}
        PaperProps={{
          sx: {
            width: 280,
            background: isDark ? brandColors.dark.surface : brandColors.light.surface,
            borderRight: `1px solid ${theme.customColors.borderColor}`,
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          {/* Drawer Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <DeepSafeLogo />
            <IconButton
              onClick={handleMobileDrawerToggle}
              sx={{ color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary }}
            >
              <CloseIcon />
            </IconButton>
          </Box>

          <Divider sx={{ mb: 2 }} />

          {/* Navigation Links */}
          <List>
            {navLinks.map((link) => (
              <ListItem key={link.path} disablePadding>
                <ListItemButton
                  onClick={() => {
                    navigate(link.path);
                    handleMobileDrawerToggle();
                  }}
                  sx={{
                    borderRadius: 2,
                    mb: 0.5,
                    backgroundColor:
                      (link.path === '/app/dashboard'
                        ? currentPath === '/app' || currentPath === '/app/dashboard'
                        : currentPath.startsWith(link.path))
                        ? isDark
                          ? 'rgba(31, 182, 166, 0.15)'
                          : 'rgba(31, 60, 136, 0.1)'
                        : 'transparent',
                    '&:hover': {
                      backgroundColor: isDark
                        ? 'rgba(255, 255, 255, 0.08)'
                        : 'rgba(0, 0, 0, 0.04)',
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      color:
                        (link.path === '/app/dashboard'
                          ? currentPath === '/app' || currentPath === '/app/dashboard'
                          : currentPath.startsWith(link.path))
                          ? brandColors.primary.signalTeal
                          : isDark
                            ? brandColors.darkText.secondary
                            : brandColors.lightText.secondary,
                      minWidth: 40,
                    }}
                  >
                    {link.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={link.label}
                    primaryTypographyProps={{
                      fontWeight:
                        (link.path === '/app/dashboard'
                          ? currentPath === '/app' || currentPath === '/app/dashboard'
                          : currentPath.startsWith(link.path))
                          ? 600
                          : 500,
                      color:
                        (link.path === '/app/dashboard'
                          ? currentPath === '/app' || currentPath === '/app/dashboard'
                          : currentPath.startsWith(link.path))
                          ? isDark
                            ? brandColors.darkText.primary
                            : brandColors.lightText.primary
                          : isDark
                            ? brandColors.darkText.secondary
                            : brandColors.lightText.secondary,
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>

          <Divider sx={{ my: 2 }} />

          {/* Settings & Profile in Drawer */}
          <List>
            <ListItem disablePadding>
              <ListItemButton
                onClick={() => {
                  navigate('/app/settings');
                  handleMobileDrawerToggle();
                }}
                sx={{ borderRadius: 2, mb: 0.5 }}
              >
                <ListItemIcon sx={{ color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary, minWidth: 40 }}>
                  <SettingsIcon />
                </ListItemIcon>
                <ListItemText primary="Settings" />
              </ListItemButton>
            </ListItem>
            <ListItem disablePadding>
              <ListItemButton
                onClick={() => {
                  navigate('/app/profile');
                  handleMobileDrawerToggle();
                }}
                sx={{ borderRadius: 2 }}
              >
                <ListItemIcon sx={{ color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary, minWidth: 40 }}>
                  <PersonIcon />
                </ListItemIcon>
                <ListItemText primary="My Profile" />
              </ListItemButton>
            </ListItem>
          </List>
        </Box>
      </Drawer>
    </AppBar>
  );
};

export default Header;
