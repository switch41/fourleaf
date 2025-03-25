import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

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

interface FingerprintScannerProps {
  voterId: string;
  pollingStation: string;
  onVerificationComplete: (result: VerificationResult) => void;
}

const FingerprintScanner: React.FC<FingerprintScannerProps> = ({
  voterId,
  pollingStation,
  onVerificationComplete,
}) => {
  const [isScanning, setIsScanning] = useState(false);
  const [scannerStatus, setScannerStatus] = useState<'idle' | 'connected' | 'disconnected'>('idle');

  // Check scanner connection status
  useEffect(() => {
    const checkScannerStatus = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/scanner/status`);
        setScannerStatus(response.data.connected ? 'connected' : 'disconnected');
      } catch (error) {
        console.error('Error checking scanner status:', error);
        setScannerStatus('disconnected');
      }
    };

    checkScannerStatus();
    const interval = setInterval(checkScannerStatus, 5000); // Check every 5 seconds

    return () => clearInterval(interval);
  }, []);

  // Start scanning
  const startScanning = async () => {
    if (scannerStatus !== 'connected') {
      toast.error('Fingerprint scanner is not connected. Please check the connection.');
      return;
    }

    try {
      setIsScanning(true);
      
      // Initialize scanner
      await axios.post(`${process.env.REACT_APP_API_URL}/scanner/init`);
      
      // Start listening for fingerprint capture
      const response = await axios.post<VerificationResult>(
        `${process.env.REACT_APP_API_URL}/verify`,
        {
          voter_id: voterId,
          polling_station: pollingStation,
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': process.env.REACT_APP_API_KEY,
          },
        }
      );

      // Handle response
      setIsScanning(false);
      onVerificationComplete(response.data);

      // Show success/failure message
      if (response.data.success) {
        toast.success('Verification successful!');
      } else {
        toast.error('Verification failed. Please try again.');
      }

    } catch (error) {
      console.error('Error during verification:', error);
      toast.error('Error during verification. Please try again.');
      setIsScanning(false);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-4 p-4 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-gray-800">Fingerprint Verification</h2>
      
      {/* Scanner Status */}
      <div className={`px-4 py-2 rounded-lg ${
        scannerStatus === 'connected' 
          ? 'bg-green-100 text-green-800' 
          : 'bg-red-100 text-red-800'
      }`}>
        {scannerStatus === 'connected' 
          ? 'Fingerprint Scanner Connected' 
          : 'Fingerprint Scanner Disconnected'}
      </div>

      {/* Scanner Preview */}
      <div className="relative w-full max-w-lg h-64 bg-gray-100 rounded-lg overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          {scannerStatus === 'connected' ? (
            <div className="text-center">
              <div className="text-6xl mb-4">👆</div>
              <p className="text-gray-600">Place your finger on the scanner</p>
            </div>
          ) : (
            <div className="text-center text-red-600">
              <div className="text-6xl mb-4">⚠️</div>
              <p>Scanner not connected</p>
            </div>
          )}
        </div>
      </div>

      {/* Controls */}
      <div className="flex space-x-4">
        <button
          onClick={startScanning}
          disabled={scannerStatus !== 'connected' || isScanning}
          className={`px-6 py-2 rounded-lg transition-colors ${
            scannerStatus === 'connected' && !isScanning
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-400 text-white cursor-not-allowed'
          }`}
        >
          {isScanning ? 'Scanning...' : 'Start Scanning'}
        </button>
        {isScanning && (
          <button
            onClick={() => setIsScanning(false)}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Instructions */}
      <div className="text-sm text-gray-600 max-w-md text-center">
        <p>Please ensure your finger is clean and dry before scanning.</p>
        <p>Place your finger firmly on the scanner and keep it steady.</p>
        <p>Wait for the green light before removing your finger.</p>
      </div>
    </div>
  );
};

export default FingerprintScanner; 