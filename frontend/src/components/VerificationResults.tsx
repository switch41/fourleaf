import React from 'react';
import { motion } from 'framer-motion';

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

interface VerificationResultsProps {
  result: VerificationResult;
  onClose: () => void;
}

const VerificationResults: React.FC<VerificationResultsProps> = ({
  result,
  onClose,
}) => {
  const formatPercentage = (value: number) => `${(value * 100).toFixed(2)}%`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">
          Verification Results
        </h2>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      {/* Status */}
      <div className={`mb-6 p-4 rounded-lg ${
        result.success ? 'bg-green-100' : 'bg-red-100'
      }`}>
        <div className="flex items-center">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
            result.success ? 'bg-green-500' : 'bg-red-500'
          }`}>
            {result.success ? (
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            ) : (
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            )}
          </div>
          <div className="ml-4">
            <h3 className={`text-lg font-semibold ${
              result.success ? 'text-green-800' : 'text-red-800'
            }`}>
              {result.success ? 'Verification Successful' : 'Verification Failed'}
            </h3>
            <p className={`text-sm ${
              result.success ? 'text-green-600' : 'text-red-600'
            }`}>
              Confidence Score: {formatPercentage(result.confidence)}
            </p>
          </div>
        </div>
      </div>

      {/* Details */}
      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-gray-600 mb-2">
            Verification Method
          </h4>
          <p className="text-gray-800 capitalize">
            {result.metadata.verification_method}
          </p>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-gray-600 mb-2">
            AI Similarity Score
          </h4>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-blue-600 h-2.5 rounded-full"
              style={{ width: formatPercentage(result.metadata.ai_similarity) }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-1">
            {formatPercentage(result.metadata.ai_similarity)}
          </p>
        </div>

        {result.metadata.minutiae_similarity !== undefined && (
          <div>
            <h4 className="text-sm font-semibold text-gray-600 mb-2">
              Minutiae Similarity Score
            </h4>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-purple-600 h-2.5 rounded-full"
                style={{
                  width: formatPercentage(result.metadata.minutiae_similarity),
                }}
              />
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {formatPercentage(result.metadata.minutiae_similarity)}
            </p>
          </div>
        )}

        <div>
          <h4 className="text-sm font-semibold text-gray-600 mb-2">
            Blockchain Transaction
          </h4>
          <p className="text-xs text-gray-500 break-all font-mono">
            {result.transaction_hash}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="mt-6 flex justify-end">
        <button
          onClick={onClose}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Close
        </button>
      </div>
    </motion.div>
  );
};

export default VerificationResults; 