import React from 'react';
import { Box, Container, Typography, IconButton, useTheme, Link } from '@mui/material';
import {
  Security as SecurityIcon,
  GitHub as GitHubIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { brandColors } from '../../../theme/colors';

export const Footer: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const isDark = theme.palette.mode === 'dark';

  const footerLinks = [
    { label: 'Interactive Demo', path: '/demo' },
    { label: 'Dashboard', path: '/app/welcome' },
    { label: 'GitHub', href: 'https://github.com', external: true },
  ];

  return (
    <Box
      component="footer"
      sx={{
        py: 6,
        background: isDark
          ? 'linear-gradient(180deg, #0B1220 0%, #05070C 100%)'
          : 'linear-gradient(180deg, #EEF2F7 0%, #F7F9FC 100%)',
        borderTop: `1px solid ${isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'}`,
      }}
    >
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            alignItems: { xs: 'center', md: 'flex-start' },
            justifyContent: 'space-between',
            gap: 4,
          }}
        >
          {/* Logo and tagline */}
          <Box sx={{ textAlign: { xs: 'center', md: 'left' } }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                mb: 2,
                justifyContent: { xs: 'center', md: 'flex-start' },
              }}
            >
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
                  fontSize: '1.125rem',
                  color: isDark ? '#E6ECF5' : '#0B1B3A',
                }}
              >
                DeepSafe
              </Typography>
            </Box>
            <Typography
              variant="body2"
              sx={{
                color: isDark ? '#7F8CA8' : '#7B8CA5',
                maxWidth: 280,
              }}
            >
              Built for security professionals. Protecting enterprises from AI-powered threats.
            </Typography>
          </Box>

          {/* Links */}
          <Box
            sx={{
              display: 'flex',
              gap: 4,
              flexWrap: 'wrap',
              justifyContent: 'center',
            }}
          >
            {footerLinks.map((link) =>
              link.external ? (
                <Link
                  key={link.label}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    color: isDark ? '#B8C3D9' : '#4A5D73',
                    textDecoration: 'none',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    '&:hover': {
                      color: brandColors.primary.signalTeal,
                    },
                    transition: 'color 0.2s ease',
                  }}
                >
                  {link.label}
                </Link>
              ) : (
                <Link
                  key={link.label}
                  component="button"
                  onClick={() => navigate(link.path!)}
                  sx={{
                    color: isDark ? '#B8C3D9' : '#4A5D73',
                    textDecoration: 'none',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    '&:hover': {
                      color: brandColors.primary.signalTeal,
                    },
                    transition: 'color 0.2s ease',
                  }}
                >
                  {link.label}
                </Link>
              )
            )}
          </Box>

          {/* Social */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton
              component="a"
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              sx={{
                color: isDark ? '#7F8CA8' : '#7B8CA5',
                '&:hover': {
                  color: brandColors.primary.signalTeal,
                  background: `${brandColors.primary.signalTeal}10`,
                },
              }}
            >
              <GitHubIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Copyright */}
        <Box
          sx={{
            mt: 4,
            pt: 4,
            borderTop: `1px solid ${isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'}`,
            textAlign: 'center',
          }}
        >
          <Typography
            variant="caption"
            sx={{
              color: isDark ? '#7F8CA8' : '#7B8CA5',
              fontSize: '0.75rem',
            }}
          >
            {new Date().getFullYear()} DeepSafe. A portfolio demonstration project.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
