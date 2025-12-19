import React from 'react';
import { Box, Container, Typography, useTheme } from '@mui/material';
import { motion } from 'framer-motion';
import { useScrollAnimation } from '../hooks/useScrollAnimation';

interface SectionProps {
  id?: string;
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  background?: 'default' | 'alternate' | 'gradient';
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | false;
  py?: number | { xs?: number; sm?: number; md?: number };
  centerTitle?: boolean;
}

const MotionBox = motion.create(Box);

export const Section: React.FC<SectionProps> = ({
  id,
  title,
  subtitle,
  children,
  background = 'default',
  maxWidth = 'lg',
  py = { xs: 8, md: 12 },
  centerTitle = true,
}) => {
  const theme = useTheme();
  const { ref, isVisible } = useScrollAnimation({ threshold: 0.1 });
  const isDark = theme.palette.mode === 'dark';

  const getBackground = () => {
    switch (background) {
      case 'alternate':
        return isDark ? 'rgba(18, 28, 46, 0.5)' : 'rgba(238, 242, 247, 0.5)';
      case 'gradient':
        return isDark
          ? 'linear-gradient(180deg, #0B1220 0%, #121C2E 100%)'
          : 'linear-gradient(180deg, #F7F9FC 0%, #EEF2F7 100%)';
      default:
        return 'transparent';
    }
  };

  return (
    <Box
      component="section"
      id={id}
      ref={ref}
      sx={{
        py,
        background: getBackground(),
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <Container maxWidth={maxWidth}>
        <MotionBox
          initial={{ opacity: 0, y: 30 }}
          animate={isVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        >
          {(title || subtitle) && (
            <Box
              sx={{
                textAlign: centerTitle ? 'center' : 'left',
                mb: { xs: 4, md: 6 },
              }}
            >
              {title && (
                <Typography
                  variant="h2"
                  component="h2"
                  sx={{
                    fontFamily: '"Space Grotesk", sans-serif',
                    fontWeight: 700,
                    fontSize: { xs: '2rem', md: '2.5rem' },
                    mb: subtitle ? 2 : 0,
                    background: isDark
                      ? 'linear-gradient(90deg, #E6ECF5 0%, #1FB6A6 100%)'
                      : 'linear-gradient(90deg, #1F3C88 0%, #1FB6A6 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  {title}
                </Typography>
              )}
              {subtitle && (
                <Typography
                  variant="body1"
                  sx={{
                    color: isDark ? 'rgba(184, 195, 217, 0.9)' : 'rgba(74, 93, 115, 0.9)',
                    fontSize: { xs: '1rem', md: '1.125rem' },
                    maxWidth: 700,
                    mx: centerTitle ? 'auto' : 0,
                  }}
                >
                  {subtitle}
                </Typography>
              )}
            </Box>
          )}
          {children}
        </MotionBox>
      </Container>
    </Box>
  );
};

export default Section;
