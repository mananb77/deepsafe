import React from 'react';
import { Chip, Stack } from '@mui/material';
import { motion } from 'framer-motion';
import { brandColors } from '../../../../theme/colors';
import { riskChipVariants } from '../../constants/animations';

const MotionChip = motion(Chip);

interface RiskChipsProps {
  indicators: string[];
}

// Map risk indicator text to colors
const getIndicatorColor = (indicator: string): string => {
  const lowerIndicator = indicator.toLowerCase();

  if (
    lowerIndicator.includes('urgent') ||
    lowerIndicator.includes('secrecy') ||
    lowerIndicator.includes('threat')
  ) {
    return brandColors.statusDark.error;
  }

  if (
    lowerIndicator.includes('authority') ||
    lowerIndicator.includes('pressure') ||
    lowerIndicator.includes('bypass')
  ) {
    return '#FF6B6B';
  }

  if (
    lowerIndicator.includes('process') ||
    lowerIndicator.includes('irregular') ||
    lowerIndicator.includes('financial')
  ) {
    return brandColors.statusDark.warning;
  }

  return brandColors.primary.signalTeal;
};

export const RiskChips: React.FC<RiskChipsProps> = ({ indicators }) => {
  if (!indicators || indicators.length === 0) return null;

  return (
    <Stack
      id="risk-indicators"
      direction="row"
      spacing={0.75}
      flexWrap="wrap"
      useFlexGap
      sx={{ mt: 1 }}
    >
      {indicators.map((indicator, index) => (
        <MotionChip
          key={indicator}
          variants={riskChipVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          custom={index}
          label={indicator}
          size="small"
          sx={{
            height: 20,
            fontSize: '0.65rem',
            fontWeight: 600,
            backgroundColor: `${getIndicatorColor(indicator)}15`,
            color: getIndicatorColor(indicator),
            border: `1px solid ${getIndicatorColor(indicator)}40`,
            '& .MuiChip-label': {
              px: 1,
            },
          }}
        />
      ))}
    </Stack>
  );
};

export default RiskChips;
