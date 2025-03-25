import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './VoterVerification.css';

const VoterVerification = () => {
  const [voterId, setVoterId] = useState('');
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showFingerprintScanner, setShowFingerprintScanner] = useState(false);
  const videoRef = useRef(null);
  const [verificationStatus, setVerificationStatus] = useState({
    voterIdVerified: false,
    faceVerified: false,
    fingerprintVerified: false
  });
  const [loading, setLoading] = useState(false);
  const [verificationStep, setVerificationStep] = useState('initial');
  const [scannerStatus, setScannerStatus] = useState(null);

  useEffect(() => {
    checkScannerStatus();
  }, []);

  useEffect(() => {
    // Cleanup camera when component unmounts
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach(track => track.stop());
      }
    };
  }, []);

  const checkScannerStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/scanner/status', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setScannerStatus(response.data);
    } catch (err) {
      console.error('Failed to check scanner status:', err);
      setScannerStatus({ connected: false });
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: 640,
          height: 480,
          facingMode: 'user'
        } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setShowModal(true);
      setError('');
    } catch (err) {
      setError('Failed to access camera. Please make sure camera permissions are granted.');
      console.error('Camera error:', err);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setShowModal(false);
  };

  const captureImage = async () => {
    if (!videoRef.current) return;

    try {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoRef.current, 0, 0);
      const imageData = canvas.toDataURL('image/jpeg', 0.8);
      
      stopCamera();
      return imageData;
    } catch (err) {
      setError('Failed to capture image');
      console.error('Capture error:', err);
      return null;
    }
  };

  const verifyVoterID = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/verify/voter-id',
        { voterId: voterId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        setVerificationStatus(prev => ({ ...prev, voterIdVerified: true }));
        setError('');
        return true;
      } else {
        setError('Invalid Voter ID');
        return false;
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to verify voter ID');
      return false;
    }
  };

  const handleFaceVerification = async () => {
    try {
      await startCamera();
    } catch (err) {
      setError('Failed to start camera');
    }
  };

  const handleFingerprintVerification = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/verify/fingerprint', {
        voterId: voterId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.status && !response.data.status.connected) {
        setError('Fingerprint scanner is not connected. Please check the connection and try again.');
        return;
      }
      
      if (response.data.message === 'Fingerprint verification successful') {
        setVerificationStep('completed');
        setVerificationStatus('success');
      } else {
        setError(response.data.message);
        setVerificationStatus('error');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Failed to verify fingerprint';
      const scannerStatus = err.response?.data?.status;
      
      if (scannerStatus && !scannerStatus.connected) {
        setError('Fingerprint scanner is not connected. Please check the connection and try again.');
      } else {
        setError(errorMessage);
      }
      setVerificationStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const handleVerification = async (type) => {
    try {
      if (!verificationStatus.voterIdVerified) {
        const verified = await verifyVoterID();
        if (!verified) return;
      }

      const token = localStorage.getItem('token');
      let verificationData;

      if (type === 'face') {
        const imageData = await captureImage();
        if (!imageData) return;
        verificationData = imageData;
      }

      const requestData = {
        voterId: voterId,
        [type === 'fingerprint' ? 'fingerprintData' : 'faceData']: verificationData
      };

      const response = await axios.post(`http://localhost:5000/verify/${type}`, 
        requestData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        setVerificationStatus(prev => ({
          ...prev,
          [type === 'fingerprint' ? 'fingerprintVerified' : 'faceVerified']: true
        }));
        setError('');
      } else {
        setError(`${type} verification failed`);
      }
    } catch (err) {
      setError(err.response?.data?.error || `Failed to verify ${type}`);
    }
  };

  const handleVote = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/vote',
        { voterId: voterId, party: 'DEMO_PARTY' },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        setStatus('Vote recorded successfully');
        setVerificationStatus({
          voterIdVerified: false,
          faceVerified: false,
          fingerprintVerified: false
        });
        setVoterId('');
      } else {
        setError('Failed to record vote');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to record vote');
    }
  };

  const allVerificationsComplete = 
    verificationStatus.voterIdVerified && 
    verificationStatus.faceVerified && 
    verificationStatus.fingerprintVerified;

  return (
    <div className="verification-container">
      <h1>Voter Verification System</h1>
      <div className="status-box">
        <h2>Scanner Status: {status}</h2>
        <div className="verification-status">
          <p>Voter ID Verified: {verificationStatus.voterIdVerified ? '✅' : '❌'}</p>
          <p>Face Verified: {verificationStatus.faceVerified ? '✅' : '❌'}</p>
          <p>Fingerprint Verified: {verificationStatus.fingerprintVerified ? '✅' : '❌'}</p>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">Face Verification</h2>
              <button className="close-button" onClick={stopCamera}>&times;</button>
            </div>
            <div className="camera-container">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="camera-feed"
                style={{ transform: 'scaleX(-1)' }}
              />
              <div className="capture-controls">
                <button onClick={() => handleVerification('face')} className="capture-button">
                  Capture and Verify
                </button>
                <button onClick={stopCamera} className="cancel-button">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showFingerprintScanner && (
        <div className="fingerprint-scanner">
          <div className="scanner-animation"></div>
          <p>Place your finger on the external scanner...</p>
        </div>
      )}

      <div className="verification-form">
        <input
          type="text"
          placeholder="Enter Voter ID (e.g., VOTER001)"
          value={voterId}
          onChange={(e) => setVoterId(e.target.value)}
        />
        <div className="verification-buttons">
          <button 
            onClick={handleFaceVerification}
            disabled={!voterId || showModal}
          >
            Verify Face
          </button>
          <button 
            onClick={handleFingerprintVerification}
            disabled={!voterId || showFingerprintScanner}
          >
            Verify Fingerprint
          </button>
          <button 
            onClick={handleVote}
            disabled={!allVerificationsComplete}
            className={allVerificationsComplete ? 'vote-button-enabled' : ''}
          >
            Vote
          </button>
        </div>
      </div>
      {error && <div className="error-message">{error}</div>}
      {status === 'Vote recorded successfully' && (
        <div className="success-message">Vote recorded successfully!</div>
      )}

      {scannerStatus && (
        <div className={`scanner-status ${scannerStatus.connected ? 'connected' : 'disconnected'}`}>
          Scanner Status: {scannerStatus.connected ? 'Connected' : 'Disconnected'}
          {scannerStatus.port && <span> (Port: {scannerStatus.port})</span>}
        </div>
      )}

      {loading && <div className="loading">Verifying fingerprint...</div>}
    </div>
  );
};

export default VoterVerification; 