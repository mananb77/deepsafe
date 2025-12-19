import React from 'react';
import { Box, Typography, Card, CardContent, Chip, Divider, Grid } from '@mui/material';
import { motion } from 'framer-motion';
import {
  Shield as ShieldIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  AccessTime as TimeIcon,
  AttachMoney as MoneyIcon,
  Timeline as TimelineIcon,
  Gavel as GavelIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors, getRiskColor } from '../../../../theme/colors';
import { darkGradients, lightGradients, glassMorphism, functionalGradients } from '../../../../theme/gradients';
import { screenVariants, staggerContainerVariants, staggerItemVariants } from '../../constants/animations';
import { demoIncident, demoTimeline } from '../../data/demoScenario';

const MotionBox = motion.create(Box);

interface TimelineItemProps {
  event: (typeof demoTimeline)[0];
  isLast: boolean;
  isDark: boolean;
}

const TimelineItem: React.FC<TimelineItemProps> = ({ event, isLast, isDark }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error':
        return brandColors.primary.threatRed;
      case 'warning':
        return brandColors.primary.alertAmber;
      case 'success':
        return brandColors.statusDark.success;
      default:
        return brandColors.primary.signalTeal;
    }
  };

  return (
    <Box sx={{ display: 'flex', gap: 2, position: 'relative' }}>
      {/* Timeline line */}
      {!isLast && (
        <Box
          sx={{
            position: 'absolute',
            left: 11,
            top: 24,
            bottom: -16,
            width: 2,
            backgroundColor: isDark
              ? 'rgba(255, 255, 255, 0.1)'
              : 'rgba(0, 0, 0, 0.08)',
          }}
        />
      )}

      {/* Dot */}
      <Box
        sx={{
          width: 24,
          height: 24,
          borderRadius: '50%',
          backgroundColor: getSeverityColor(event.severity),
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          zIndex: 1,
        }}
      >
        {event.severity === 'success' ? (
          <CheckIcon sx={{ fontSize: 14, color: '#FFFFFF' }} />
        ) : event.severity === 'error' ? (
          <WarningIcon sx={{ fontSize: 14, color: '#FFFFFF' }} />
        ) : (
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: '#FFFFFF',
            }}
          />
        )}
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, pb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
          <Typography
            variant="body2"
            sx={{
              fontWeight: 600,
              color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
            }}
          >
            {event.title}
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
              fontFamily: 'monospace',
            }}
          >
            {event.timestamp}
          </Typography>
          {event.riskScore && (
            <Chip
              label={`${event.riskScore}%`}
              size="small"
              sx={{
                height: 18,
                fontSize: '0.65rem',
                fontWeight: 600,
                backgroundColor: `${getRiskColor(event.riskScore, isDark)}20`,
                color: getRiskColor(event.riskScore, isDark),
              }}
            />
          )}
        </Box>
        <Typography
          variant="caption"
          sx={{
            color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
          }}
        >
          {event.description}
        </Typography>
      </Box>
    </Box>
  );
};

export const IncidentReportScreen: React.FC = () => {
  const { isDark } = useThemeMode();
  const gradients = isDark ? darkGradients : lightGradients;
  const glass = glassMorphism(isDark ? 'dark' : 'light');

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <MotionBox
      variants={screenVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      sx={{
        minHeight: '100vh',
        background: gradients.signature,
        px: { xs: 2, sm: 4 },
        py: { xs: 4, sm: 6 },
        pb: { xs: 12, sm: 14 },
      }}
    >
      <MotionBox
        variants={staggerContainerVariants}
        initial="initial"
        animate="animate"
        sx={{ maxWidth: 1000, mx: 'auto' }}
      >
        {/* Header */}
        <MotionBox
          variants={staggerItemVariants}
          sx={{ textAlign: 'center', mb: 5 }}
        >
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 64,
              height: 64,
              borderRadius: 3,
              background: functionalGradients.success,
              mb: 2,
            }}
          >
            <ShieldIcon sx={{ fontSize: 32, color: '#FFFFFF' }} />
          </Box>
          <Typography
            variant="h4"
            sx={{
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 700,
              color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
              mb: 1,
            }}
          >
            Incident Report
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
            }}
          >
            Threat successfully neutralized • Evidence preserved
          </Typography>
        </MotionBox>

        <Grid container spacing={3}>
          {/* Incident Summary Card */}
          <Grid size={{ xs: 12, md: 6 }}>
            <MotionBox variants={staggerItemVariants}>
              <Card
                sx={{
                  height: '100%',
                  ...glass,
                  border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'}`,
                  borderRadius: 3,
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                    <GavelIcon
                      sx={{
                        fontSize: 20,
                        color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                      }}
                    />
                    <Typography
                      variant="subtitle1"
                      sx={{
                        fontWeight: 600,
                        color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                      }}
                    >
                      Incident Summary
                    </Typography>
                  </Box>

                  {/* Incident ID */}
                  <Box sx={{ mb: 2 }}>
                    <Typography
                      variant="caption"
                      sx={{
                        color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                      }}
                    >
                      Incident ID
                    </Typography>
                    <Typography
                      variant="body2"
                      id="incident-type"
                      sx={{
                        fontFamily: 'monospace',
                        color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                        fontWeight: 500,
                      }}
                    >
                      {demoIncident.id}
                    </Typography>
                  </Box>

                  {/* Type */}
                  <Box sx={{ mb: 2 }}>
                    <Typography
                      variant="caption"
                      sx={{
                        color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                      }}
                    >
                      Attack Type
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                      <Chip
                        label="Deepfake Impersonation"
                        size="small"
                        sx={{
                          backgroundColor: `${brandColors.primary.threatRed}20`,
                          color: brandColors.primary.threatRed,
                          fontWeight: 600,
                        }}
                      />
                    </Box>
                  </Box>

                  {/* Description */}
                  <Box sx={{ mb: 2 }}>
                    <Typography
                      variant="caption"
                      sx={{
                        color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                      }}
                    >
                      Description
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                        mt: 0.5,
                      }}
                    >
                      {demoIncident.description}
                    </Typography>
                  </Box>

                  <Divider sx={{ my: 2, borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)' }} />

                  {/* Risk Breakdown */}
                  <Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: isDark ? brandColors.darkText.muted : brandColors.lightText.muted,
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                      }}
                    >
                      Risk Breakdown
                    </Typography>
                    <Box sx={{ mt: 1.5, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      {[
                        { label: 'Video Risk', value: demoIncident.riskBreakdown.videoRisk },
                        { label: 'Audio Risk', value: demoIncident.riskBreakdown.audioRisk },
                        { label: 'Credential Risk', value: demoIncident.riskBreakdown.credentialRisk },
                      ].map((item) => (
                        <Box key={item.label}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                            <Typography variant="caption" sx={{ color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary }}>
                              {item.label}
                            </Typography>
                            <Typography variant="caption" sx={{ color: getRiskColor(item.value, isDark), fontWeight: 600 }}>
                              {item.value}%
                            </Typography>
                          </Box>
                          <Box
                            sx={{
                              height: 4,
                              borderRadius: 2,
                              backgroundColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)',
                              overflow: 'hidden',
                            }}
                          >
                            <Box
                              sx={{
                                height: '100%',
                                width: `${item.value}%`,
                                borderRadius: 2,
                                background: functionalGradients.riskScore,
                              }}
                            />
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </MotionBox>
          </Grid>

          {/* Stats & Timeline Card */}
          <Grid size={{ xs: 12, md: 6 }}>
            <MotionBox variants={staggerItemVariants} sx={{ display: 'flex', flexDirection: 'column', gap: 3, height: '100%' }}>
              {/* Stats Row */}
              <Box sx={{ display: 'flex', gap: 2 }}>
                {/* Amount Protected */}
                <Card
                  id="amount-protected"
                  sx={{
                    flex: 1,
                    ...glass,
                    border: `1px solid ${brandColors.statusDark.success}40`,
                    borderRadius: 3,
                  }}
                >
                  <CardContent sx={{ p: 2, textAlign: 'center' }}>
                    <MoneyIcon sx={{ fontSize: 28, color: brandColors.statusDark.success, mb: 1 }} />
                    <Typography
                      variant="h5"
                      sx={{
                        fontFamily: '"Space Grotesk", sans-serif',
                        fontWeight: 700,
                        color: brandColors.statusDark.success,
                      }}
                    >
                      {formatCurrency(demoIncident.amountProtected)}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{ color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary }}
                    >
                      Amount Protected
                    </Typography>
                  </CardContent>
                </Card>

                {/* Detection Time */}
                <Card
                  sx={{
                    flex: 1,
                    ...glass,
                    border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'}`,
                    borderRadius: 3,
                  }}
                >
                  <CardContent sx={{ p: 2, textAlign: 'center' }}>
                    <TimeIcon sx={{ fontSize: 28, color: brandColors.primary.signalTeal, mb: 1 }} />
                    <Typography
                      variant="h5"
                      sx={{
                        fontFamily: '"Space Grotesk", sans-serif',
                        fontWeight: 700,
                        color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                      }}
                    >
                      {demoIncident.detectionTime}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{ color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary }}
                    >
                      Detection Time
                    </Typography>
                  </CardContent>
                </Card>
              </Box>

              {/* Timeline Card */}
              <Card
                id="incident-timeline"
                sx={{
                  flex: 1,
                  ...glass,
                  border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'}`,
                  borderRadius: 3,
                  overflow: 'auto',
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                    <TimelineIcon
                      sx={{
                        fontSize: 20,
                        color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                      }}
                    />
                    <Typography
                      variant="subtitle1"
                      sx={{
                        fontWeight: 600,
                        color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                      }}
                    >
                      Event Timeline
                    </Typography>
                  </Box>

                  <Box sx={{ mt: 2 }}>
                    {demoTimeline.map((event, index) => (
                      <TimelineItem
                        key={event.id}
                        event={event}
                        isLast={index === demoTimeline.length - 1}
                        isDark={isDark}
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </MotionBox>
          </Grid>

          {/* Evidence Links */}
          <Grid size={{ xs: 12 }}>
            <MotionBox variants={staggerItemVariants}>
              <Card
                id="evidence-links"
                sx={{
                  ...glass,
                  border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'}`,
                  borderRadius: 3,
                }}
              >
                <CardContent sx={{ p: 3, display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
                  <Typography
                    variant="body2"
                    sx={{
                      color: isDark ? brandColors.darkText.secondary : brandColors.lightText.secondary,
                      fontWeight: 500,
                    }}
                  >
                    Evidence Preserved:
                  </Typography>
                  {[
                    'Video Recording',
                    'Audio Analysis',
                    'Network Logs',
                    'Behavioral Profile',
                    'Chat Transcript',
                  ].map((item) => (
                    <Chip
                      key={item}
                      label={item}
                      size="small"
                      clickable
                      sx={{
                        backgroundColor: isDark
                          ? 'rgba(31, 182, 166, 0.1)'
                          : 'rgba(31, 60, 136, 0.1)',
                        color: isDark ? brandColors.primary.signalTeal : brandColors.primary.deepSafeBlue,
                        fontWeight: 500,
                        '&:hover': {
                          backgroundColor: isDark
                            ? 'rgba(31, 182, 166, 0.2)'
                            : 'rgba(31, 60, 136, 0.15)',
                        },
                      }}
                    />
                  ))}
                </CardContent>
              </Card>
            </MotionBox>
          </Grid>
        </Grid>
      </MotionBox>
    </MotionBox>
  );
};

export default IncidentReportScreen;
