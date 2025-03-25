import numpy as np
import cv2
from face_recognition import face_encodings, face_locations, compare_faces
from typing import Tuple, Optional
from .data_service import DataService

class FaceService:
    def __init__(self):
        # Dummy dataset of pre-registered face encodings
        # Format: {voter_id: face_encoding}
        self.registered_faces: dict = {
            "RDV6404990": np.random.rand(128),  # Temporary random encoding until we process the real image
            "KUSHAL001": np.random.rand(128),  # Keeping one test entry
        }
        self.data_service = DataService()
    
    def process_image(self, image_data: bytes) -> np.ndarray:
        """Process image data and extract face encoding"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to RGB for face_recognition library
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations_list = face_locations(rgb_image)
            if not face_locations_list:
                raise ValueError("No face detected in the image")
                
            # Get face encodings
            face_encodings_list = face_encodings(rgb_image, face_locations_list)
            if not face_encodings_list:
                raise ValueError("Could not encode face from the image")
                
            return face_encodings_list[0]
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return np.random.rand(128)  # Fallback for testing
    
    def verify_face(self, voter_id, face_data):
        stored_face_data = self.data_service.get_face_data(voter_id)
        if not stored_face_data:
            return False
            
        # In a real implementation, this would use actual face recognition
        # For demo purposes, we'll just compare the strings
        return stored_face_data == face_data
    
    def register_face(self, voter_id: str, face_encoding: np.ndarray) -> bool:
        """
        Register a new face in the dataset
        """
        if voter_id in self.registered_faces:
            return False
            
        self.registered_faces[voter_id] = face_encoding
        return True 