"""
Utility module for fingerprint verification combining preprocessing and AI model.
"""

import numpy as np
from typing import Tuple, Optional, Dict
from loguru import logger
import hashlib
from datetime import datetime

from ..preprocessing.fingerprint_processor import FingerprintProcessor
from ..models.fingerprint_model import FingerprintModel

class FingerprintVerifier:
    def __init__(self,
                 similarity_threshold: float = 0.85,
                 use_minutiae: bool = True):
        """
        Initialize the fingerprint verifier.
        
        Args:
            similarity_threshold: Threshold for considering fingerprints as matching
            use_minutiae: Whether to use minutiae-based verification in addition to AI
        """
        self.similarity_threshold = similarity_threshold
        self.use_minutiae = use_minutiae
        
        # Initialize components
        self.processor = FingerprintProcessor()
        self.model = FingerprintModel()
        
    def verify_fingerprint(self,
                          input_image: np.ndarray,
                          stored_features: np.ndarray,
                          stored_minutiae: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> Tuple[bool, float, Dict]:
        """
        Verify a fingerprint against stored features.
        
        Args:
            input_image: Input fingerprint image
            stored_features: Stored feature vector
            stored_minutiae: Optional stored minutiae points and types
            
        Returns:
            Tuple of (verification result, confidence score, metadata)
        """
        try:
            # Preprocess input image
            processed_image = self.processor.preprocess_image(input_image)
            
            # Extract AI features
            input_features = self.model.extract_features(processed_image)
            
            # Compute AI-based similarity
            ai_similarity = self.model.compute_similarity(input_features, stored_features)
            
            # Initialize verification result
            verification_result = False
            confidence_score = 0.0
            metadata = {
                'timestamp': datetime.utcnow().isoformat(),
                'ai_similarity': float(ai_similarity),
                'verification_method': 'ai_only'
            }
            
            if self.use_minutiae and stored_minutiae is not None:
                # Extract minutiae from input image
                input_minutiae, input_types = self.processor.extract_minutiae(processed_image)
                
                # Compute minutiae-based similarity
                minutiae_similarity = self._compute_minutiae_similarity(
                    input_minutiae, input_types,
                    stored_minutiae[0], stored_minutiae[1]
                )
                
                # Combine similarities (weighted average)
                confidence_score = 0.7 * ai_similarity + 0.3 * minutiae_similarity
                metadata['minutiae_similarity'] = float(minutiae_similarity)
                metadata['verification_method'] = 'hybrid'
            else:
                confidence_score = ai_similarity
            
            # Determine verification result
            verification_result = confidence_score >= self.similarity_threshold
            
            metadata['confidence_score'] = float(confidence_score)
            metadata['verification_result'] = verification_result
            
            return verification_result, confidence_score, metadata
            
        except Exception as e:
            logger.error(f"Error in fingerprint verification: {str(e)}")
            raise
            
    def _compute_minutiae_similarity(self,
                                   minutiae1: np.ndarray,
                                   types1: np.ndarray,
                                   minutiae2: np.ndarray,
                                   types2: np.ndarray) -> float:
        """
        Compute similarity between two sets of minutiae points.
        
        Args:
            minutiae1: First set of minutiae points
            types1: Types of first set of minutiae
            minutiae2: Second set of minutiae points
            types2: Types of second set of minutiae
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Normalize coordinates
            minutiae1_norm = minutiae1 / self.processor.image_size
            minutiae2_norm = minutiae2 / self.processor.image_size
            
            # Compute pairwise distances
            distances = np.zeros((len(minutiae1), len(minutiae2)))
            for i, m1 in enumerate(minutiae1_norm):
                for j, m2 in enumerate(minutiae2_norm):
                    distances[i, j] = np.linalg.norm(m1 - m2)
            
            # Find matching pairs
            matches = []
            used1 = set()
            used2 = set()
            
            while True:
                # Find closest unmatched pair
                min_dist = float('inf')
                min_i, min_j = -1, -1
                
                for i in range(len(minutiae1)):
                    if i in used1:
                        continue
                    for j in range(len(minutiae2)):
                        if j in used2:
                            continue
                        if distances[i, j] < min_dist:
                            min_dist = distances[i, j]
                            min_i, min_j = i, j
                
                if min_i == -1 or min_j == -1:
                    break
                    
                # Check if types match
                if types1[min_i] == types2[min_j]:
                    matches.append(min_dist)
                    used1.add(min_i)
                    used2.add(min_j)
                else:
                    break
            
            # Compute similarity score
            if not matches:
                return 0.0
                
            # Convert distances to similarities (closer = more similar)
            similarities = 1 - np.array(matches)
            return float(np.mean(similarities))
            
        except Exception as e:
            logger.error(f"Error computing minutiae similarity: {str(e)}")
            raise
            
    def create_verification_hash(self,
                               features: np.ndarray,
                               minutiae: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> str:
        """
        Create a secure hash of the verification data.
        
        Args:
            features: Feature vector
            minutiae: Optional minutiae data
            
        Returns:
            SHA-256 hash of the verification data
        """
        try:
            # Convert features to bytes
            feature_bytes = features.tobytes()
            
            # Add minutiae data if available
            if minutiae is not None:
                minutiae_bytes = np.concatenate([minutiae[0].flatten(), minutiae[1]]).tobytes()
                data = feature_bytes + minutiae_bytes
            else:
                data = feature_bytes
            
            # Compute SHA-256 hash
            return hashlib.sha256(data).hexdigest()
            
        except Exception as e:
            logger.error(f"Error creating verification hash: {str(e)}")
            raise 