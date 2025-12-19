import React from 'react';
import { useDemoContext } from '../../context/DemoContext';
import { DemoModal } from './DemoModal';
import { ExplainerModal } from './ExplainerModal';
import { RiskBreakdownModal } from './RiskBreakdownModal';
import { ForensicModal } from './ForensicModal';

export const ModalPortal: React.FC = () => {
  const { state } = useDemoContext();

  if (!state.activeModal) return null;

  // Render appropriate modal content based on type
  const renderModalContent = () => {
    switch (state.activeModal?.type) {
      case 'explainer':
        return <ExplainerModal title={state.activeModal.title} />;
      case 'riskBreakdown':
        return <RiskBreakdownModal />;
      case 'forensic':
        return <ForensicModal />;
      case 'timeline':
        // Timeline uses the incident report screen, show a simpler view
        return <ExplainerModal title="Incident Timeline" />;
      default:
        return <ExplainerModal title={state.activeModal?.title || 'Information'} />;
    }
  };

  return <DemoModal>{renderModalContent()}</DemoModal>;
};

export default ModalPortal;
