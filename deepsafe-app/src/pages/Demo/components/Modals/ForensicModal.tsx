import React, { useState } from 'react';
import { Box, Typography, Tabs, Tab, Stack, Chip } from '@mui/material';
import {
  Videocam as VideocamIcon,
  RecordVoiceOver as AudioIcon,
  Wifi as NetworkIcon,
  Psychology as BehavioralIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../../../context/ThemeContext';
import { brandColors } from '../../../../theme/colors';
import { demoForensicData, getSeverityColor } from '../../data/forensicData';

interface TabPanelProps {
  children: React.ReactNode;
  value: number;
  index: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <Box
    role="tabpanel"
    hidden={value !== index}
    sx={{ pt: 2 }}
  >
    {value === index && children}
  </Box>
);

interface EvidenceItemProps {
  label: string;
  value: string | number;
  severity?: 'critical' | 'high' | 'medium' | 'low';
}

const EvidenceItem: React.FC<EvidenceItemProps> = ({ label, value, severity }) => {
  const { isDark } = useThemeMode();

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        py: 1,
        borderBottom: `1px solid ${
          isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'
        }`,
      }}
    >
      <Typography
        variant="body2"
        sx={{
          color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)',
        }}
      >
        {label}
      </Typography>
      <Typography
        variant="body2"
        sx={{
          fontWeight: 600,
          fontFamily: typeof value === 'number' ? '"JetBrains Mono", monospace' : 'inherit',
          color: severity ? getSeverityColor(severity) : (isDark ? '#fff' : '#333'),
        }}
      >
        {typeof value === 'number' ? `${value}%` : value}
      </Typography>
    </Box>
  );
};

export const ForensicModal: React.FC = () => {
  const { isDark } = useThemeMode();
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box>
      {/* Tabs */}
      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        variant="fullWidth"
        sx={{
          minHeight: 42,
          '& .MuiTabs-indicator': {
            backgroundColor: brandColors.primary.signalTeal,
          },
        }}
      >
        <Tab
          icon={<VideocamIcon sx={{ fontSize: 18 }} />}
          iconPosition="start"
          label="Video"
          sx={{
            minHeight: 42,
            fontSize: '0.8rem',
            textTransform: 'none',
            color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)',
            '&.Mui-selected': {
              color: brandColors.primary.signalTeal,
            },
          }}
        />
        <Tab
          icon={<AudioIcon sx={{ fontSize: 18 }} />}
          iconPosition="start"
          label="Audio"
          sx={{
            minHeight: 42,
            fontSize: '0.8rem',
            textTransform: 'none',
            color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)',
            '&.Mui-selected': {
              color: brandColors.primary.signalTeal,
            },
          }}
        />
        <Tab
          icon={<NetworkIcon sx={{ fontSize: 18 }} />}
          iconPosition="start"
          label="Network"
          sx={{
            minHeight: 42,
            fontSize: '0.8rem',
            textTransform: 'none',
            color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)',
            '&.Mui-selected': {
              color: brandColors.primary.signalTeal,
            },
          }}
        />
        <Tab
          icon={<BehavioralIcon sx={{ fontSize: 18 }} />}
          iconPosition="start"
          label="Behavioral"
          sx={{
            minHeight: 42,
            fontSize: '0.8rem',
            textTransform: 'none',
            color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)',
            '&.Mui-selected': {
              color: brandColors.primary.signalTeal,
            },
          }}
        />
      </Tabs>

      {/* Video Tab */}
      <TabPanel value={activeTab} index={0}>
        <Box
          sx={{
            p: 2,
            borderRadius: '12px',
            backgroundColor: 'rgba(214, 69, 69, 0.1)',
            border: `1px solid ${brandColors.statusDark.error}30`,
            mb: 2,
          }}
        >
          <Typography
            variant="caption"
            sx={{ color: isDark ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)' }}
          >
            Deepfake Confidence
          </Typography>
          <Typography
            variant="h4"
            sx={{ fontWeight: 700, color: brandColors.statusDark.error }}
          >
            {demoForensicData.videoAnalysis.deepfakeConfidence}%
          </Typography>
        </Box>
        <Stack spacing={0}>
          <EvidenceItem
            label="Facial Landmark Inconsistencies"
            value={demoForensicData.videoAnalysis.facialLandmarkInconsistencies}
            severity="critical"
          />
          <EvidenceItem
            label="Micro-Expression Anomalies"
            value={demoForensicData.videoAnalysis.microExpressionAnomalies ? 'Detected' : 'None'}
            severity="high"
          />
          <EvidenceItem
            label="Lighting Inconsistencies"
            value={demoForensicData.videoAnalysis.lightingInconsistencies}
            severity="medium"
          />
          <EvidenceItem
            label="Edge Artifacts"
            value={demoForensicData.videoAnalysis.edgeArtifacts ? 'Detected' : 'None'}
            severity="high"
          />
        </Stack>
      </TabPanel>

      {/* Audio Tab */}
      <TabPanel value={activeTab} index={1}>
        <Box
          sx={{
            p: 2,
            borderRadius: '12px',
            backgroundColor: 'rgba(245, 166, 35, 0.1)',
            border: `1px solid ${brandColors.statusDark.warning}30`,
            mb: 2,
          }}
        >
          <Typography
            variant="caption"
            sx={{ color: isDark ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)' }}
          >
            Voice Cloning Confidence
          </Typography>
          <Typography
            variant="h4"
            sx={{ fontWeight: 700, color: brandColors.statusDark.warning }}
          >
            {demoForensicData.audioAnalysis.voiceCloningConfidence}%
          </Typography>
        </Box>
        <Stack spacing={0}>
          <EvidenceItem
            label="Audio/Video Desync"
            value={`${demoForensicData.audioAnalysis.audioVideoDesync}ms`}
          />
          <EvidenceItem
            label="Spectral Anomalies"
            value={demoForensicData.audioAnalysis.spectralAnomalies ? 'Detected' : 'None'}
            severity="medium"
          />
          <EvidenceItem
            label="Prosody Anomalies"
            value={demoForensicData.audioAnalysis.prosodyAnomalies ? 'Detected' : 'None'}
            severity="medium"
          />
          <EvidenceItem
            label="Voice Fingerprint Match"
            value={demoForensicData.audioAnalysis.voiceFingerprintMatch ? 'Matched' : 'No Match'}
          />
        </Stack>
      </TabPanel>

      {/* Network Tab */}
      <TabPanel value={activeTab} index={2}>
        <Box
          sx={{
            p: 2,
            borderRadius: '12px',
            backgroundColor: 'rgba(245, 166, 35, 0.1)',
            border: `1px solid ${brandColors.statusDark.warning}30`,
            mb: 2,
          }}
        >
          <Stack direction="row" spacing={1}>
            <Chip
              label="VPN Detected"
              size="small"
              sx={{
                backgroundColor: brandColors.statusDark.error,
                color: '#fff',
                fontWeight: 600,
              }}
            />
            <Chip
              label="Virtual Camera"
              size="small"
              sx={{
                backgroundColor: brandColors.statusDark.warning,
                color: '#fff',
                fontWeight: 600,
              }}
            />
          </Stack>
        </Box>
        <Stack spacing={0}>
          <EvidenceItem label="VPN Provider" value={demoForensicData.networkAnalysis.vpnProvider || 'N/A'} />
          <EvidenceItem label="Location" value={demoForensicData.networkAnalysis.location} />
          <EvidenceItem label="Device OS" value={demoForensicData.networkAnalysis.deviceOS} />
          <EvidenceItem label="Virtual Camera" value={demoForensicData.networkAnalysis.virtualCameraName || 'N/A'} />
          <EvidenceItem label="Known Device" value={demoForensicData.networkAnalysis.isKnownDevice ? 'Yes' : 'No'} />
        </Stack>
      </TabPanel>

      {/* Behavioral Tab */}
      <TabPanel value={activeTab} index={3}>
        <Box
          sx={{
            p: 2,
            borderRadius: '12px',
            backgroundColor: 'rgba(214, 69, 69, 0.1)',
            border: `1px solid ${brandColors.statusDark.error}30`,
            mb: 2,
          }}
        >
          <Typography
            variant="caption"
            sx={{ color: isDark ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)' }}
          >
            Social Engineering Score
          </Typography>
          <Typography
            variant="h4"
            sx={{ fontWeight: 700, color: brandColors.statusDark.error }}
          >
            {demoForensicData.behavioralAnalysis.socialEngineeringScore}%
          </Typography>
        </Box>
        <Stack spacing={0}>
          <EvidenceItem
            label="Authority Bypass"
            value={demoForensicData.behavioralAnalysis.authorityBypass}
            severity="critical"
          />
          <EvidenceItem
            label="Urgency Tactics"
            value={demoForensicData.behavioralAnalysis.urgencyTactics}
            severity="high"
          />
          <EvidenceItem
            label="Isolation Tactics"
            value={demoForensicData.behavioralAnalysis.isolationTactics}
            severity="high"
          />
          <EvidenceItem
            label="Known Pattern Match"
            value={demoForensicData.behavioralAnalysis.knownAttackPatternSimilarity}
            severity="critical"
          />
        </Stack>
      </TabPanel>
    </Box>
  );
};

export default ForensicModal;
