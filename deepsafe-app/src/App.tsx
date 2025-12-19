import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { ThemeProvider } from './context/ThemeContext';
import { MainLayout } from './components/layout';
import { LandingPage } from './pages/Landing';
import { DashboardPage } from './pages/Dashboard';
import { MeetingsPage, MeetingDetailPage } from './pages/Meetings';
import { ParticipantsPage, ParticipantProfilePage } from './pages/Participants';
import { SettingsPage } from './pages/Settings';
import { ProfilePage } from './pages/Profile';
import { SupportPage, ArticlePage } from './pages/Support';
import { DemoPage, DemoProvider } from './pages/Demo';
import { WelcomeSplashPage } from './pages/Welcome';
import { WalkthroughProvider } from './features/Walkthrough';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

// Get base URL from Vite config (handles GitHub Pages deployment)
const basename = import.meta.env.BASE_URL;

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter basename={basename}>
          <Routes>
            {/* Landing Page - Portfolio showcase */}
            <Route path="/" element={<LandingPage />} />

            {/* Demo Route - Outside MainLayout for full-screen experience */}
            <Route
              path="demo"
              element={
                <DemoProvider>
                  <DemoPage />
                </DemoProvider>
              }
            />

            {/* Welcome Splash Page - Entry point to dashboard */}
            <Route
              path="/app/welcome"
              element={
                <WalkthroughProvider>
                  <WelcomeSplashPage />
                </WalkthroughProvider>
              }
            />

            {/* App Routes - Dashboard and related pages */}
            <Route
              path="/app"
              element={
                <WalkthroughProvider>
                  <MainLayout />
                </WalkthroughProvider>
              }
            >
              {/* Dashboard - Default app route */}
              <Route index element={<Navigate to="/app/welcome" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />

              {/* Meetings */}
              <Route path="meetings" element={<MeetingsPage />} />
              <Route path="meetings/:meetingId" element={<MeetingDetailPage />} />

              {/* Participants */}
              <Route path="participants" element={<ParticipantsPage />} />
              <Route path="participants/:participantId" element={<ParticipantProfilePage />} />

              {/* Settings, Profile, Support */}
              <Route path="settings" element={<SettingsPage />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route path="support" element={<SupportPage />} />
              <Route path="support/articles/:articleId" element={<ArticlePage />} />

              {/* Catch all within app - redirect to dashboard */}
              <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
            </Route>

            {/* Legacy route redirects for backwards compatibility */}
            <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
            <Route path="/meetings/*" element={<Navigate to="/app/meetings" replace />} />
            <Route path="/participants/*" element={<Navigate to="/app/participants" replace />} />
            <Route path="/settings" element={<Navigate to="/app/settings" replace />} />
            <Route path="/profile" element={<Navigate to="/app/profile" replace />} />
            <Route path="/support/*" element={<Navigate to="/app/support" replace />} />

            {/* Catch all - redirect to landing page */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
