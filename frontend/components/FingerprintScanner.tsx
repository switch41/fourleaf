import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
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
  const [isCameraActive, setIsCameraActive] = useState(false);
  const webcamRef = useRef<Webcam>(null);

  // Camera settings
  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: 'environment', // Use back camera if available
  };

  // Start scanning
  const startScanning = () => {
    setIsScanning(true);
    setIsCameraActive(true);
  };

  // Capture fingerprint
  const captureFingerprint = useCallback(async () => {
    try {
      if (!webcamRef.current) return;

      // Capture image
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) return;

      // Convert base64 to blob
      const base64Data = imageSrc.split(',')[1];
      const blob = await fetch(`data:image/jpeg;base64,${base64Data}`).then(res => res.blob());

      // Create form data
      const formData = new FormData();
      formData.append('fingerprint', blob, 'fingerprint.jpg');
      formData.append('voter_id', voterId);
      formData.append('polling_station', pollingStation);

      // Send to API
      const response = await axios.post<VerificationResult>(
        `${process.env.NEXT_PUBLIC_API_URL}/verify`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'X-API-Key': process.env.NEXT_PUBLIC_API_KEY,
          },
        }
      );

      // Handle response
      setIsScanning(false);
      setIsCameraActive(false);
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
  }, [voterId, pollingStation, onVerificationComplete]);

  return (
    <div className="flex flex-col items-center space-y-4 p-4 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-gray-800">Fingerprint Verification</h2>
      
      {/* Camera View */}
      {isCameraActive && (
        <div className="relative w-full max-w-lg">
          <Webcam
            ref={webcamRef}
            audio={false}
            screenshotFormat="image/jpeg"
            videoConstraints={videoConstraints}
            className="w-full rounded-lg"
          />
          <div className="absolute top-0 left-0 right-0 bottom-0 flex items-center justify-center">
            <div className="border-2 border-blue-500 rounded-lg w-64 h-64 flex items-center justify-center">
              <span className="text-blue-500">Place finger here</span>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex space-x-4">
        {!isScanning ? (
          <button
            onClick={startScanning}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Start Scanning
          </button>
        ) : (
          <button
            onClick={captureFingerprint}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            Capture Fingerprint
          </button>
        )}
        {isScanning && (
          <button
            onClick={() => {
              setIsScanning(false);
              setIsCameraActive(false);
            }}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Instructions */}
      <div className="text-sm text-gray-600 max-w-md text-center">
        <p>Please place your finger on the scanner and ensure it's clearly visible.</p>
        <p>Keep your finger steady while capturing the fingerprint.</p>
      </div>
    </div>
  );
};

export default FingerprintScanner; 