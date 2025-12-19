import React from 'react';
import { Box, Typography, useTheme, Grid, Paper, IconButton } from '@mui/material';
import { motion } from 'framer-motion';
import { ContentCopy as CopyIcon, Check as CheckIcon } from '@mui/icons-material';
import { Section } from './Section';
import { useScrollAnimation } from '../hooks/useScrollAnimation';
import { installationSteps, projectStructure } from '../data/techStack';
import { brandColors } from '../../../theme/colors';

const MotionBox = motion.create(Box);

const CodeBlock: React.FC<{ code: string; language?: string }> = ({ code }) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Box
      sx={{
        position: 'relative',
        borderRadius: 2,
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          p: 2,
          background: isDark ? '#0B1220' : '#1F2937',
          fontFamily: '"JetBrains Mono", monospace',
          fontSize: '0.8rem',
          lineHeight: 1.6,
          color: '#E6ECF5',
          overflowX: 'auto',
          whiteSpace: 'pre',
        }}
      >
        {code}
      </Box>
      <IconButton
        onClick={handleCopy}
        size="small"
        sx={{
          position: 'absolute',
          top: 8,
          right: 8,
          color: copied ? brandColors.statusDark.success : 'rgba(255,255,255,0.5)',
          background: 'rgba(0,0,0,0.3)',
          '&:hover': {
            background: 'rgba(0,0,0,0.5)',
          },
        }}
      >
        {copied ? <CheckIcon fontSize="small" /> : <CopyIcon fontSize="small" />}
      </IconButton>
    </Box>
  );
};

export const SetupSection: React.FC = () => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const { ref: stepsRef, isVisible: stepsVisible } = useScrollAnimation({ threshold: 0.2 });
  const { ref: structureRef, isVisible: structureVisible } = useScrollAnimation({ threshold: 0.2 });

  return (
    <Section
      id="setup"
      title="Get Started"
      subtitle="Set up DeepSafe locally in minutes"
      background="default"
    >
      <Grid container spacing={4}>
        {/* Installation Steps */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Box ref={stepsRef}>
            <Typography
              variant="h6"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                fontSize: '1rem',
                color: isDark ? '#E6ECF5' : '#0B1B3A',
                mb: 3,
              }}
            >
              Quick Start
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {installationSteps.map((step, index) => (
                <MotionBox
                  key={step.step}
                  initial={{ opacity: 0, x: -20 }}
                  animate={stepsVisible ? { opacity: 1, x: 0 } : { opacity: 0, x: -20 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: isDark
                        ? 'rgba(18, 28, 46, 0.6)'
                        : 'rgba(255, 255, 255, 0.9)',
                      border: `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                      <Box
                        sx={{
                          width: 28,
                          height: 28,
                          borderRadius: '50%',
                          background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                        }}
                      >
                        <Typography
                          sx={{
                            color: '#fff',
                            fontWeight: 700,
                            fontSize: '0.75rem',
                          }}
                        >
                          {step.step}
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography
                          variant="caption"
                          sx={{
                            color: isDark ? '#7F8CA8' : '#7B8CA5',
                            display: 'block',
                            mb: 0.5,
                          }}
                        >
                          {step.description}
                        </Typography>
                        <Box
                          sx={{
                            p: 1,
                            borderRadius: 1,
                            background: isDark ? '#0B1220' : '#1F2937',
                            fontFamily: '"JetBrains Mono", monospace',
                            fontSize: '0.75rem',
                            color: brandColors.primary.signalTeal,
                            overflowX: 'auto',
                          }}
                        >
                          {step.command}
                        </Box>
                      </Box>
                    </Box>
                  </Paper>
                </MotionBox>
              ))}
            </Box>
          </Box>
        </Grid>

        {/* Project Structure */}
        <Grid size={{ xs: 12, md: 6 }}>
          <MotionBox
            ref={structureRef}
            initial={{ opacity: 0, y: 20 }}
            animate={structureVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Typography
              variant="h6"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                fontSize: '1rem',
                color: isDark ? '#E6ECF5' : '#0B1B3A',
                mb: 3,
              }}
            >
              Project Structure
            </Typography>

            <CodeBlock code={projectStructure.trim()} />

            {/* Links */}
            <Box sx={{ mt: 3 }}>
              <Typography
                variant="body2"
                sx={{
                  color: isDark ? '#B8C3D9' : '#4A5D73',
                  mb: 2,
                }}
              >
                For detailed documentation and contribution guidelines:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {[
                  { label: 'GitHub Repository', href: 'https://github.com' },
                  { label: 'Documentation', href: '#' },
                  { label: 'API Reference', href: '#' },
                ].map((link) => (
                  <Box
                    key={link.label}
                    component="a"
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{
                      px: 2,
                      py: 0.75,
                      borderRadius: 4,
                      background: isDark
                        ? 'rgba(31, 182, 166, 0.1)'
                        : 'rgba(31, 182, 166, 0.15)',
                      border: `1px solid ${brandColors.primary.signalTeal}30`,
                      color: brandColors.primary.signalTeal,
                      textDecoration: 'none',
                      fontSize: '0.8rem',
                      fontWeight: 500,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        background: `${brandColors.primary.signalTeal}20`,
                        borderColor: brandColors.primary.signalTeal,
                      },
                    }}
                  >
                    {link.label}
                  </Box>
                ))}
              </Box>
            </Box>
          </MotionBox>
        </Grid>
      </Grid>
    </Section>
  );
};

export default SetupSection;
