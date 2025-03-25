"""
Fingerprint preprocessing module for the voter verification system.
Handles image enhancement, normalization, and feature extraction.
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from loguru import logger

class FingerprintProcessor:
    def __init__(self, 
                 image_size: Tuple[int, int] = (224, 224),
                 gaussian_kernel_size: Tuple[int, int] = (5, 5),
                 threshold_block_size: int = 11,
                 threshold_c: int = 2):
        """
        Initialize the fingerprint processor with configuration parameters.
        
        Args:
            image_size: Target size for processed images (height, width)
            gaussian_kernel_size: Kernel size for Gaussian blur
            threshold_block_size: Block size for adaptive thresholding
            threshold_c: Constant subtracted from mean for thresholding
        """
        self.image_size = image_size
        self.gaussian_kernel_size = gaussian_kernel_size
        self.threshold_block_size = threshold_block_size
        self.threshold_c = threshold_c
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the fingerprint image through multiple stages.
        
        Args:
            image: Input fingerprint image (grayscale)
            
        Returns:
            Processed image ready for feature extraction
        """
        try:
            # Resize image to standard size
            image = cv2.resize(image, self.image_size)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(image, self.gaussian_kernel_size, 0)
            
            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(
                blurred,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                self.threshold_block_size,
                self.threshold_c
            )
            
            # Apply morphological operations
            kernel = np.ones((3,3), np.uint8)
            morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Normalize the image
            normalized = cv2.normalize(morph, None, 0, 1, cv2.NORM_MINMAX)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error in preprocessing: {str(e)}")
            raise
            
    def extract_minutiae(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract minutiae points from the preprocessed fingerprint image.
        
        Args:
            image: Preprocessed fingerprint image
            
        Returns:
            Tuple of (minutiae points, minutiae types)
        """
        try:
            # Convert to uint8 for OpenCV operations
            image_uint8 = (image * 255).astype(np.uint8)
            
            # Detect ridges
            ridges = cv2.ximgproc.ridgeFilter(image_uint8, 0, 0, 3, 1, 0, 0)
            
            # Detect minutiae points
            minutiae = cv2.ximgproc.ridgeDetector(image_uint8, 0, 0, 3, 1, 0, 0)
            
            # Classify minutiae types (bifurcations and endings)
            minutiae_types = self._classify_minutiae(minutiae, ridges)
            
            return minutiae, minutiae_types
            
        except Exception as e:
            logger.error(f"Error in minutiae extraction: {str(e)}")
            raise
            
    def _classify_minutiae(self, 
                          minutiae: np.ndarray, 
                          ridges: np.ndarray) -> np.ndarray:
        """
        Classify minutiae points into bifurcations and endings.
        
        Args:
            minutiae: Detected minutiae points
            ridges: Ridge image
            
        Returns:
            Array of minutiae types (0 for ending, 1 for bifurcation)
        """
        # Implementation of minutiae classification
        # This is a simplified version - in production, you'd want a more robust method
        types = np.zeros(len(minutiae))
        
        for i, point in enumerate(minutiae):
            x, y = point.astype(int)
            # Count ridge crossings in 3x3 neighborhood
            neighborhood = ridges[y-1:y+2, x-1:x+2]
            crossings = np.sum(neighborhood > 0)
            
            if crossings >= 3:
                types[i] = 1  # Bifurcation
            else:
                types[i] = 0  # Ending
                
        return types
        
    def create_feature_vector(self, 
                            minutiae: np.ndarray, 
                            types: np.ndarray) -> np.ndarray:
        """
        Create a feature vector from minutiae points and their types.
        
        Args:
            minutiae: Array of minutiae points
            types: Array of minutiae types
            
        Returns:
            Feature vector for matching
        """
        # Normalize coordinates
        normalized_coords = minutiae / self.image_size
        
        # Combine coordinates and types
        features = np.concatenate([
            normalized_coords.flatten(),
            types
        ])
        
        return features 