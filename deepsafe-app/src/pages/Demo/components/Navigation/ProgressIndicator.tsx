import React from 'react';
import { Box, Tooltip } from '@mui/material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { demoScenario } from '../../data/demoScenario';

interface ProgressIndicatorProps {
  currentStep: number;
  totalSteps: number;
  onStepClick: (step: number) => void;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  currentStep,
  totalSteps,
  onStepClick,
}) => {
  const { isDark } = useThemeMode();

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
      }}
      role="navigation"
      aria-label="Demo progress"
    >
      {Array.from({ length: totalSteps }, (_, index) => {
        const stepNumber = index + 1;
        const isActive = stepNumber === currentStep;
        const isVisited = stepNumber <= currentStep;
        const stepConfig = demoScenario[index];

        return (
          <Tooltip
            key={stepNumber}
            title={`${stepNumber}. ${stepConfig?.name || `Step ${stepNumber}`}`}
            arrow
          >
            <Box
              component="button"
              onClick={() => onStepClick(stepNumber)}
              aria-label={`Go to step ${stepNumber}: ${stepConfig?.name || ''}`}
              aria-current={isActive ? 'step' : undefined}
              sx={{
                width: isActive ? 24 : 10,
                height: 10,
                borderRadius: 5,
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                backgroundColor: isActive
                  ? brandColors.primary.signalTeal
                  : isVisited
                    ? isDark
                      ? brandColors.darkText.secondary
                      : brandColors.lightText.secondary
                    : isDark
                      ? 'rgba(255, 255, 255, 0.2)'
                      : 'rgba(0, 0, 0, 0.15)',
                '&:hover': {
                  backgroundColor: isActive
                    ? brandColors.primary.signalTeal
                    : brandColors.primary.signalTeal + '80',
                  transform: 'scale(1.2)',
                },
                '&:focus': {
                  outline: `2px solid ${brandColors.primary.signalTeal}`,
                  outlineOffset: 2,
                },
              }}
            />
          </Tooltip>
        );
      })}
    </Box>
  );
};

export default ProgressIndicator;
