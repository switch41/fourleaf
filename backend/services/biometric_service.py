import cv2
import numpy as np
import face_recognition
import base64
import os
from typing import Optional, Tuple

class BiometricService:
    def __init__(self):
        self.face_tolerance = 0.6
        self.fingerprint_threshold = 0.8

    def process_face_image(self, face_data: str) -> Optional[np.ndarray]:
        """
        Process face image and extract 128D vector
        Args:
            face_data: Base64 encoded face image
        Returns:
            128D vector if successful, None otherwise
        """
        try:
            # Remove data URL prefix if present
            if ',' in face_data:
                face_data = face_data.split(',')[1]
            
            # Decode base64 image
            image_data = base64.b64decode(face_data)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                print("Failed to decode image")
                return None
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect face locations
            face_locations = face_recognition.face_locations(rgb_image, model="hog")
            if not face_locations:
                print("No face detected in image")
                return None
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            if not face_encodings:
                print("Could not encode face features")
                return None
            
            # Get the first face encoding
            face_encoding = face_encodings[0]
            
            # Normalize the vector
            face_encoding = face_encoding / np.linalg.norm(face_encoding)
            
            return face_encoding
        except Exception as e:
            print(f"Error processing face image: {str(e)}")
            return None

    def process_fingerprint(self, fingerprint_data: bytes) -> Optional[np.ndarray]:
        """
        Process fingerprint data and extract 128D vector
        Args:
            fingerprint_data: Raw fingerprint image data
        Returns:
            128D vector if successful, None otherwise
        """
        try:
            # For testing purposes, generate a random 128D vector
            # In a real system, this would process actual fingerprint data
            vector = np.random.rand(128)
            vector = vector / np.linalg.norm(vector)  # Normalize
            return vector
        except Exception as e:
            print(f"Error processing fingerprint: {str(e)}")
            return None

    def compare_face_vectors(self, vector1: np.ndarray, vector2: np.ndarray) -> bool:
        """
        Compare two face vectors using Euclidean distance
        Args:
            vector1: First face vector
            vector2: Second face vector
        Returns:
            True if vectors match, False otherwise
        """
        try:
            distance = np.linalg.norm(vector1 - vector2)
            return distance <= self.face_tolerance
        except Exception as e:
            print(f"Error comparing face vectors: {str(e)}")
            return False

    def compare_fingerprint_vectors(self, vector1: np.ndarray, vector2: np.ndarray) -> bool:
        """
        Compare two fingerprint vectors using cosine similarity
        Args:
            vector1: First fingerprint vector
            vector2: Second fingerprint vector
        Returns:
            True if vectors match, False otherwise
        """
        try:
            similarity = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
            return similarity >= self.fingerprint_threshold
        except Exception as e:
            print(f"Error comparing fingerprint vectors: {str(e)}")
            return False

    def save_vector(self, vector: np.ndarray, path: str) -> bool:
        """
        Save biometric vector to file
        Args:
            vector: Biometric vector to save
            path: Path to save the vector
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            np.save(path, vector)
            return True
        except Exception as e:
            print(f"Error saving vector: {str(e)}")
            return False

    def load_vector(self, path: str) -> Optional[np.ndarray]:
        """
        Load biometric vector from file
        Args:
            path: Path to load the vector from
        Returns:
            Vector if successful, None otherwise
        """
        try:
            return np.load(path)
        except Exception as e:
            print(f"Error loading vector: {str(e)}")
            return None 