import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { motion } from 'framer-motion';
import { Section } from './Section';
import { useScrollAnimation } from '../hooks/useScrollAnimation';
import { brandColors } from '../../../theme/colors';

const MotionBox = motion.create(Box);

interface DiagramBoxProps {
  children: React.ReactNode;
  delay?: number;
  isVisible: boolean;
  variant?: 'primary' | 'secondary' | 'accent';
}

const DiagramBox: React.FC<DiagramBoxProps> = ({ children, delay = 0, isVisible, variant = 'primary' }) => {
  const theme = useTheme();
  const themeDark = theme.palette.mode === 'dark';

  const getStyles = () => {
    switch (variant) {
      case 'accent':
        return {
          background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}30 0%, ${brandColors.primary.signalTeal}30 100%)`,
          border: `1px solid ${brandColors.primary.signalTeal}50`,
        };
      case 'secondary':
        return {
          background: themeDark
            ? 'rgba(26, 39, 64, 0.8)'
            : 'rgba(238, 242, 247, 0.9)',
          border: `1px solid ${themeDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
        };
      default:
        return {
          background: themeDark
            ? 'rgba(18, 28, 46, 0.9)'
            : 'rgba(255, 255, 255, 0.9)',
          border: `1px solid ${themeDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
        };
    }
  };

  return (
    <MotionBox
      initial={{ opacity: 0, y: 20 }}
      animate={isVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
      transition={{ duration: 0.5, delay, ease: [0.4, 0, 0.2, 1] }}
      sx={{
        p: 2,
        borderRadius: 2,
        textAlign: 'center',
        ...getStyles(),
      }}
    >
      {children}
    </MotionBox>
  );
};

const ConnectorLine: React.FC<{ delay: number; isVisible: boolean; direction?: 'down' | 'right' }> = ({
  delay,
  isVisible,
  direction = 'down',
}) => {
  return (
    <MotionBox
      initial={{ opacity: 0, scaleY: direction === 'down' ? 0 : 1, scaleX: direction === 'right' ? 0 : 1 }}
      animate={
        isVisible
          ? { opacity: 1, scaleY: 1, scaleX: 1 }
          : { opacity: 0, scaleY: direction === 'down' ? 0 : 1, scaleX: direction === 'right' ? 0 : 1 }
      }
      transition={{ duration: 0.4, delay }}
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        py: direction === 'down' ? 1 : 0,
        px: direction === 'right' ? 1 : 0,
      }}
    >
      <Box
        sx={{
          width: direction === 'down' ? 2 : 40,
          height: direction === 'down' ? 30 : 2,
          background: `linear-gradient(${direction === 'down' ? '180deg' : '90deg'}, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
          borderRadius: 1,
        }}
      />
    </MotionBox>
  );
};

export const ArchitectureSection: React.FC = () => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const { ref, isVisible } = useScrollAnimation({ threshold: 0.2 });

  return (
    <Section
      id="architecture"
      title="System Design"
      subtitle="Enterprise-grade architecture built for real-time threat detection"
      background="alternate"
    >
      <Box
        ref={ref}
        sx={{
          maxWidth: 900,
          mx: 'auto',
          p: { xs: 2, md: 4 },
        }}
      >
        {/* Video Platform Layer */}
        <DiagramBox delay={0} isVisible={isVisible} variant="secondary">
          <Typography
            variant="overline"
            sx={{ color: isDark ? '#7F8CA8' : '#7B8CA5', fontSize: '0.65rem' }}
          >
            Integration Layer
          </Typography>
          <Typography
            sx={{
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 600,
              color: isDark ? '#E6ECF5' : '#0B1B3A',
              fontSize: '1rem',
              mb: 0.5,
            }}
          >
            Video Platforms
          </Typography>
          <Typography variant="caption" sx={{ color: isDark ? '#B8C3D9' : '#4A5D73' }}>
            Zoom • Microsoft Teams • Google Meet • Slack
          </Typography>
        </DiagramBox>

        <ConnectorLine delay={0.2} isVisible={isVisible} />

        {/* DeepSafe Engine */}
        <DiagramBox delay={0.3} isVisible={isVisible} variant="accent">
          <Typography
            variant="overline"
            sx={{ color: brandColors.primary.signalTeal, fontSize: '0.65rem' }}
          >
            Core Engine
          </Typography>
          <Typography
            sx={{
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 700,
              background: `linear-gradient(90deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontSize: '1.25rem',
              mb: 2,
            }}
          >
            DeepSafe Analysis Engine
          </Typography>

          {/* Analyzer Grid */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: 'repeat(2, 1fr)', sm: 'repeat(4, 1fr)' },
              gap: 1.5,
              mb: 2,
            }}
          >
            {[
              { name: 'Video', weight: '40%', icon: '🎥' },
              { name: 'Audio', weight: '30%', icon: '🎙️' },
              { name: 'Behavioral', weight: '20%', icon: '🧠' },
              { name: 'Network', weight: '10%', icon: '🌐' },
            ].map((analyzer, index) => (
              <MotionBox
                key={analyzer.name}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={isVisible ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.4, delay: 0.4 + index * 0.1 }}
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  background: isDark
                    ? 'rgba(11, 18, 32, 0.8)'
                    : 'rgba(255, 255, 255, 0.9)',
                  border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)'}`,
                }}
              >
                <Typography sx={{ fontSize: '1.5rem', mb: 0.5 }}>{analyzer.icon}</Typography>
                <Typography
                  sx={{
                    fontWeight: 600,
                    fontSize: '0.75rem',
                    color: isDark ? '#E6ECF5' : '#0B1B3A',
                  }}
                >
                  {analyzer.name}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{ color: brandColors.primary.signalTeal, fontWeight: 600 }}
                >
                  {analyzer.weight}
                </Typography>
              </MotionBox>
            ))}
          </Box>

          {/* Risk Aggregator */}
          <MotionBox
            initial={{ opacity: 0 }}
            animate={isVisible ? { opacity: 1 } : { opacity: 0 }}
            transition={{ duration: 0.4, delay: 0.8 }}
            sx={{
              p: 2,
              borderRadius: 2,
              background: isDark
                ? 'rgba(11, 18, 32, 0.6)'
                : 'rgba(247, 249, 252, 0.9)',
              border: `1px solid ${brandColors.primary.signalTeal}30`,
            }}
          >
            <Typography
              sx={{
                fontWeight: 600,
                fontSize: '0.875rem',
                color: isDark ? '#E6ECF5' : '#0B1B3A',
              }}
            >
              Risk Aggregator
            </Typography>
            <Typography
              variant="caption"
              sx={{ color: isDark ? '#7F8CA8' : '#7B8CA5' }}
            >
              Weighted Analysis • Confidence Scoring • Threshold Triggers
            </Typography>
          </MotionBox>
        </DiagramBox>

        <ConnectorLine delay={0.9} isVisible={isVisible} />

        {/* Security Dashboard */}
        <DiagramBox delay={1} isVisible={isVisible} variant="primary">
          <Typography
            variant="overline"
            sx={{ color: isDark ? '#7F8CA8' : '#7B8CA5', fontSize: '0.65rem' }}
          >
            Output Layer
          </Typography>
          <Typography
            sx={{
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 600,
              color: isDark ? '#E6ECF5' : '#0B1B3A',
              fontSize: '1rem',
              mb: 0.5,
            }}
          >
            Security Dashboard
          </Typography>
          <Typography variant="caption" sx={{ color: isDark ? '#B8C3D9' : '#4A5D73' }}>
            Real-time Alerts • Forensic Reports • Incident Management
          </Typography>
        </DiagramBox>

        {/* Technology badges */}
        <MotionBox
          initial={{ opacity: 0 }}
          animate={isVisible ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: 0.5, delay: 1.2 }}
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: 1,
            mt: 4,
          }}
        >
          {['WebSocket', 'WebRTC', 'REST API', 'Real-time Processing'].map((tech) => (
            <Box
              key={tech}
              sx={{
                px: 2,
                py: 0.5,
                borderRadius: 4,
                background: isDark
                  ? 'rgba(31, 182, 166, 0.1)'
                  : 'rgba(31, 182, 166, 0.15)',
                border: `1px solid ${brandColors.primary.signalTeal}30`,
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  color: brandColors.primary.signalTeal,
                  fontWeight: 500,
                  fontSize: '0.7rem',
                }}
              >
                {tech}
              </Typography>
            </Box>
          ))}
        </MotionBox>
      </Box>
    </Section>
  );
};

export default ArchitectureSection;
