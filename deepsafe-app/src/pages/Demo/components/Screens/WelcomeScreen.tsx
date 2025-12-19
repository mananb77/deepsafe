import React from 'react';
import { Box, Typography, Button, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import { PlayArrow as PlayIcon, Security as SecurityIcon } from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { darkGradients, lightGradients, functionalGradients } from '../../../../theme/gradients';
import { useDemoContext } from '../../context/DemoContext';
import { screenVariants, staggerContainerVariants, staggerItemVariants } from '../../constants/animations';

const MotionBox = motion.create(Box);

export const WelcomeScreen: React.FC = () => {
  const { isDark } = useThemeMode();
  const { dispatch } = useDemoContext();
  const gradients = isDark ? darkGradients : lightGradients;

  const handleStart = () => {
    dispatch({ type: 'NEXT_STEP' });
  };

  return (
    <MotionBox
      variants={screenVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: gradients.signature,
        px: 3,
        py: 6,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background glow effect */}
      <Box
        sx={{
          position: 'absolute',
          width: '600px',
          height: '600px',
          borderRadius: '50%',
          background: `radial-gradient(circle, ${brandColors.primary.signalTeal}20 0%, transparent 70%)`,
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          filter: 'blur(80px)',
          pointerEvents: 'none',
        }}
      />

      <MotionBox
        variants={staggerContainerVariants}
        initial="initial"
        animate="animate"
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          maxWidth: 600,
          textAlign: 'center',
          position: 'relative',
          zIndex: 1,
        }}
      >
        {/* Logo with animated glow */}
        <MotionBox
          variants={staggerItemVariants}
          sx={{
            mb: 4,
            position: 'relative',
          }}
        >
          <motion.div
            animate={{
              boxShadow: [
                `0 0 20px ${brandColors.primary.signalTeal}40`,
                `0 0 40px ${brandColors.primary.signalTeal}60`,
                `0 0 20px ${brandColors.primary.signalTeal}40`,
              ],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 120,
              height: 120,
              borderRadius: '24px',
              background: isDark
                ? `linear-gradient(135deg, ${brandColors.dark.surface} 0%, ${brandColors.dark.deepest} 100%)`
                : `linear-gradient(135deg, #FFFFFF 0%, #F7F9FC 100%)`,
              border: `2px solid ${brandColors.primary.signalTeal}`,
            }}
          >
            <SecurityIcon
              sx={{
                fontSize: 64,
                color: brandColors.primary.signalTeal,
              }}
            />
          </motion.div>
        </MotionBox>

        {/* Badge */}
        <MotionBox variants={staggerItemVariants}>
          <Chip
            label="Interactive Demo"
            size="small"
            sx={{
              mb: 3,
              background: functionalGradients.info,
              color: '#FFFFFF',
              fontWeight: 600,
              fontSize: '0.75rem',
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              px: 1,
            }}
          />
        </MotionBox>

        {/* Headline */}
        <MotionBox variants={staggerItemVariants}>
          <Typography
            variant="h2"
            sx={{
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 700,
              fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' },
              lineHeight: 1.2,
              mb: 2,
              background: isDark
                ? `linear-gradient(90deg, ${brandColors.darkText.primary} 0%, ${brandColors.primary.signalTeal} 100%)`
                : `linear-gradient(90deg, ${brandColors.lightText.primary} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            Experience DeepSafe
            <br />
            in Action
          </Typography>
        </MotionBox>

        {/* Subheadline */}
        <MotionBox variants={staggerItemVariants}>
          <Typography
            variant="body1"
            sx={{
              color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
              fontSize: { xs: '1rem', sm: '1.125rem' },
              lineHeight: 1.7,
              mb: 4,
              maxWidth: 500,
            }}
          >
            Watch how DeepSafe detects and stops a sophisticated deepfake attack
            targeting a CFO for a $250,000 wire transfer — in real-time.
          </Typography>
        </MotionBox>

        {/* Demo info */}
        <MotionBox
          variants={staggerItemVariants}
          sx={{
            display: 'flex',
            gap: 3,
            mb: 5,
            flexWrap: 'wrap',
            justifyContent: 'center',
          }}
        >
          {[
            { label: '9 Steps', icon: '📍' },
            { label: '~4 Minutes', icon: '⏱️' },
            { label: 'Interactive', icon: '🖱️' },
          ].map((item) => (
            <Box
              key={item.label}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                px: 2,
                py: 1,
                borderRadius: 2,
                backgroundColor: isDark
                  ? 'rgba(255, 255, 255, 0.05)'
                  : 'rgba(0, 0, 0, 0.03)',
                border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
              }}
            >
              <span style={{ fontSize: '1rem' }}>{item.icon}</span>
              <Typography
                variant="body2"
                sx={{
                  color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                  fontWeight: 500,
                }}
              >
                {item.label}
              </Typography>
            </Box>
          ))}
        </MotionBox>

        {/* CTA Button */}
        <MotionBox
          variants={staggerItemVariants}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Button
            variant="contained"
            size="large"
            onClick={handleStart}
            startIcon={<PlayIcon />}
            sx={{
              px: 5,
              py: 1.75,
              borderRadius: 3,
              fontSize: '1.125rem',
              fontWeight: 600,
              textTransform: 'none',
              background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
              boxShadow: `0 8px 24px ${brandColors.primary.signalTeal}40`,
              '&:hover': {
                background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 20%, ${brandColors.primary.deepSafeBlue} 100%)`,
                boxShadow: `0 12px 32px ${brandColors.primary.signalTeal}50`,
              },
            }}
          >
            Start Demo
          </Button>
        </MotionBox>

        {/* Keyboard hint */}
        <MotionBox
          variants={staggerItemVariants}
          sx={{ mt: 4 }}
        >
          <Typography
            variant="caption"
            sx={{
              color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            Press
            <Box
              component="kbd"
              sx={{
                px: 1,
                py: 0.25,
                borderRadius: 1,
                backgroundColor: isDark
                  ? 'rgba(255, 255, 255, 0.08)'
                  : 'rgba(0, 0, 0, 0.06)',
                border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.1)'}`,
                fontFamily: 'monospace',
                fontSize: '0.75rem',
              }}
            >
              Space
            </Box>
            or
            <Box
              component="kbd"
              sx={{
                px: 1,
                py: 0.25,
                borderRadius: 1,
                backgroundColor: isDark
                  ? 'rgba(255, 255, 255, 0.08)'
                  : 'rgba(0, 0, 0, 0.06)',
                border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.1)'}`,
                fontFamily: 'monospace',
                fontSize: '0.75rem',
              }}
            >
              →
            </Box>
            to navigate
          </Typography>
        </MotionBox>
      </MotionBox>
    </MotionBox>
  );
};

export default WelcomeScreen;
