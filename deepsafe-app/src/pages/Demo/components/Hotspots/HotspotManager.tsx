import React, { useEffect, useState, useCallback } from 'react';
import { Box } from '@mui/material';
import { useDemoContext } from '../../context/DemoContext';
import { Hotspot } from './Hotspot';
import type { HotspotConfig } from '../../types/demo.types';

interface HotspotPosition {
  config: HotspotConfig;
  position: { top: number; left: number } | null;
  placedOnLeft: boolean;
}

const HOTSPOT_SIZE = 28;
const HOTSPOT_MARGIN = 8;
const SCREEN_EDGE_BUFFER = 60; // Extra buffer to account for panel/UI elements

export const HotspotManager: React.FC = () => {
  const { activeHotspots, currentStepConfig } = useDemoContext();
  const [positions, setPositions] = useState<HotspotPosition[]>([]);

  // Calculate positions for hotspots based on their anchor elements
  const calculatePositions = useCallback(() => {
    const screenWidth = window.innerWidth;

    const newPositions: HotspotPosition[] = activeHotspots.map((config) => {
      const anchorElement = document.querySelector(config.anchor);

      if (!anchorElement) {
        return { config, position: null, placedOnLeft: false };
      }

      const rect = anchorElement.getBoundingClientRect();
      const offsetX = config.offsetX || 0;
      const offsetY = config.offsetY || 0;

      // Determine position based on config or auto-detect
      let placeOnLeft = false;

      if (config.position === 'left') {
        placeOnLeft = true;
      } else if (config.position === 'right') {
        placeOnLeft = false;
      } else {
        // Auto: check if placing on right would go off screen
        const rightPosition = rect.right + HOTSPOT_MARGIN + HOTSPOT_SIZE;
        if (rightPosition > screenWidth - SCREEN_EDGE_BUFFER) {
          placeOnLeft = true;
        }
      }

      const left = placeOnLeft
        ? rect.left - HOTSPOT_SIZE - HOTSPOT_MARGIN + offsetX
        : rect.right + HOTSPOT_MARGIN + offsetX;

      return {
        config,
        position: {
          top: rect.top + offsetY,
          left: Math.max(HOTSPOT_MARGIN, Math.min(left, screenWidth - HOTSPOT_SIZE - HOTSPOT_MARGIN)),
        },
        placedOnLeft: placeOnLeft,
      };
    });

    setPositions(newPositions);
  }, [activeHotspots]);

  // Recalculate positions on mount, step change, and window resize
  useEffect(() => {
    // Small delay to allow DOM to update
    const timer = setTimeout(calculatePositions, 100);

    window.addEventListener('resize', calculatePositions);
    window.addEventListener('scroll', calculatePositions, true);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', calculatePositions);
      window.removeEventListener('scroll', calculatePositions, true);
    };
  }, [calculatePositions, currentStepConfig]);

  // Don't render if no hotspots on current step
  if (activeHotspots.length === 0) return null;

  return (
    <>
      {positions.map(({ config, position, placedOnLeft }) =>
        position ? (
          <Box
            key={config.id}
            sx={{
              position: 'fixed',
              top: position.top,
              left: position.left,
              zIndex: 50,
              pointerEvents: 'auto',
            }}
          >
            <Hotspot config={config} tooltipPosition={placedOnLeft ? 'left' : 'right'} />
          </Box>
        ) : null
      )}
    </>
  );
};

export default HotspotManager;
