import React from 'react';
import { Box } from '@mui/material';
import { Warning as MuiWarningIcon } from '@mui/icons-material';
import { colors } from '../../theme/colors';

interface WarningIconProps {
  size?: 'small' | 'medium' | 'large';
}

// Custom cyan warning icon matching the mockup design
export const WarningIcon: React.FC<WarningIconProps> = ({ size = 'medium' }) => {
  const sizeMap = {
    small: 18,
    medium: 24,
    large: 32,
  };

  return (
    <Box
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <MuiWarningIcon
        sx={{
          fontSize: sizeMap[size],
          color: colors.alert.info, // Cyan color from mockup
        }}
      />
    </Box>
  );
};

export default WarningIcon;
