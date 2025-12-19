import React from 'react';
import { Box, Typography, Button, Container, useTheme } from '@mui/material';
import { motion } from 'framer-motion';
import { PlayArrow as PlayIcon, GitHub as GitHubIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useScrollAnimation } from '../hooks/useScrollAnimation';
import { brandColors } from '../../../theme/colors';

const MotionBox = motion.create(Box);

export const CTASection: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const isDark = theme.palette.mode === 'dark';
  const { ref, isVisible } = useScrollAnimation({ threshold: 0.3 });

  return (
    <Box
      component="section"
      ref={ref}
      sx={{
        py: { xs: 10, md: 14 },
        position: 'relative',
        overflow: 'hidden',
        background: isDark
          ? `linear-gradient(180deg, #0B1220 0%, ${brandColors.primary.deepSafeBlue}30 50%, #0B1220 100%)`
          : `linear-gradient(180deg, #F7F9FC 0%, ${brandColors.primary.deepSafeBlue}15 50%, #F7F9FC 100%)`,
      }}
    >
      {/* Background glow */}
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '80%',
          height: '100%',
          background: `radial-gradient(ellipse at center, ${brandColors.primary.signalTeal}15 0%, transparent 70%)`,
          pointerEvents: 'none',
        }}
      />

      <Container maxWidth="md" sx={{ position: 'relative', zIndex: 1 }}>
        <MotionBox
          initial={{ opacity: 0, y: 30 }}
          animate={isVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
          sx={{ textAlign: 'center' }}
        >
          <Typography
            variant="h2"
            sx={{
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 700,
              fontSize: { xs: '2rem', md: '2.75rem' },
              mb: 2,
              color: isDark ? '#E6ECF5' : '#0B1B3A',
            }}
          >
            Ready to Explore?
          </Typography>

          <Typography
            variant="body1"
            sx={{
              color: isDark ? '#B8C3D9' : '#4A5D73',
              fontSize: { xs: '1rem', md: '1.125rem' },
              mb: 5,
              maxWidth: 600,
              mx: 'auto',
              lineHeight: 1.7,
            }}
          >
            Dive into the interactive demo to see AI-powered deepfake detection in action,
            or explore the full dashboard experience.
          </Typography>

          <MotionBox
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.4, 0, 0.2, 1] }}
            sx={{
              display: 'flex',
              gap: 2,
              justifyContent: 'center',
              flexWrap: 'wrap',
            }}
          >
            <Button
              variant="contained"
              size="large"
              startIcon={<PlayIcon />}
              onClick={() => navigate('/demo')}
              sx={{
                background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                color: '#fff',
                fontWeight: 600,
                fontSize: '1rem',
                textTransform: 'none',
                borderRadius: 2,
                px: 5,
                py: 1.75,
                boxShadow: `0 4px 20px ${brandColors.primary.deepSafeBlue}50`,
                '&:hover': {
                  background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
                  transform: 'translateY(-2px)',
                  boxShadow: `0 8px 30px ${brandColors.primary.deepSafeBlue}60`,
                },
                transition: 'all 0.3s ease',
              }}
            >
              Try Interactive Demo
            </Button>

            <Button
              variant="outlined"
              size="large"
              startIcon={<GitHubIcon />}
              component="a"
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              sx={{
                borderColor: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.2)',
                color: isDark ? '#E6ECF5' : '#0B1B3A',
                fontWeight: 600,
                fontSize: '1rem',
                textTransform: 'none',
                borderRadius: 2,
                px: 4,
                py: 1.75,
                '&:hover': {
                  borderColor: brandColors.primary.signalTeal,
                  background: `${brandColors.primary.signalTeal}10`,
                },
              }}
            >
              View on GitHub
            </Button>
          </MotionBox>

          {/* Tech badges */}
          <MotionBox
            initial={{ opacity: 0 }}
            animate={isVisible ? { opacity: 1 } : { opacity: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            sx={{
              mt: 6,
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'center',
              gap: 1.5,
            }}
          >
            {['React', 'TypeScript', 'Material-UI', 'FastAPI', 'TensorFlow'].map((tech) => (
              <Box
                key={tech}
                sx={{
                  px: 2,
                  py: 0.5,
                  borderRadius: 4,
                  background: isDark
                    ? 'rgba(255, 255, 255, 0.05)'
                    : 'rgba(0, 0, 0, 0.05)',
                  border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: isDark ? '#B8C3D9' : '#4A5D73',
                    fontWeight: 500,
                    fontSize: '0.75rem',
                  }}
                >
                  {tech}
                </Typography>
              </Box>
            ))}
          </MotionBox>
        </MotionBox>
      </Container>
    </Box>
  );
};

export default CTASection;
