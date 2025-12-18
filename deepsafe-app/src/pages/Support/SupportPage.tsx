import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  InputAdornment,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Button,
  Chip,
  Link,
  Alert,
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  PlayCircle as GetStartedIcon,
  Psychology as RiskScoreIcon,
  BugReport as IncidentIcon,
  Code as ApiIcon,
  Email as EmailIcon,
  Chat as ChatIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  MenuBook as DocumentationIcon,
  NewReleases as ReleaseNotesIcon,
  SupportAgent as SupportIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useThemeMode } from '../../context/ThemeContext';
import { brandColors } from '../../theme/colors';
import { faqItems, systemStatus, type SystemStatus } from '../../data/user';

interface QuickHelpCardProps {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick: (id: string) => void;
}

const QuickHelpCard: React.FC<QuickHelpCardProps> = ({ id, title, description, icon, onClick }) => {
  const { isDark } = useThemeMode();

  return (
    <Paper
      onClick={() => onClick(id)}
      sx={{
        p: 3,
        cursor: 'pointer',
        background: isDark
          ? 'linear-gradient(180deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.6) 100%)'
          : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.8) 100%)',
        backdropFilter: 'blur(10px)',
        border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
        borderRadius: 3,
        transition: 'all 0.2s ease',
        height: '100%',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: isDark
            ? `0 12px 40px ${brandColors.primary.deepSafeBlue}30`
            : '0 8px 32px rgba(0, 0, 0, 0.1)',
          border: `1px solid ${brandColors.primary.signalTeal}40`,
        },
      }}
    >
      <Box
        sx={{
          p: 1.5,
          borderRadius: 2,
          background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue}20 0%, ${brandColors.primary.signalTeal}20 100%)`,
          display: 'inline-flex',
          mb: 2,
        }}
      >
        {icon}
      </Box>
      <Typography
        variant="h6"
        sx={{
          fontFamily: '"Space Grotesk", sans-serif',
          fontWeight: 600,
          fontSize: '1rem',
          mb: 1,
        }}
      >
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {description}
      </Typography>
    </Paper>
  );
};

const getStatusIcon = (status: SystemStatus['status']) => {
  switch (status) {
    case 'operational':
      return <CheckCircleIcon sx={{ fontSize: 18, color: brandColors.statusDark.success }} />;
    case 'degraded':
      return <WarningIcon sx={{ fontSize: 18, color: brandColors.primary.alertAmber }} />;
    case 'outage':
      return <ErrorIcon sx={{ fontSize: 18, color: brandColors.primary.threatRed }} />;
  }
};

const getStatusColor = (status: SystemStatus['status'], isDark: boolean) => {
  const colors = isDark ? brandColors.statusDark : brandColors.statusLight;
  switch (status) {
    case 'operational':
      return colors.success;
    case 'degraded':
      return brandColors.primary.alertAmber;
    case 'outage':
      return brandColors.primary.threatRed;
  }
};

export const SupportPage: React.FC = () => {
  const { isDark } = useThemeMode();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  const categories = [
    { id: 'general', label: 'General' },
    { id: 'technical', label: 'Technical' },
    { id: 'security', label: 'Security' },
    { id: 'billing', label: 'Billing' },
  ];

  const filteredFAQs = faqItems.filter((faq) => {
    const matchesSearch =
      searchQuery === '' ||
      faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === null || faq.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleOpenArticle = (articleId: string) => {
    navigate(`/support/articles/${articleId}`);
  };

  const quickHelpCards = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      description: 'Learn the basics of DeepSafe and set up your first meeting protection.',
      icon: <GetStartedIcon sx={{ color: brandColors.primary.signalTeal, fontSize: 24 }} />,
    },
    {
      id: 'risk-scores',
      title: 'Understanding Risk Scores',
      description: 'Learn how our AI calculates and presents threat confidence levels.',
      icon: <RiskScoreIcon sx={{ color: brandColors.primary.signalTeal, fontSize: 24 }} />,
    },
    {
      id: 'incident-response',
      title: 'Incident Response',
      description: 'Best practices for handling detected threats and false positives.',
      icon: <IncidentIcon sx={{ color: brandColors.primary.signalTeal, fontSize: 24 }} />,
    },
    {
      id: 'api-documentation',
      title: 'API Documentation',
      description: 'Integrate DeepSafe with your existing security infrastructure.',
      icon: <ApiIcon sx={{ color: brandColors.primary.signalTeal, fontSize: 24 }} />,
    },
  ];

  const allOperational = systemStatus.every((s) => s.status === 'operational');

  return (
    <Box
      sx={{
        p: { xs: 2, md: 4 },
        maxWidth: 1200,
        mx: 'auto',
      }}
    >
      {/* Page Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography
          variant="h4"
          sx={{
            fontFamily: '"Space Grotesk", sans-serif',
            fontWeight: 700,
            mb: 1,
            background: isDark
              ? 'linear-gradient(90deg, #E6ECF5 0%, #B8C3D9 100%)'
              : 'linear-gradient(90deg, #0B1B3A 0%, #1F3C88 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          Help & Support
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Find answers, learn best practices, and get help when you need it
        </Typography>

        {/* Search Bar */}
        <TextField
          fullWidth
          placeholder="Search for help articles..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{
            maxWidth: 600,
            mx: 'auto',
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              backgroundColor: isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)',
            },
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {/* Quick Help Cards */}
      <Box sx={{ mb: 5 }}>
        <Typography
          variant="h6"
          sx={{
            fontFamily: '"Space Grotesk", sans-serif',
            fontWeight: 600,
            mb: 3,
          }}
        >
          Quick Help
        </Typography>
        <Grid container spacing={3}>
          {quickHelpCards.map((card) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={card.id}>
              <QuickHelpCard {...card} onClick={handleOpenArticle} />
            </Grid>
          ))}
        </Grid>
      </Box>

      <Grid container spacing={4}>
        {/* FAQ Section */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Paper
            sx={{
              p: 3,
              background: isDark
                ? 'linear-gradient(180deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.6) 100%)'
                : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.8) 100%)',
              backdropFilter: 'blur(10px)',
              border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
              borderRadius: 3,
            }}
          >
            <Typography
              variant="h6"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                mb: 2,
              }}
            >
              Frequently Asked Questions
            </Typography>

            {/* Category Filters */}
            <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
              <Chip
                label="All"
                onClick={() => setSelectedCategory(null)}
                sx={{
                  backgroundColor: selectedCategory === null
                    ? `${brandColors.primary.signalTeal}30`
                    : isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)',
                  color: selectedCategory === null ? brandColors.primary.signalTeal : 'text.secondary',
                  fontWeight: selectedCategory === null ? 600 : 400,
                  '&:hover': {
                    backgroundColor: `${brandColors.primary.signalTeal}20`,
                  },
                }}
              />
              {categories.map((cat) => (
                <Chip
                  key={cat.id}
                  label={cat.label}
                  onClick={() => setSelectedCategory(cat.id)}
                  sx={{
                    backgroundColor: selectedCategory === cat.id
                      ? `${brandColors.primary.signalTeal}30`
                      : isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)',
                    color: selectedCategory === cat.id ? brandColors.primary.signalTeal : 'text.secondary',
                    fontWeight: selectedCategory === cat.id ? 600 : 400,
                    '&:hover': {
                      backgroundColor: `${brandColors.primary.signalTeal}20`,
                    },
                  }}
                />
              ))}
            </Box>

            {/* FAQ Accordions */}
            {filteredFAQs.length > 0 ? (
              filteredFAQs.map((faq) => (
                <Accordion
                  key={faq.id}
                  sx={{
                    backgroundColor: 'transparent',
                    boxShadow: 'none',
                    '&:before': { display: 'none' },
                    '& .MuiAccordionSummary-root': {
                      px: 0,
                      minHeight: 48,
                    },
                    '& .MuiAccordionDetails-root': {
                      px: 0,
                      pb: 2,
                    },
                  }}
                >
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon sx={{ color: brandColors.primary.signalTeal }} />}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Chip
                        label={faq.category}
                        size="small"
                        sx={{
                          backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
                          fontSize: '0.7rem',
                          height: 20,
                        }}
                      />
                      <Typography variant="body1" fontWeight={500}>
                        {faq.question}
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                      {faq.answer}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))
            ) : (
              <Box sx={{ py: 4, textAlign: 'center' }}>
                <Typography color="text.secondary">
                  No results found for "{searchQuery}"
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Right Sidebar */}
        <Grid size={{ xs: 12, md: 4 }}>
          {/* Contact Support */}
          <Paper
            sx={{
              p: 3,
              mb: 3,
              background: isDark
                ? 'linear-gradient(135deg, rgba(31, 60, 136, 0.3) 0%, rgba(31, 182, 166, 0.2) 100%)'
                : 'linear-gradient(135deg, rgba(31, 60, 136, 0.1) 0%, rgba(31, 182, 166, 0.08) 100%)',
              backdropFilter: 'blur(10px)',
              border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.06)'}`,
              borderRadius: 3,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
              <SupportIcon sx={{ color: brandColors.primary.signalTeal }} />
              <Typography
                variant="h6"
                sx={{
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 600,
                }}
              >
                Contact Support
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Can't find what you're looking for? Our support team is here to help.
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <EmailIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                <Typography variant="body2">support@deepsafe.ai</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <ScheduleIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                <Typography variant="body2" color="text.secondary">
                  Response within 24 hours
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Button
                variant="contained"
                startIcon={<ChatIcon />}
                fullWidth
                sx={{
                  background: `linear-gradient(135deg, ${brandColors.primary.deepSafeBlue} 0%, ${brandColors.primary.signalTeal} 100%)`,
                  '&:hover': {
                    background: `linear-gradient(135deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
                  },
                }}
              >
                Start Live Chat
              </Button>
              <Button
                variant="outlined"
                startIcon={<EmailIcon />}
                fullWidth
                sx={{
                  borderColor: brandColors.primary.signalTeal,
                  color: brandColors.primary.signalTeal,
                  '&:hover': {
                    borderColor: brandColors.primary.signalTeal,
                    backgroundColor: `${brandColors.primary.signalTeal}10`,
                  },
                }}
              >
                Send Email
              </Button>
            </Box>

            <Alert severity="info" sx={{ mt: 2 }}>
              Enterprise customers have access to priority support with 1-hour response time.
            </Alert>
          </Paper>

          {/* Documentation Links */}
          <Paper
            sx={{
              p: 3,
              mb: 3,
              background: isDark
                ? 'linear-gradient(180deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.6) 100%)'
                : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.8) 100%)',
              backdropFilter: 'blur(10px)',
              border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
              borderRadius: 3,
            }}
          >
            <Typography
              variant="h6"
              sx={{
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                mb: 2,
              }}
            >
              Documentation
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Link
                href="#"
                underline="hover"
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                  '&:hover': { color: brandColors.primary.signalTeal },
                }}
              >
                <DocumentationIcon sx={{ fontSize: 18 }} />
                <Typography variant="body2">User Guide</Typography>
              </Link>
              <Link
                href="#"
                underline="hover"
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                  '&:hover': { color: brandColors.primary.signalTeal },
                }}
              >
                <ApiIcon sx={{ fontSize: 18 }} />
                <Typography variant="body2">API Reference</Typography>
              </Link>
              <Link
                href="#"
                underline="hover"
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  color: isDark ? brandColors.darkText.primary : brandColors.lightText.primary,
                  '&:hover': { color: brandColors.primary.signalTeal },
                }}
              >
                <ReleaseNotesIcon sx={{ fontSize: 18 }} />
                <Typography variant="body2">Release Notes</Typography>
              </Link>
            </Box>
          </Paper>

          {/* System Status */}
          <Paper
            sx={{
              p: 3,
              background: isDark
                ? 'linear-gradient(180deg, rgba(18, 28, 46, 0.8) 0%, rgba(26, 39, 64, 0.6) 100%)'
                : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(247, 249, 252, 0.8) 100%)',
              backdropFilter: 'blur(10px)',
              border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'}`,
              borderRadius: 3,
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography
                variant="h6"
                sx={{
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 600,
                }}
              >
                System Status
              </Typography>
              <Chip
                icon={allOperational ? <CheckCircleIcon sx={{ fontSize: 14 }} /> : <WarningIcon sx={{ fontSize: 14 }} />}
                label={allOperational ? 'All Systems Operational' : 'Partial Degradation'}
                size="small"
                sx={{
                  backgroundColor: allOperational
                    ? `${statusColors.success}20`
                    : `${brandColors.primary.alertAmber}20`,
                  color: allOperational
                    ? statusColors.success
                    : brandColors.primary.alertAmber,
                  '& .MuiChip-icon': {
                    color: allOperational
                      ? statusColors.success
                      : brandColors.primary.alertAmber,
                  },
                }}
              />
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {systemStatus.map((service) => (
                <Box
                  key={service.service}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    py: 1,
                    borderBottom: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)'}`,
                    '&:last-child': { borderBottom: 'none' },
                  }}
                >
                  <Typography variant="body2">{service.service}</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getStatusIcon(service.status)}
                    <Typography
                      variant="caption"
                      sx={{
                        color: getStatusColor(service.status, isDark),
                        fontWeight: 500,
                        textTransform: 'capitalize',
                      }}
                    >
                      {service.status}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Box>

            <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
              Last updated: {new Date(systemStatus[0].lastUpdated).toLocaleString()}
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SupportPage;
