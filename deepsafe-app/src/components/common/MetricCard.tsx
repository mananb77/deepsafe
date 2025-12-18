import React from 'react';
import { Card, CardContent, Typography, Box, Skeleton, useTheme } from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../../context/ThemeContext';
import { brandColors } from '../../theme/colors';

interface MetricCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'flat';
    label?: string;
    isPositive?: boolean;
  };
  icon?: React.ReactNode;
  isLoading?: boolean;
  onClick?: () => void;
  isAlert?: boolean;
  formatValue?: (val: number | string) => string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  icon,
  isLoading = false,
  onClick,
  isAlert = false,
  formatValue,
}) => {
  const theme = useTheme();
  const { isDark } = useThemeMode();
  const displayValue = formatValue ? formatValue(value) : value;

  const statusColors = isDark ? brandColors.statusDark : brandColors.statusLight;

  const getTrendColor = () => {
    if (!trend) return 'text.secondary';
    if (trend.direction === 'flat') return 'text.secondary';
    if (trend.isPositive !== undefined) {
      return trend.isPositive ? statusColors.success : statusColors.error;
    }
    return trend.direction === 'up' ? statusColors.success : statusColors.error;
  };

  const TrendIcon =
    trend?.direction === 'up'
      ? TrendingUpIcon
      : trend?.direction === 'down'
        ? TrendingDownIcon
        : TrendingFlatIcon;

  return (
    <Card
      onClick={onClick}
      sx={{
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
        background: isDark
          ? isAlert
            ? 'linear-gradient(180deg, rgba(58, 43, 16, 0.3) 0%, rgba(26, 39, 64, 0.9) 100%)'
            : theme.gradients.deepOcean
          : isAlert
            ? 'linear-gradient(180deg, rgba(245, 166, 35, 0.08) 0%, #FFFFFF 100%)'
            : theme.gradients.blueGlass,
        border: isAlert
          ? `1px solid ${isDark ? 'rgba(255, 200, 87, 0.3)' : 'rgba(245, 166, 35, 0.4)'}`
          : `1px solid ${theme.customColors.borderColor}`,
        backdropFilter: 'blur(10px)',
        '&:hover': onClick
          ? {
              boxShadow: isDark
                ? '0 8px 32px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(31, 60, 136, 0.2)'
                : '0 8px 32px rgba(0, 0, 0, 0.1)',
              transform: 'translateY(-4px)',
              border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.1)'}`,
            }
          : {},
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
          <Typography
            variant="body2"
            sx={{
              color: 'text.secondary',
              fontWeight: 500,
              fontSize: '0.8125rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            {title}
          </Typography>
          {icon && (
            <Box
              sx={{
                color: brandColors.primary.signalTeal,
                opacity: 0.8,
              }}
            >
              {icon}
            </Box>
          )}
        </Box>

        {isLoading ? (
          <>
            <Skeleton
              variant="text"
              width="60%"
              height={48}
              sx={{
                bgcolor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
              }}
            />
            <Skeleton
              variant="text"
              width="40%"
              sx={{
                bgcolor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
              }}
            />
          </>
        ) : (
          <>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {isAlert && (
                <WarningIcon
                  sx={{
                    color: statusColors.warning,
                    fontSize: 28,
                  }}
                />
              )}
              <Typography
                variant="h3"
                sx={{
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 700,
                  background: isAlert
                    ? `linear-gradient(90deg, ${statusColors.warning} 0%, ${brandColors.primary.alertAmber} 100%)`
                    : `linear-gradient(90deg, ${brandColors.primary.signalTeal} 0%, ${brandColors.primary.deepSafeBlue} 100%)`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  fontSize: '2.25rem',
                  lineHeight: 1.2,
                }}
              >
                {displayValue}
              </Typography>
            </Box>

            {subtitle && (
              <Typography
                variant="body2"
                sx={{ color: 'text.secondary', mt: 0.5 }}
              >
                {subtitle}
              </Typography>
            )}

            {trend && (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                  mt: 1.5,
                  p: 0.75,
                  borderRadius: 1,
                  background: isDark
                    ? 'rgba(255, 255, 255, 0.03)'
                    : 'rgba(0, 0, 0, 0.02)',
                  width: 'fit-content',
                }}
              >
                <TrendIcon
                  sx={{
                    fontSize: 18,
                    color: getTrendColor(),
                  }}
                />
                <Typography
                  variant="caption"
                  sx={{
                    color: getTrendColor(),
                    fontWeight: 600,
                  }}
                >
                  {trend.value > 0 ? '+' : ''}
                  {trend.value}
                  {trend.label && ` ${trend.label}`}
                </Typography>
              </Box>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default MetricCard;
