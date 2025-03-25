import React from 'react';
import VerificationFlow from '../components/VerificationFlow';
import { useParams } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

const VoterVerification: React.FC = () => {
  const { voterId } = useParams<{ voterId: string }>();
  const pollingStation = "PS-001"; // This could come from user context or URL params
  
  const handleVerificationComplete = (faceResult, fingerprintResult) => {
    console.log('Verification completed:', { faceResult, fingerprintResult });
    // Here you would typically record the vote, update voter status, etc.
  };
  
  return (
    <div className="min-h-screen bg-gray-100 py-12">
      <Toaster position="top-right" />
      <div className="container mx-auto">
        <VerificationFlow 
          voterId={voterId || ""}
          pollingStation={pollingStation}
          onComplete={handleVerificationComplete}
        />
      </div>
    </div>
  );
};

export default VoterVerification; 