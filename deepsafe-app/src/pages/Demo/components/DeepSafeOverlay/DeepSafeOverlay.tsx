import React from 'react';
import { useDemoContext } from '../../context/DemoContext';
import { VerificationModal } from './VerificationModal';
import { ThreatConfirmedOverlay } from './ThreatConfirmedOverlay';

export const DeepSafeOverlay: React.FC = () => {
  const { state, currentStepConfig } = useDemoContext();

  // Only show overlay components during call screens (steps 3-7)
  const showOverlays =
    currentStepConfig.component === 'call' && state.currentStep >= 3;

  if (!showOverlays) return null;

  return (
    <>
      {/* Note: RiskMeter and AlertBanner are now in RightSidePanel */}

      {/* Verification Modal - Step 6 */}
      {state.verificationStep && !state.threatConfirmed && <VerificationModal />}

      {/* Threat Confirmed Overlay - Step 7 */}
      {state.threatConfirmed && <ThreatConfirmedOverlay />}
    </>
  );
};

export default DeepSafeOverlay;
