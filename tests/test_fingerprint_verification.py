"""
Test suite for fingerprint verification system.
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
import os

from ai.preprocessing.fingerprint_processor import FingerprintProcessor
from ai.models.fingerprint_model import FingerprintModel
from ai.utils.verification import FingerprintVerifier

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"

@pytest.fixture
def fingerprint_processor():
    """Create a FingerprintProcessor instance for testing."""
    return FingerprintProcessor()

@pytest.fixture
def fingerprint_model():
    """Create a FingerprintModel instance for testing."""
    return FingerprintModel()

@pytest.fixture
def fingerprint_verifier():
    """Create a FingerprintVerifier instance for testing."""
    return FingerprintVerifier()

def test_preprocessing(fingerprint_processor):
    """Test fingerprint preprocessing."""
    # Create a dummy fingerprint image
    image = np.random.rand(224, 224)
    
    # Test preprocessing
    processed = fingerprint_processor.preprocess_image(image)
    
    # Check output shape and range
    assert processed.shape == (224, 224)
    assert np.min(processed) >= 0
    assert np.max(processed) <= 1

def test_minutiae_extraction(fingerprint_processor):
    """Test minutiae extraction."""
    # Create a dummy fingerprint image
    image = np.random.rand(224, 224)
    
    # Test minutiae extraction
    minutiae, types = fingerprint_processor.extract_minutiae(image)
    
    # Check output types
    assert isinstance(minutiae, np.ndarray)
    assert isinstance(types, np.ndarray)
    
    # Check array shapes
    if len(minutiae) > 0:
        assert minutiae.shape[1] == 2  # x, y coordinates
        assert len(types) == len(minutiae)

def test_feature_extraction(fingerprint_model):
    """Test feature extraction."""
    # Create a dummy fingerprint image
    image = np.random.rand(224, 224, 1)
    
    # Test feature extraction
    features = fingerprint_model.extract_features(image)
    
    # Check output shape and normalization
    assert features.shape == (512,)  # Default feature dimension
    assert np.isclose(np.linalg.norm(features), 1.0)

def test_similarity_computation(fingerprint_model):
    """Test similarity computation between feature vectors."""
    # Create dummy feature vectors
    features1 = np.random.rand(512)
    features2 = np.random.rand(512)
    
    # Test similarity computation
    similarity = fingerprint_model.compute_similarity(features1, features2)
    
    # Check output range
    assert 0 <= similarity <= 1

def test_verification(fingerprint_verifier):
    """Test fingerprint verification."""
    # Create dummy input and stored data
    input_image = np.random.rand(224, 224)
    stored_features = np.random.rand(512)
    stored_minutiae = (np.random.rand(10, 2), np.random.randint(0, 2, 10))
    
    # Test verification
    result, confidence, metadata = fingerprint_verifier.verify_fingerprint(
        input_image,
        stored_features,
        stored_minutiae
    )
    
    # Check output types and ranges
    assert isinstance(result, bool)
    assert 0 <= confidence <= 1
    assert isinstance(metadata, dict)
    
    # Check metadata fields
    assert 'timestamp' in metadata
    assert 'ai_similarity' in metadata
    assert 'confidence_score' in metadata
    assert 'verification_result' in metadata
    assert 'verification_method' in metadata

def test_verification_hash(fingerprint_verifier):
    """Test verification hash creation."""
    # Create dummy data
    features = np.random.rand(512)
    minutiae = (np.random.rand(10, 2), np.random.randint(0, 2, 10))
    
    # Test hash creation
    hash_value = fingerprint_verifier.create_verification_hash(features, minutiae)
    
    # Check hash format
    assert isinstance(hash_value, str)
    assert len(hash_value) == 64  # SHA-256 hash length

def test_minutiae_similarity(fingerprint_verifier):
    """Test minutiae similarity computation."""
    # Create dummy minutiae data
    minutiae1 = np.random.rand(5, 2)
    types1 = np.random.randint(0, 2, 5)
    minutiae2 = np.random.rand(5, 2)
    types2 = np.random.randint(0, 2, 5)
    
    # Test similarity computation
    similarity = fingerprint_verifier._compute_minutiae_similarity(
        minutiae1, types1,
        minutiae2, types2
    )
    
    # Check output range
    assert 0 <= similarity <= 1

def test_model_save_load(fingerprint_model, tmp_path):
    """Test model saving and loading."""
    # Create a temporary path for the model
    model_path = tmp_path / "test_model"
    
    # Test model saving
    fingerprint_model.save_model(str(model_path))
    assert model_path.exists()
    
    # Create a new model instance
    new_model = FingerprintModel()
    
    # Test model loading
    new_model.load_model(str(model_path))
    
    # Verify the loaded model works
    test_image = np.random.rand(224, 224, 1)
    features = new_model.extract_features(test_image)
    assert features.shape == (512,) 