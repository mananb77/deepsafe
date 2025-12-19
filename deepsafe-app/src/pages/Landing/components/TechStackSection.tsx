import React from 'react';
import { Box, Typography, useTheme, Grid, Paper, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import { Section } from './Section';
import { useScrollAnimation } from '../hooks/useScrollAnimation';
import { frontendStack, backendStack, aiStack } from '../data/techStack';
import type { Technology } from '../data/techStack';
import { brandColors } from '../../../theme/colors';

const MotionBox = motion.create(Box);

interface TechTableProps {
  title: string;
  technologies: Technology[];
  delay?: number;
  accent?: string;
}

const TechTable: React.FC<TechTableProps> = ({ title, technologies, delay = 0, accent }) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const { ref, isVisible } = useScrollAnimation({ threshold: 0.2 });

  return (
    <MotionBox
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{ duration: 0.6, delay, ease: [0.4, 0, 0.2, 1] }}
    >
      <Paper
        elevation={0}
        sx={{
          borderRadius: 3,
          overflow: 'hidden',
          background: isDark
            ? 'linear-gradient(135deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.8) 100%)'
            : 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.9) 100%)',
          border: `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
          height: '100%',
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            background: accent
              ? `linear-gradient(135deg, ${accent}15 0%, ${accent}05 100%)`
              : isDark
              ? 'rgba(11, 18, 32, 0.5)'
              : 'rgba(238, 242, 247, 0.8)',
            borderBottom: `1px solid ${isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'}`,
          }}
        >
          <Typography
            sx={{
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 600,
              fontSize: '1rem',
              color: accent || (isDark ? '#E6ECF5' : '#0B1B3A'),
            }}
          >
            {title}
          </Typography>
        </Box>

        {/* Technologies */}
        <Box sx={{ p: 2 }}>
          {technologies.map((tech, index) => (
            <Box
              key={tech.name}
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                py: 1.5,
                borderBottom:
                  index < technologies.length - 1
                    ? `1px solid ${isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'}`
                    : 'none',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <Box
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: accent || brandColors.primary.signalTeal,
                  }}
                />
                <Box>
                  <Typography
                    sx={{
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      color: isDark ? '#E6ECF5' : '#0B1B3A',
                    }}
                  >
                    {tech.name}
                    {tech.version && (
                      <Typography
                        component="span"
                        sx={{
                          ml: 1,
                          fontSize: '0.7rem',
                          color: isDark ? '#7F8CA8' : '#7B8CA5',
                          fontFamily: '"JetBrains Mono", monospace',
                        }}
                      >
                        v{tech.version}
                      </Typography>
                    )}
                  </Typography>
                </Box>
              </Box>
              <Chip
                label={tech.purpose}
                size="small"
                sx={{
                  height: 24,
                  fontSize: '0.7rem',
                  fontWeight: 500,
                  background: isDark
                    ? 'rgba(255, 255, 255, 0.05)'
                    : 'rgba(0, 0, 0, 0.05)',
                  color: isDark ? '#B8C3D9' : '#4A5D73',
                  border: 'none',
                }}
              />
            </Box>
          ))}
        </Box>
      </Paper>
    </MotionBox>
  );
};

export const TechStackSection: React.FC = () => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  return (
    <Section
      id="tech-stack"
      title="Built for Enterprise"
      subtitle="Modern technology stack designed for performance, security, and scalability"
      background="default"
    >
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <TechTable
            title="Frontend"
            technologies={frontendStack}
            delay={0}
            accent={brandColors.primary.signalTeal}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <TechTable
            title="Backend"
            technologies={backendStack}
            delay={0.1}
            accent={brandColors.primary.deepSafeBlue}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <TechTable
            title="AI / ML"
            technologies={aiStack}
            delay={0.2}
            accent="#9B59B6"
          />
        </Grid>
      </Grid>

      {/* Key Features */}
      <Box sx={{ mt: 6, textAlign: 'center' }}>
        <Grid container spacing={2} justifyContent="center">
          {[
            { label: 'Type-Safe', icon: '🔒' },
            { label: 'Real-time', icon: '⚡' },
            { label: 'Scalable', icon: '📈' },
            { label: 'Secure', icon: '🛡️' },
          ].map((feature, index) => (
            <Grid key={feature.label} size={{ xs: 6, sm: 3 }}>
              <MotionBox
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                sx={{
                  p: 2,
                  borderRadius: 2,
                  background: isDark
                    ? 'rgba(31, 182, 166, 0.05)'
                    : 'rgba(31, 182, 166, 0.1)',
                  border: `1px solid ${brandColors.primary.signalTeal}20`,
                }}
              >
                <Typography sx={{ fontSize: '1.5rem', mb: 0.5 }}>{feature.icon}</Typography>
                <Typography
                  sx={{
                    fontWeight: 600,
                    fontSize: '0.875rem',
                    color: isDark ? '#E6ECF5' : '#0B1B3A',
                  }}
                >
                  {feature.label}
                </Typography>
              </MotionBox>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Section>
  );
};

export default TechStackSection;
