import React from 'react';
import { Box, Toolbar, useTheme } from '@mui/material';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { useThemeMode } from '../../context/ThemeContext';

export const MainLayout: React.FC = () => {
  const theme = useTheme();
  const { isDark } = useThemeMode();

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Header />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minHeight: '100vh',
          // Bold immersive gradient background
          background: isDark
            ? theme.gradients.midnightCore
            : theme.gradients.cloudSecure,
          // Smooth transition for theme changes
          transition: 'background 0.3s ease',
          position: 'relative',
          // Subtle pattern overlay for depth
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: isDark
              ? 'radial-gradient(ellipse at top right, rgba(31, 60, 136, 0.15) 0%, transparent 50%), radial-gradient(ellipse at bottom left, rgba(31, 182, 166, 0.08) 0%, transparent 50%)'
              : 'radial-gradient(ellipse at top right, rgba(31, 60, 136, 0.05) 0%, transparent 50%), radial-gradient(ellipse at bottom left, rgba(31, 182, 166, 0.03) 0%, transparent 50%)',
            pointerEvents: 'none',
          },
        }}
      >
        {/* Spacer for fixed AppBar */}
        <Toolbar />
        {/* Page content */}
        <Box
          sx={{
            p: { xs: 2, sm: 3 },
            position: 'relative',
            zIndex: 1,
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;
