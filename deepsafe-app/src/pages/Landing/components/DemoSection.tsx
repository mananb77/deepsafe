import React from 'react';
import { Box, Typography, Button, useTheme, Grid, Paper } from '@mui/material';
import { motion } from 'framer-motion';
import {
  PlayArrow as PlayIcon,
  Dashboard as DashboardIcon,
  Security as SecurityIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { Section } from './Section';
import { useScrollAnimation } from '../hooks/useScrollAnimation';
import { brandColors } from '../../../theme/colors';

const MotionBox = motion.create(Box);

interface DemoCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  buttonText: string;
  buttonIcon: React.ReactNode;
  onClick: () => void;
  features: string[];
  delay?: number;
  accent?: boolean;
}

const DemoCard: React.FC<DemoCardProps> = ({
  title,
  description,
  icon,
  buttonText,
  buttonIcon,
  onClick,
  features,
  delay = 0,
  accent = false,
}) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const { ref, isVisible } = useScrollAnimation({ threshold: 0.2 });

  return (
    <MotionBox
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{ duration: 0.6, delay, ease: [0.4, 0, 0.2, 1] }}
      sx={{ height: '100%' }}
    >
      <Paper
        elevation={0}
        sx={{
          p: 4,
          borderRadius: 3,
          background: accent
            ? `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}15 0%, ${brandColors.primary.signalTeal}10 100%)`
            : isDark
            ? 'linear-gradient(135deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.8) 100%)'
            : 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.9) 100%)',
          border: accent
            ? `1px solid ${brandColors.primary.signalTeal}40`
            : `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: isDark
              ? `0 12px 40px rgba(0, 0, 0, 0.4)`
              : `0 12px 40px rgba(0, 0, 0, 0.1)`,
          },
        }}
      >
        {/* Icon */}
        <Box
          sx={{
            width: 64,
            height: 64,
            borderRadius: 3,
            background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}20 0%, ${brandColors.primary.signalTeal}20 100%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mb: 3,
          }}
        >
          {icon}
        </Box>

        {/* Title */}
        <Typography
          variant="h5"
          sx={{
            fontFamily: '"Space Grotesk", sans-serif',
            fontWeight: 600,
            fontSize: '1.25rem',
            color: isDark ? '#E6ECF5' : '#0B1B3A',
            mb: 1.5,
          }}
        >
          {title}
        </Typography>

        {/* Description */}
        <Typography
          variant="body1"
          sx={{
            color: isDark ? '#B8C3D9' : '#4A5D73',
            mb: 3,
            lineHeight: 1.6,
          }}
        >
          {description}
        </Typography>

        {/* Features */}
        <Box sx={{ mb: 3 }}>
          {features.map((feature, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                py: 0.75,
              }}
            >
              <Box
                sx={{
                  width: 18,
                  height: 18,
                  borderRadius: '50%',
                  background: `${brandColors.primary.signalTeal}20`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Box
                  sx={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    background: brandColors.primary.signalTeal,
                  }}
                />
              </Box>
              <Typography
                variant="body2"
                sx={{
                  color: isDark ? '#B8C3D9' : '#4A5D73',
                  fontSize: '0.875rem',
                }}
              >
                {feature}
              </Typography>
            </Box>
          ))}
        </Box>

        {/* CTA Button */}
        <Button
          variant={accent ? 'contained' : 'outlined'}
          size="large"
          startIcon={buttonIcon}
          onClick={onClick}
          sx={{
            mt: 'auto',
            ...(accent
              ? {
                  background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                  color: '#fff',
                  '&:hover': {
                    background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
                  },
                }
              : {
                  borderColor: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
                  color: isDark ? '#E6ECF5' : '#0B1B3A',
                  '&:hover': {
                    borderColor: brandColors.primary.signalTeal,
                    background: `${brandColors.primary.signalTeal}10`,
                  },
                }),
            fontWeight: 600,
            textTransform: 'none',
            borderRadius: 2,
            py: 1.5,
          }}
        >
          {buttonText}
        </Button>
      </Paper>
    </MotionBox>
  );
};

export const DemoSection: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Section
      id="demo"
      title="See It In Action"
      subtitle="Experience DeepSafe through interactive demonstrations"
      background="alternate"
    >
      <Grid container spacing={4}>
        <Grid size={{ xs: 12, md: 6 }}>
          <DemoCard
            title="Interactive Demo"
            description="Experience a simulated deepfake attack being detected in real-time. Walk through the complete detection and response workflow."
            icon={<SecurityIcon sx={{ fontSize: 32, color: brandColors.primary.signalTeal }} />}
            buttonText="Launch Interactive Demo"
            buttonIcon={<PlayIcon />}
            onClick={() => navigate('/demo')}
            features={[
              'Simulated deepfake video call',
              'Real-time risk scoring',
              'Step-by-step detection walkthrough',
              'Forensic analysis preview',
            ]}
            delay={0}
            accent
          />
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <DemoCard
            title="Security Dashboard"
            description="Explore the full security monitoring interface. View meeting history, participant profiles, and incident reports."
            icon={<DashboardIcon sx={{ fontSize: 32, color: brandColors.primary.deepSafeBlue }} />}
            buttonText="View Dashboard"
            buttonIcon={<TimelineIcon />}
            onClick={() => navigate('/app/welcome')}
            features={[
              'Meeting monitoring dashboard',
              'Risk trend analytics',
              'Participant trust profiles',
              'Incident management',
            ]}
            delay={0.1}
          />
        </Grid>
      </Grid>
    </Section>
  );
};

export default DemoSection;
