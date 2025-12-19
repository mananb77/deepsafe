import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Box,
  Typography,
  Button,
  IconButton,
  useTheme,
  useScrollTrigger,
  Container,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Security as SecurityIcon,
  GitHub as GitHubIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
  Menu as MenuIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useThemeMode } from '../../../context/ThemeContext';
import { brandColors } from '../../../theme/colors';

interface NavItem {
  label: string;
  href: string;
}

const navItems: NavItem[] = [
  { label: 'Problem', href: '#problem' },
  { label: 'Solution', href: '#solution' },
  { label: 'Architecture', href: '#architecture' },
  { label: 'Tech Stack', href: '#tech-stack' },
  { label: 'Demo', href: '#demo' },
];

export const LandingHeader: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { mode, toggleTheme } = useThemeMode();
  const isDark = theme.palette.mode === 'dark';
  const [activeSection, setActiveSection] = useState('');
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  const handleMobileDrawerToggle = () => {
    setMobileDrawerOpen(!mobileDrawerOpen);
  };

  const trigger = useScrollTrigger({
    disableHysteresis: true,
    threshold: 50,
  });

  // Track active section on scroll
  useEffect(() => {
    const handleScroll = () => {
      const sections = navItems.map((item) => item.href.slice(1));
      const scrollPosition = window.scrollY + 100;

      for (const section of sections.reverse()) {
        const element = document.getElementById(section);
        if (element && element.offsetTop <= scrollPosition) {
          setActiveSection(section);
          break;
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleNavClick = (href: string) => {
    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setMobileDrawerOpen(false);
  };

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        background: trigger
          ? isDark
            ? 'rgba(11, 18, 32, 0.95)'
            : 'rgba(255, 255, 255, 0.95)'
          : 'transparent',
        backdropFilter: trigger ? 'blur(10px)' : 'none',
        borderBottom: trigger
          ? `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`
          : 'none',
        transition: 'all 0.3s ease',
      }}
    >
      <Container maxWidth="lg">
        <Toolbar sx={{ px: { xs: 0 }, py: 1 }}>
          {/* Mobile Menu Button */}
          <IconButton
            onClick={handleMobileDrawerToggle}
            sx={{
              display: { xs: 'flex', md: 'none' },
              mr: 1,
              color: isDark ? '#B8C3D9' : '#4A5D73',
            }}
          >
            <MenuIcon />
          </IconButton>

          {/* Logo */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              cursor: 'pointer',
            }}
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <SecurityIcon sx={{ color: '#fff', fontSize: 24 }} />
            </Box>
            <Typography
              variant="h6"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 700,
                fontSize: '1.25rem',
                color: isDark ? '#E6ECF5' : '#0B1B3A',
                display: { xs: 'none', sm: 'block' },
              }}
            >
              DeepSafe
            </Typography>
          </Box>

          {/* Navigation */}
          <Box
            sx={{
              display: { xs: 'none', md: 'flex' },
              gap: 1,
              ml: 'auto',
              mr: 2,
            }}
          >
            {navItems.map((item) => (
              <Button
                key={item.href}
                onClick={() => handleNavClick(item.href)}
                sx={{
                  color: activeSection === item.href.slice(1)
                    ? brandColors.primary.signalTeal
                    : isDark
                    ? 'rgba(184, 195, 217, 0.9)'
                    : 'rgba(74, 93, 115, 0.9)',
                  fontWeight: 500,
                  fontSize: '0.875rem',
                  textTransform: 'none',
                  position: 'relative',
                  '&:hover': {
                    color: brandColors.primary.signalTeal,
                    background: 'transparent',
                  },
                  '&::after': activeSection === item.href.slice(1) ? {
                    content: '""',
                    position: 'absolute',
                    bottom: 6,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: 20,
                    height: 2,
                    borderRadius: 1,
                    background: `linear-gradient(90deg, ${brandColors.primary.deepSafeBlue}, ${brandColors.primary.signalTeal})`,
                  } : {},
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>

          {/* Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: { xs: 'auto', md: 0 } }}>
            <IconButton
              onClick={toggleTheme}
              sx={{
                color: isDark ? '#B8C3D9' : '#4A5D73',
                '&:hover': {
                  background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
                },
              }}
            >
              {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
            <IconButton
              component="a"
              href="https://github.com/mananb77/deepsafe"
              target="_blank"
              rel="noopener noreferrer"
              sx={{
                color: isDark ? '#B8C3D9' : '#4A5D73',
                '&:hover': {
                  background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
                },
              }}
            >
              <GitHubIcon />
            </IconButton>
            <Button
              variant="contained"
              onClick={() => navigate('/demo')}
              sx={{
                ml: 1,
                background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                color: '#fff',
                fontWeight: 600,
                textTransform: 'none',
                borderRadius: 2,
                px: 2.5,
                '&:hover': {
                  background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
                },
              }}
            >
              Try Demo
            </Button>
          </Box>
        </Toolbar>
      </Container>

      {/* Mobile Navigation Drawer */}
      <Drawer
        anchor="left"
        open={mobileDrawerOpen}
        onClose={handleMobileDrawerToggle}
        PaperProps={{
          sx: {
            width: 280,
            background: isDark ? brandColors.dark.surface : brandColors.light.surface,
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          {/* Drawer Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Box
                sx={{
                  width: 36,
                  height: 36,
                  borderRadius: 2,
                  background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <SecurityIcon sx={{ color: '#fff', fontSize: 20 }} />
              </Box>
              <Typography
                sx={{
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 700,
                  fontSize: '1.1rem',
                  color: isDark ? '#E6ECF5' : '#0B1B3A',
                }}
              >
                DeepSafe
              </Typography>
            </Box>
            <IconButton
              onClick={handleMobileDrawerToggle}
              sx={{ color: isDark ? '#B8C3D9' : '#4A5D73' }}
            >
              <CloseIcon />
            </IconButton>
          </Box>

          <Divider sx={{ mb: 2 }} />

          {/* Navigation Links */}
          <List>
            {navItems.map((item) => (
              <ListItem key={item.href} disablePadding>
                <ListItemButton
                  onClick={() => handleNavClick(item.href)}
                  sx={{
                    borderRadius: 2,
                    mb: 0.5,
                    backgroundColor:
                      activeSection === item.href.slice(1)
                        ? isDark
                          ? 'rgba(31, 182, 166, 0.15)'
                          : 'rgba(31, 60, 136, 0.1)'
                        : 'transparent',
                  }}
                >
                  <ListItemText
                    primary={item.label}
                    primaryTypographyProps={{
                      fontWeight: activeSection === item.href.slice(1) ? 600 : 500,
                      color: activeSection === item.href.slice(1)
                        ? brandColors.primary.signalTeal
                        : isDark
                          ? '#B8C3D9'
                          : '#4A5D73',
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>

          <Divider sx={{ my: 2 }} />

          {/* Demo Button */}
          <Button
            fullWidth
            variant="contained"
            onClick={() => {
              navigate('/demo');
              handleMobileDrawerToggle();
            }}
            sx={{
              background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
              color: '#fff',
              fontWeight: 600,
              textTransform: 'none',
              borderRadius: 2,
              py: 1.5,
            }}
          >
            Try Interactive Demo
          </Button>
        </Box>
      </Drawer>
    </AppBar>
  );
};

export default LandingHeader;
