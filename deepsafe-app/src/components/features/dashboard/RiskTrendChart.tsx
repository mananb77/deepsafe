import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart,
} from 'recharts';
import { useThemeMode } from '../../../context/ThemeContext';
import { brandColors } from '../../../theme/colors';
import type { RiskTrendDataPoint } from '../../../types';

interface RiskTrendChartProps {
  data: RiskTrendDataPoint[];
  height?: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ payload: RiskTrendDataPoint }>;
  label?: string;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  const { isDark } = useThemeMode();
  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <Paper
        sx={{
          p: 2,
          background: isDark
            ? brandColors.dark.elevated
            : brandColors.light.surface,
          border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'}`,
          borderRadius: 2,
          boxShadow: isDark
            ? '0 8px 32px rgba(0, 0, 0, 0.5)'
            : '0 4px 16px rgba(0, 0, 0, 0.1)',
        }}
      >
        <Typography variant="body2" fontWeight={600} sx={{ mb: 1 }}>
          {new Date(label || '').toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
          })}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Avg Risk:{' '}
          <Box
            component="span"
            sx={{
              fontWeight: 700,
              color: brandColors.primary.signalTeal,
              fontFamily: '"JetBrains Mono", monospace',
            }}
          >
            {data.averageRiskScore}%
          </Box>
        </Typography>
        {data.criticalAlerts > 0 && (
          <Typography variant="body2" sx={{ color: statusColors.error, mt: 0.5 }}>
            Critical Alerts: {data.criticalAlerts}
          </Typography>
        )}
        {data.highRiskCount > 0 && (
          <Typography variant="body2" sx={{ color: statusColors.warning, mt: 0.5 }}>
            High Risk Meetings: {data.highRiskCount}
          </Typography>
        )}
      </Paper>
    );
  }
  return null;
};

export const RiskTrendChart: React.FC<RiskTrendChartProps> = ({
  data,
  height = 300,
}) => {
  const { isDark } = useThemeMode();

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)';
  const axisColor = isDark ? brandColors.darkText.muted : brandColors.lightText.muted;

  return (
    <Box sx={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor={brandColors.primary.signalTeal}
                stopOpacity={isDark ? 0.4 : 0.3}
              />
              <stop
                offset="95%"
                stopColor={brandColors.primary.signalTeal}
                stopOpacity={0}
              />
            </linearGradient>
            <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor={brandColors.primary.signalTeal} />
              <stop offset="100%" stopColor={brandColors.primary.deepSafeBlue} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />

          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={{ fontSize: 12, fill: axisColor }}
            tickLine={false}
            axisLine={{ stroke: gridColor }}
          />

          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 12, fill: axisColor }}
            tickLine={false}
            axisLine={{ stroke: gridColor }}
            tickFormatter={(value) => `${value}%`}
          />

          <Tooltip content={<CustomTooltip />} />

          {/* Reference lines for risk thresholds */}
          <ReferenceLine
            y={60}
            stroke={isDark ? brandColors.statusDark.warning : brandColors.statusLight.warning}
            strokeDasharray="5 5"
            strokeWidth={1}
            strokeOpacity={0.6}
          />
          <ReferenceLine
            y={85}
            stroke={brandColors.primary.threatRed}
            strokeDasharray="5 5"
            strokeWidth={1}
            strokeOpacity={0.6}
          />

          {/* Area fill under the line */}
          <Area
            type="monotone"
            dataKey="averageRiskScore"
            stroke="none"
            fill="url(#riskGradient)"
          />

          {/* Main risk score line */}
          <Line
            type="monotone"
            dataKey="averageRiskScore"
            stroke="url(#lineGradient)"
            strokeWidth={3}
            dot={false}
            activeDot={{
              r: 8,
              fill: brandColors.primary.signalTeal,
              stroke: isDark ? brandColors.dark.surface : brandColors.light.surface,
              strokeWidth: 3,
              filter: `drop-shadow(0 0 6px ${brandColors.primary.signalTeal}80)`,
            }}
          />

          {/* Critical alerts as dots */}
          <Line
            type="monotone"
            dataKey="criticalAlerts"
            stroke="none"
            dot={(props: { cx?: number; cy?: number; payload?: RiskTrendDataPoint }) => {
              const { cx, cy, payload } = props;
              if (payload && payload.criticalAlerts > 0 && cx !== undefined && cy !== undefined) {
                return (
                  <g key={`critical-${payload.date}`}>
                    {/* Glow effect */}
                    <circle
                      cx={cx}
                      cy={cy}
                      r={12}
                      fill={brandColors.primary.threatRed}
                      opacity={0.3}
                    />
                    {/* Main dot */}
                    <circle
                      cx={cx}
                      cy={cy}
                      r={8}
                      fill={brandColors.primary.threatRed}
                      stroke={isDark ? brandColors.dark.surface : brandColors.light.surface}
                      strokeWidth={2}
                      filter={`drop-shadow(0 0 4px ${brandColors.primary.threatRed}80)`}
                    />
                  </g>
                );
              }
              return <g key={`empty-${payload?.date || Math.random()}`} />;
            }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default RiskTrendChart;
