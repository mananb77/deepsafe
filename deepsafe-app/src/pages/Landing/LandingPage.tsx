import React from 'react';
import { Box, CssBaseline } from '@mui/material';
import { LandingHeader } from './components/LandingHeader';
import { HeroSection } from './components/HeroSection';
import { ProblemSection } from './components/ProblemSection';
import { SolutionSection } from './components/SolutionSection';
import { ArchitectureSection } from './components/ArchitectureSection';
import { TechStackSection } from './components/TechStackSection';
import { DemoSection } from './components/DemoSection';
import { SetupSection } from './components/SetupSection';
import { CTASection } from './components/CTASection';
import { Footer } from './components/Footer';

export const LandingPage: React.FC = () => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <CssBaseline />
      <LandingHeader />
      <Box component="main" sx={{ flex: 1 }}>
        <HeroSection />
        <ProblemSection />
        <SolutionSection />
        <ArchitectureSection />
        <TechStackSection />
        <DemoSection />
        <SetupSection />
        <CTASection />
      </Box>
      <Footer />
    </Box>
  );
};

export default LandingPage;
