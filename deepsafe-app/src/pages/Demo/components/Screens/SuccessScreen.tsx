import React from 'react';
import { Box, Typography, Button, Grid, Card, CardContent } from '@mui/material';
import { motion } from 'framer-motion';
import {
  Shield as ShieldIcon,
  Replay as ReplayIcon,
  MenuBook as LearnIcon,
  CalendarMonth as CalendarIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  AttachMoney as MoneyIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { darkGradients, lightGradients, glassMorphism, functionalGradients } from '../../../../theme/gradients';
import { useDemoContext } from '../../context/DemoContext';
import {
  screenVariants,
  staggerContainerVariants,
  staggerItemVariants,
  successIconVariants,
} from '../../constants/animations';
import { useCountUp } from '../../hooks';
import { demoIncident } from '../../data/demoScenario';

const MotionBox = motion.create(Box);

interface MetricCardProps {
  icon: React.ReactNode;
  value: string;
  label: string;
  delay?: number;
  isDark: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, value, label, isDark }) => {
  const glass = glassMorphism(isDark ? 'dark' : 'light');

  return (
    <Card
      sx={{
        ...glass,
        border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'}`,
        borderRadius: 3,
        textAlign: 'center',
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box
          sx={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 48,
            height: 48,
            borderRadius: 2,
            backgroundColor: isDark
              ? 'rgba(31, 182, 166, 0.1)'
              : 'rgba(31, 60, 136, 0.08)',
            mb: 2,
          }}
        >
          {icon}
        </Box>
        <Typography
          variant="h4"
          sx={{
            fontFamily: '"Space Grotesk", sans-serif',
            fontWeight: 700,
            color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
            mb: 0.5,
          }}
        >
          {value}
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
          }}
        >
          {label}
        </Typography>
      </CardContent>
    </Card>
  );
};

export const SuccessScreen: React.FC = () => {
  const { isDark } = useThemeMode();
  const { dispatch } = useDemoContext();
  const gradients = isDark ? darkGradients : lightGradients;

  // Animated metrics
  const amountProtected = useCountUp(demoIncident.amountProtected, {
    duration: 2000,
    prefix: '$',
    formatter: (n) => n.toLocaleString(),
  });
  const detectionConfidence = useCountUp(92, {
    duration: 1500,
    delay: 200,
    suffix: '%',
  });
  const responseTime = useCountUp(98, {
    duration: 1500,
    delay: 400,
    suffix: ' sec',
  });

  const handleReplay = () => {
    dispatch({ type: 'RESET_DEMO' });
  };

  const handleLearnMore = () => {
    window.open('https://deepsafe.ai/how-it-works', '_blank');
  };

  const handleRequestDemo = () => {
    window.open('https://deepsafe.ai/contact', '_blank');
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
      {/* Background celebration effect */}
      <Box
        sx={{
          position: 'absolute',
          width: '800px',
          height: '800px',
          borderRadius: '50%',
          background: `radial-gradient(circle, ${brandColors.statusDark.success}15 0%, transparent 60%)`,
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          filter: 'blur(100px)',
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
          maxWidth: 800,
          textAlign: 'center',
          position: 'relative',
          zIndex: 1,
        }}
      >
        {/* Success Icon with Animation */}
        <MotionBox
          variants={successIconVariants}
          sx={{ mb: 3 }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 100,
              height: 100,
              borderRadius: '50%',
              background: functionalGradients.success,
              boxShadow: `0 0 40px ${brandColors.statusDark.success}60`,
            }}
          >
            <ShieldIcon sx={{ fontSize: 48, color: '#FFFFFF' }} />
          </Box>
        </MotionBox>

        {/* Headline */}
        <MotionBox variants={staggerItemVariants}>
          <Typography
            variant="h2"
            sx={{
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 700,
              fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' },
              color: brandColors.statusDark.success,
              mb: 1,
            }}
          >
            Attack Prevented
          </Typography>
        </MotionBox>

        <MotionBox variants={staggerItemVariants}>
          <Typography
            variant="h5"
            sx={{
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 500,
              color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
              mb: 2,
            }}
          >
            Your organization is protected
          </Typography>
        </MotionBox>

        <MotionBox variants={staggerItemVariants}>
          <Typography
            variant="body1"
            sx={{
              color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
              maxWidth: 500,
              mb: 5,
            }}
          >
            DeepSafe successfully identified and neutralized a sophisticated deepfake
            impersonation attack before any damage could occur.
          </Typography>
        </MotionBox>

        {/* Metrics Grid */}
        <MotionBox variants={staggerItemVariants} sx={{ width: '100%', mb: 5 }}>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, sm: 4 }}>
              <MetricCard
                icon={<MoneyIcon sx={{ fontSize: 24, color: brandColors.statusDark.success }} />}
                value={amountProtected.formattedValue}
                label="Amount Protected"
                isDark={isDark}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <MetricCard
                icon={<SecurityIcon sx={{ fontSize: 24, color: brandColors.primary.signalTeal }} />}
                value={detectionConfidence.formattedValue}
                label="Detection Confidence"
                isDark={isDark}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <MetricCard
                icon={<SpeedIcon sx={{ fontSize: 24, color: brandColors.primary.alertAmber }} />}
                value={responseTime.formattedValue}
                label="Response Time"
                delay={400}
                isDark={isDark}
              />
            </Grid>
          </Grid>
        </MotionBox>

        {/* Action Buttons */}
        <MotionBox
          variants={staggerItemVariants}
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: 2,
          }}
        >
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button
              variant="outlined"
              size="large"
              startIcon={<ReplayIcon />}
              onClick={handleReplay}
              sx={{
                px: 3,
                py: 1.5,
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 600,
                borderColor: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                '&:hover': {
                  borderColor: brandColors.primary.signalTeal,
                  backgroundColor: 'transparent',
                },
              }}
            >
              Replay Demo
            </Button>
          </motion.div>

          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button
              variant="outlined"
              size="large"
              startIcon={<LearnIcon />}
              onClick={handleLearnMore}
              sx={{
                px: 3,
                py: 1.5,
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 600,
                borderColor: brandColors.primary.signalTeal,
                color: brandColors.primary.signalTeal,
                '&:hover': {
                  backgroundColor: 'rgba(31, 182, 166, 0.08)',
                  borderColor: brandColors.primary.signalTeal,
                },
              }}
            >
              Learn More
            </Button>
          </motion.div>

          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<CalendarIcon />}
              onClick={handleRequestDemo}
              sx={{
                px: 3,
                py: 1.5,
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 600,
                background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
                boxShadow: `0 4px 16px ${brandColors.primary.signalTeal}40`,
                '&:hover': {
                  background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 20%, ${brandColors.primary.deepSafeBlue} 100%)`,
                },
              }}
            >
              Request Live Demo
            </Button>
          </motion.div>
        </MotionBox>

        {/* Final note */}
        <MotionBox variants={staggerItemVariants} sx={{ mt: 5 }}>
          <Typography
            variant="caption"
            sx={{
              color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
              maxWidth: 400,
              display: 'block',
            }}
          >
            This demo showcases a real-world attack scenario. DeepSafe&apos;s AI protection
            works 24/7 to keep your organization secure.
          </Typography>
        </MotionBox>
      </MotionBox>
    </MotionBox>
  );
};

export default SuccessScreen;
