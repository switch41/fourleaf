import React, { useState } from 'react';
import { motion } from 'framer-motion';
import FingerprintScanner from './FingerprintScanner';
import VerificationResults from './VerificationResults';
import { Toaster } from 'react-hot-toast';
import FaceScanner from './FaceScanner';

interface VerificationResult {
  success: boolean;
  confidence: number;
  metadata: {
    ai_similarity: number;
    minutiae_similarity?: number;
    verification_method: string;
  };
  transaction_hash: string;
}

const Verify: React.FC = () => {
  const [voterId, setVoterId] = useState('');
  const [pollingStation, setPollingStation] = useState('');
  const [verificationMethod, setVerificationMethod] = useState<'face' | 'fingerprint' | null>(null);
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);

  const handleVerificationComplete = (result: VerificationResult) => {
    setVerificationResult(result);
  };

  const handleVerificationMethodSelect = (method: 'face' | 'fingerprint') => {
    setVerificationMethod(method);
    setVerificationResult(null);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8">Voter Verification</h1>

      {!voterId || !pollingStation ? (
        <div className="mt-8 max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Enter Voter Details</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Voter ID</label>
              <input
                type="text"
                value={voterId}
                onChange={(e) => setVoterId(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="Enter your Voter ID"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Polling Station</label>
              <input
                type="text"
                value={pollingStation}
                onChange={(e) => setPollingStation(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="Enter your Polling Station"
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="max-w-2xl mx-auto">
          {!verificationResult ? (
            <>
              {!verificationMethod ? (
                <div className="space-y-4">
                  <h2 className="text-xl font-semibold text-center mb-6">Select Verification Method</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button
                      onClick={() => handleVerificationMethodSelect('face')}
                      className="p-6 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow"
                    >
                      <h3 className="text-lg font-semibold mb-2">Face Verification</h3>
                      <p className="text-gray-600">Verify using facial recognition</p>
                    </button>
                    <button
                      onClick={() => handleVerificationMethodSelect('fingerprint')}
                      className="p-6 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow"
                    >
                      <h3 className="text-lg font-semibold mb-2">Fingerprint Verification</h3>
                      <p className="text-gray-600">Verify using fingerprint scanning</p>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="max-w-2xl mx-auto">
                  <div className="mb-4">
                    <button
                      onClick={() => setVerificationMethod(null)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      ← Change verification method
                    </button>
                  </div>

                  {verificationMethod === 'face' ? (
                    <FaceScanner
                      voterId={voterId}
                      pollingStation={pollingStation}
                      onVerificationComplete={handleVerificationComplete}
                    />
                  ) : (
                    <FingerprintScanner
                      voterId={voterId}
                      pollingStation={pollingStation}
                      onVerificationComplete={handleVerificationComplete}
                    />
                  )}
                </div>
              )}
            </>
          ) : (
            <VerificationResults
              result={verificationResult}
              onClose={() => {
                setVerificationResult(null);
                setVerificationMethod(null);
              }}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default Verify; 