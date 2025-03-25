import numpy as np
import serial
import time
import os
from typing import Dict, Tuple, Optional, Any
from .data_service import DataService

class FingerprintService:
    def __init__(self):
        self.data_service = DataService()
        self.scanner_status = "ready"
        # Dummy dataset of pre-registered fingerprints
        # Format: {voter_id: (fingerprint_vector, party_choice)}
        self.registered_fingerprints: Dict[str, Tuple[np.ndarray, str]] = {
            "RDV6404990": (np.random.rand(128), "Party A"),  # Real voter's fingerprint
            "KUSHAL001": (np.random.rand(128), "Party B"),  # Keeping one test entry
        }
        self.port = 'COM3'  # Default port
        self.baud_rate = 57600
        self.timeout = 1
        self.connected = False
        self.serial = None
        
    def get_status(self):
        return {"status": self.scanner_status}

    def initialize_scanner(self):
        self.scanner_status = "ready"
        return {"status": "success", "message": "Scanner initialized"}

    def convert_to_vector(self, fingerprint_data: bytes) -> np.ndarray:
        """
        Convert raw fingerprint data to 128-dimensional vector
        In a real implementation, this would use proper fingerprint processing algorithms
        """
        # For demo purposes, we'll generate a random vector
        # In production, this would use proper fingerprint processing
        return np.random.rand(128)
    
    def verify_fingerprint(self, voter_id: str, fingerprint_data: bytes) -> bool:
        """
        Verify a fingerprint against stored data
        Args:
            voter_id: The ID of the voter
            fingerprint_data: The fingerprint data to verify
        Returns:
            bool: True if verification successful, False otherwise
        """
        stored_fingerprint = self.data_service.get_fingerprint_data(voter_id)
        if not stored_fingerprint:
            return False
            
        # In a real implementation, this would use actual fingerprint matching
        # For demo purposes, we'll just compare the strings
        return stored_fingerprint == fingerprint_data
    
    def register_fingerprint(self, voter_id: str, fingerprint_vector: np.ndarray, party_choice: str) -> bool:
        """
        Register a new fingerprint in the dataset
        """
        if voter_id in self.registered_fingerprints:
            return False
            
        self.registered_fingerprints[voter_id] = (fingerprint_vector, party_choice)
        return True

    def connect(self, port: str = None) -> bool:
        """Connect to the fingerprint scanner"""
        try:
            if port:
                self.port = port
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            self.connected = True
            return True
        except Exception as e:
            print(f"Error connecting to scanner: {str(e)}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from the fingerprint scanner"""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.connected = False

    def get_scanner_status(self) -> Dict[str, Any]:
        """
        Get the current status of the fingerprint scanner
        Returns:
            Dict containing scanner status information
        """
        return {
            'connected': self.connected,
            'port': self.port,
            'baud_rate': self.baud_rate
        }

    def capture_fingerprint(self) -> Optional[bytes]:
        """Capture fingerprint data from the scanner"""
        if not self.connected:
            print("Scanner not connected")
            return None

        try:
            # Send command to capture fingerprint
            self.serial.write(b'\x01')  # Example command
            time.sleep(1)  # Wait for capture

            # Read the response
            if self.serial.in_waiting:
                data = self.serial.read(self.serial.in_waiting)
                return data
            return None
        except Exception as e:
            print(f"Error capturing fingerprint: {str(e)}")
            return None

    def save_fingerprint(self, voter_id: str, fingerprint_data: bytes) -> bool:
        """
        Save a fingerprint template
        Args:
            voter_id: The ID of the voter
            fingerprint_data: The fingerprint data to save
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs('data/fingerprints', exist_ok=True)
            
            # Save the fingerprint data
            filename = f'data/fingerprints/{voter_id}_{int(time.time())}.bin'
            with open(filename, 'wb') as f:
                f.write(fingerprint_data)
            return True
        except Exception as e:
            print(f"Error saving fingerprint: {str(e)}")
            return False 