/**
 * Standalone Demo Entry Point
 *
 * This file is used when building the demo as a standalone deployable.
 * It includes only the minimal dependencies needed for the demo to run.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { ThemeProvider } from './context/ThemeContext';
import { DemoProvider } from './pages/Demo/context/DemoContext';
import { DemoPage } from './pages/Demo/DemoPage';

// Standalone flag - enables special behaviors for standalone deployment
const STANDALONE = true;

const StandaloneDemo: React.FC = () => {
  return (
    <ThemeProvider>
      <DemoProvider>
        <DemoPage standalone={STANDALONE} />
      </DemoProvider>
    </ThemeProvider>
  );
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <StandaloneDemo />
  </React.StrictMode>
);
