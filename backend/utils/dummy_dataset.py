import os
import json
import numpy as np
import cv2
from pathlib import Path
import shutil
import logging

logger = logging.getLogger(__name__)

class DummyDatasetManager:
    """Manages the dummy fingerprint dataset for testing and development purposes"""
    
    def __init__(self, dataset_path="dummy_dataset"):
        """Initialize the dummy dataset manager
        
        Args:
            dataset_path: Path to the dummy dataset directory
        """
        self.dataset_path = Path(dataset_path)
        self.ensure_dataset_exists()
        
    def ensure_dataset_exists(self):
        """Create the dataset directory if it doesn't exist"""
        self.dataset_path.mkdir(parents=True, exist_ok=True)
        
        # Create metadata file if it doesn't exist
        metadata_path = self.dataset_path / "metadata.json"
        if not metadata_path.exists():
            with open(metadata_path, "w") as f:
                json.dump({"fingerprints": {}}, f)
    
    def add_fingerprint(self, voter_id, fingerprint_image, metadata=None):
        """Add a fingerprint to the dummy dataset
        
        Args:
            voter_id: Unique ID for the voter
            fingerprint_image: Numpy array containing the fingerprint image
            metadata: Additional metadata for the fingerprint
            
        Returns:
            Path to the saved fingerprint
        """
        if metadata is None:
            metadata = {}
            
        # Ensure directory exists
        voter_dir = self.dataset_path / voter_id
        voter_dir.mkdir(exist_ok=True)
        
        # Save the fingerprint image
        fp_path = voter_dir / "fingerprint.jpg"
        cv2.imwrite(str(fp_path), fingerprint_image)
        
        # Update metadata
        self._update_metadata(voter_id, metadata)
        
        return fp_path
    
    def get_fingerprint(self, voter_id):
        """Get a fingerprint from the dummy dataset
        
        Args:
            voter_id: Unique ID for the voter
            
        Returns:
            Tuple of (fingerprint_image, metadata) or (None, None) if not found
        """
        fp_path = self.dataset_path / voter_id / "fingerprint.jpg"
        
        if not fp_path.exists():
            return None, None
            
        # Load the fingerprint image
        fingerprint = cv2.imread(str(fp_path), cv2.IMREAD_GRAYSCALE)
        
        # Load metadata
        metadata = self._get_metadata(voter_id)
        
        return fingerprint, metadata
    
    def delete_fingerprint(self, voter_id):
        """Delete a fingerprint from the dummy dataset
        
        Args:
            voter_id: Unique ID for the voter
            
        Returns:
            True if deleted, False if not found
        """
        voter_dir = self.dataset_path / voter_id
        
        if not voter_dir.exists():
            return False
            
        # Delete the directory
        shutil.rmtree(voter_dir)
        
        # Update metadata
        self._delete_metadata(voter_id)
        
        return True
    
    def _update_metadata(self, voter_id, metadata):
        """Update the metadata for a voter"""
        metadata_path = self.dataset_path / "metadata.json"
        
        with open(metadata_path, "r") as f:
            data = json.load(f)
            
        data["fingerprints"][voter_id] = metadata
        
        with open(metadata_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def _get_metadata(self, voter_id):
        """Get metadata for a voter"""
        metadata_path = self.dataset_path / "metadata.json"
        
        with open(metadata_path, "r") as f:
            data = json.load(f)
            
        return data["fingerprints"].get(voter_id, {})
    
    def _delete_metadata(self, voter_id):
        """Delete metadata for a voter"""
        metadata_path = self.dataset_path / "metadata.json"
        
        with open(metadata_path, "r") as f:
            data = json.load(f)
            
        if voter_id in data["fingerprints"]:
            del data["fingerprints"][voter_id]
            
        with open(metadata_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def list_fingerprints(self):
        """List all fingerprints in the dataset
        
        Returns:
            List of voter IDs
        """
        metadata_path = self.dataset_path / "metadata.json"
        
        with open(metadata_path, "r") as f:
            data = json.load(f)
            
        return list(data["fingerprints"].keys()) 