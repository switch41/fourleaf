import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import { toast } from 'react-hot-toast';

interface VerificationResult {
  success: boolean;
  confidence: number;
  metadata: {
    ai_similarity: number;
    verification_method: string;
  };
  transaction_hash: string;
}

interface FaceScannerProps {
  voterId: string;
  pollingStation: string;
  onVerificationComplete: (result: VerificationResult) => void;
}

const FaceScanner: React.FC<FaceScannerProps> = ({
  voterId,
  pollingStation,
  onVerificationComplete,
}) => {
  const [isScanning, setIsScanning] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [faceDetected, setFaceDetected] = useState(false);
  const webcamRef = useRef<Webcam>(null);

  // Camera settings
  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: "user", // Use front camera for face
  };

  // Start scanning
  const startScanning = () => {
    setIsScanning(true);
    setIsCameraActive(true);
  };

  // Capture face
  const captureFace = useCallback(async () => {
    try {
      if (!webcamRef.current) return;

      // Capture image
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) return;

      // Convert base64 to blob
      const base64Data = imageSrc.split(',')[1];
      
      // Create form data
      const formData = new FormData();
      formData.append('face_base64', base64Data);
      formData.append('voter_id', voterId);
      formData.append('polling_station', pollingStation);

      // Send to API
      const response = await axios.post<VerificationResult>(
        `${process.env.NEXT_PUBLIC_API_URL}/api/verification/verify-face`,
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
        toast.success('Face verification successful!');
      } else {
        toast.error('Face verification failed. Please try again.');
      }

    } catch (error) {
      console.error('Error during face verification:', error);
      toast.error('Error during face verification. Please try again.');
      setIsScanning(false);
    }
  }, [voterId, pollingStation, onVerificationComplete]);

  // Simulate face detection (replace with actual face detection logic)
  React.useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isCameraActive) {
      interval = setInterval(() => {
        // Simulate face detection - in production use a real face detection library
        setFaceDetected(Math.random() > 0.5);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isCameraActive]);

  return (
    <div className="flex flex-col items-center space-y-4 p-4 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-gray-800">Face Verification</h2>
      
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
            <div className={`border-2 rounded-lg w-64 h-64 flex items-center justify-center ${
              faceDetected ? 'border-green-500' : 'border-blue-500'
            }`}>
              <span className={`${
                faceDetected ? 'text-green-500' : 'text-blue-500'
              }`}>
                {faceDetected ? 'Face Detected' : 'Position your face here'}
              </span>
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
            Start Face Scan
          </button>
        ) : (
          <button
            onClick={captureFace}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            disabled={!faceDetected}
          >
            Capture Face
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
        <p>Please look directly at the camera with good lighting.</p>
        <p>Keep your face centered in the frame.</p>
      </div>
    </div>
  );
};

export default FaceScanner; 