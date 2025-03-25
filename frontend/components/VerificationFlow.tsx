import React, { useState } from 'react';
import FaceScanner from './FaceScanner';
import FingerprintScanner from './FingerprintScanner';
import { toast } from 'react-hot-toast';

interface VerificationResult {
  success: boolean;
  confidence: number;
  metadata: any;
  transaction_hash: string;
}

interface VerificationFlowProps {
  voterId: string;
  pollingStation: string;
  onComplete: (faceResult: VerificationResult, fingerprintResult: VerificationResult) => void;
}

enum VerificationStep {
  FACE = 'face',
  FINGERPRINT = 'fingerprint',
  COMPLETE = 'complete'
}

const VerificationFlow: React.FC<VerificationFlowProps> = ({
  voterId,
  pollingStation,
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState<VerificationStep>(VerificationStep.FACE);
  const [faceVerificationResult, setFaceVerificationResult] = useState<VerificationResult | null>(null);
  const [fingerprintVerificationResult, setFingerprintVerificationResult] = useState<VerificationResult | null>(null);

  const handleFaceVerificationComplete = (result: VerificationResult) => {
    setFaceVerificationResult(result);
    
    if (result.success) {
      toast.success('Face verification successful! Please continue to fingerprint verification.');
      setCurrentStep(VerificationStep.FINGERPRINT);
    } else {
      toast.error('Face verification failed. Please try again.');
      // Stay on face verification step
    }
  };

  const handleFingerprintVerificationComplete = (result: VerificationResult) => {
    setFingerprintVerificationResult(result);
    
    if (result.success) {
      toast.success('Fingerprint verification successful!');
      setCurrentStep(VerificationStep.COMPLETE);
      
      if (faceVerificationResult) {
        onComplete(faceVerificationResult, result);
      }
    } else {
      toast.error('Fingerprint verification failed. Please try again.');
      // Stay on fingerprint verification step
    }
  };

  const resetVerification = () => {
    setCurrentStep(VerificationStep.FACE);
    setFaceVerificationResult(null);
    setFingerprintVerificationResult(null);
  };

  return (
    <div className="flex flex-col items-center space-y-6 p-6">
      <h1 className="text-3xl font-bold text-gray-900">Voter Verification</h1>
      
      {/* Progress indicator */}
      <div className="w-full max-w-md flex items-center mb-4">
        <div className={`flex-1 h-2 rounded-l-full ${currentStep === VerificationStep.FACE || currentStep === VerificationStep.FINGERPRINT || currentStep === VerificationStep.COMPLETE ? 'bg-green-500' : 'bg-gray-300'}`}></div>
        <div className={`flex-1 h-2 ${currentStep === VerificationStep.FINGERPRINT || currentStep === VerificationStep.COMPLETE ? 'bg-green-500' : 'bg-gray-300'}`}></div>
        <div className={`flex-1 h-2 rounded-r-full ${currentStep === VerificationStep.COMPLETE ? 'bg-green-500' : 'bg-gray-300'}`}></div>
      </div>
      
      {/* Step indicators */}
      <div className="w-full max-w-md flex justify-between mb-8">
        <div className="text-center">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center mb-1 mx-auto ${currentStep === VerificationStep.FACE ? 'bg-blue-500 text-white' : faceVerificationResult?.success ? 'bg-green-500 text-white' : 'bg-gray-200'}`}>
            1
          </div>
          <span className="text-sm">Face</span>
        </div>
        <div className="text-center">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center mb-1 mx-auto ${currentStep === VerificationStep.FINGERPRINT ? 'bg-blue-500 text-white' : fingerprintVerificationResult?.success ? 'bg-green-500 text-white' : 'bg-gray-200'}`}>
            2
          </div>
          <span className="text-sm">Fingerprint</span>
        </div>
        <div className="text-center">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center mb-1 mx-auto ${currentStep === VerificationStep.COMPLETE ? 'bg-green-500 text-white' : 'bg-gray-200'}`}>
            3
          </div>
          <span className="text-sm">Complete</span>
        </div>
      </div>
      
      {/* Current step */}
      {currentStep === VerificationStep.FACE && (
        <FaceScanner 
          voterId={voterId}
          pollingStation={pollingStation}
          onVerificationComplete={handleFaceVerificationComplete}
        />
      )}
      
      {currentStep === VerificationStep.FINGERPRINT && (
        <FingerprintScanner
          voterId={voterId}
          pollingStation={pollingStation}
          onVerificationComplete={handleFingerprintVerificationComplete}
        />
      )}
      
      {currentStep === VerificationStep.COMPLETE && (
        <div className="flex flex-col items-center space-y-4 p-6 bg-white rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold text-green-600">Verification Complete!</h2>
          <p className="text-gray-700">Both face and fingerprint verification were successful.</p>
          
          <div className="mt-4">
            <button 
              onClick={resetVerification}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Verify Another Voter
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VerificationFlow; 