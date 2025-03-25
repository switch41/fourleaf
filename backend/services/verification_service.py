from utils.dummy_dataset import DummyDatasetManager
from ai.preprocessing.fingerprint_processor import FingerprintProcessor
from ai.utils.verification import FingerprintVerifier
import numpy as np
import cv2
import logging
import uuid

logger = logging.getLogger(__name__)

class VerificationService:
    def __init__(self):
        self.dataset_manager = DummyDatasetManager()
        self.fp_processor = FingerprintProcessor()
        self.fp_verifier = FingerprintVerifier()
    
    def verify_fingerprint(self, fingerprint_image, voter_id, polling_station):
        """Verify a fingerprint against the dummy dataset
        
        Args:
            fingerprint_image: Numpy array containing the fingerprint image
            voter_id: Voter ID to verify against
            polling_station: Polling station ID
            
        Returns:
            Dictionary with verification result
        """
        try:
            # Convert image to grayscale if needed
            if len(fingerprint_image.shape) == 3:
                fingerprint_image = cv2.cvtColor(fingerprint_image, cv2.COLOR_BGR2GRAY)
            
            # Preprocess the fingerprint
            processed_fp = self.fp_processor.preprocess_image(fingerprint_image)
            
            # Get stored fingerprint
            stored_fp, metadata = self.dataset_manager.get_fingerprint(voter_id)
            
            if stored_fp is None:
                return {
                    "success": False,
                    "confidence": 0.0,
                    "metadata": {
                        "ai_similarity": 0.0,
                        "verification_method": "dummy_dataset",
                        "error": "Voter ID not found in dataset"
                    },
                    "transaction_hash": str(uuid.uuid4())
                }
            
            # Preprocess stored fingerprint
            processed_stored_fp = self.fp_processor.preprocess_image(stored_fp)
            
            # Compare fingerprints
            ai_similarity = self.fp_verifier.verify(processed_fp, processed_stored_fp)
            
            # Determine if verification was successful
            success = ai_similarity >= 0.85  # Threshold can be adjusted
            
            return {
                "success": success,
                "confidence": float(ai_similarity),
                "metadata": {
                    "ai_similarity": float(ai_similarity),
                    "verification_method": "dummy_dataset",
                    "polling_station": polling_station
                },
                "transaction_hash": str(uuid.uuid4())
            }
            
        except Exception as e:
            logger.error(f"Error during fingerprint verification: {str(e)}")
            return {
                "success": False,
                "confidence": 0.0,
                "metadata": {
                    "verification_method": "dummy_dataset",
                    "error": str(e)
                },
                "transaction_hash": str(uuid.uuid4())
            }
    
    def register_fingerprint(self, fingerprint_image, voter_id, metadata=None):
        """Register a fingerprint in the dummy dataset
        
        Args:
            fingerprint_image: Numpy array containing the fingerprint image
            voter_id: Voter ID to register
            metadata: Additional metadata
            
        Returns:
            True if registered successfully
        """
        if metadata is None:
            metadata = {}
            
        try:
            # Convert image to grayscale if needed
            if len(fingerprint_image.shape) == 3:
                fingerprint_image = cv2.cvtColor(fingerprint_image, cv2.COLOR_BGR2GRAY)
                
            # Save to dataset
            self.dataset_manager.add_fingerprint(voter_id, fingerprint_image, metadata)
            return True
        except Exception as e:
            logger.error(f"Error registering fingerprint: {str(e)}")
            return False 