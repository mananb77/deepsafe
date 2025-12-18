import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { ThemeProvider } from './context/ThemeContext';
import { MainLayout } from './components/layout';
import { DashboardPage } from './pages/Dashboard';
import { MeetingsPage, MeetingDetailPage } from './pages/Meetings';
import { ParticipantsPage, ParticipantProfilePage } from './pages/Participants';
import { SettingsPage } from './pages/Settings';
import { ProfilePage } from './pages/Profile';
import { SupportPage, ArticlePage } from './pages/Support';
import { DemoPage, DemoProvider } from './pages/Demo';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <Routes>
            {/* Demo Route - Outside MainLayout for full-screen experience */}
            <Route
              path="demo"
              element={
                <DemoProvider>
                  <DemoPage />
                </DemoProvider>
              }
            />

            <Route path="/" element={<MainLayout />}>
              {/* Dashboard - Default route */}
              <Route index element={<Navigate to="/dashboard" replace />} />
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

              {/* Catch all - redirect to dashboard */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
