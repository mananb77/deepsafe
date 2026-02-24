import React from 'react';
import { Navigate } from 'react-router-dom';
import { config } from '../../config/env';
import { useCurrentUser } from '../../hooks/useAuth';
import { Box, CircularProgress } from '@mui/material';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  // In mock mode, always allow access
  if (config.isMock) {
    return <>{children}</>;
  }

  const { data: user, isLoading } = useCurrentUser();

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!user?.isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
