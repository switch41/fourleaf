import cv2
import numpy as np
import base64
from services.biometric_service import BiometricService
import os
import urllib.request

def download_sample_face():
    """Download a sample face image for testing"""
    url = "https://raw.githubusercontent.com/ageitgey/face_recognition/master/examples/obama.jpg"
    try:
        urllib.request.urlretrieve(url, "test_data/sample_face.jpg")
        return True
    except Exception as e:
        print(f"Error downloading sample face: {str(e)}")
        return False

def create_test_face():
    """Create a test face image"""
    # Create a larger image for better face detection
    image = np.zeros((400, 400, 3), dtype=np.uint8)
    image.fill(255)  # White background
    
    # Draw face outline
    cv2.ellipse(image, (200, 200), (150, 200), 0, 0, 360, (255, 220, 180), -1)
    
    # Draw eyes
    cv2.ellipse(image, (150, 160), (30, 20), 0, 0, 360, (0, 0, 0), -1)
    cv2.ellipse(image, (250, 160), (30, 20), 0, 0, 360, (0, 0, 0), -1)
    
    # Draw eyebrows
    cv2.line(image, (120, 120), (180, 140), (0, 0, 0), 3)
    cv2.line(image, (220, 140), (280, 120), (0, 0, 0), 3)
    
    # Draw nose
    cv2.line(image, (200, 180), (200, 220), (0, 0, 0), 2)
    
    # Draw mouth
    cv2.ellipse(image, (200, 250), (50, 30), 0, 0, 180, (0, 0, 0), 2)
    
    # Add some shading
    cv2.circle(image, (150, 150), 20, (255, 200, 150), -1)
    cv2.circle(image, (250, 150), 20, (255, 200, 150), -1)
    
    return image

def create_test_fingerprint():
    """Create a test fingerprint pattern"""
    # Create a simple fingerprint-like pattern
    image = np.zeros((200, 200), dtype=np.uint8)
    # Draw some ridges
    for i in range(0, 200, 10):
        cv2.line(image, (0, i), (200, i), 255, 2)
    # Add some noise
    noise = np.random.normal(0, 25, (200, 200)).astype(np.uint8)
    image = cv2.add(image, noise)
    return image

def test_face_processing():
    """Test face image processing"""
    print("\nTesting face processing...")
    
    # Create test directory
    os.makedirs('test_data', exist_ok=True)
    
    # Download sample face image
    if not download_sample_face():
        print("Failed to download sample face image")
        return
    
    # Read the sample face image
    face_image = cv2.imread('test_data/sample_face.jpg')
    if face_image is None:
        print("Failed to read sample face image")
        return
    
    # Convert to base64
    _, buffer = cv2.imencode('.jpg', face_image)
    face_data = base64.b64encode(buffer).decode('utf-8')
    
    # Process face image
    biometric_service = BiometricService()
    face_vector = biometric_service.process_face_image(face_data)
    
    if face_vector is not None:
        print(f"Successfully created 128D vector from face image")
        print(f"Vector shape: {face_vector.shape}")
        print(f"Vector mean: {np.mean(face_vector):.4f}")
        print(f"Vector std: {np.std(face_vector):.4f}")
        
        # Save vector
        biometric_service.save_vector(face_vector, 'test_data/test_face_vector.npy')
        print("Saved face vector to test_data/test_face_vector.npy")
    else:
        print("Failed to process face image")

def test_fingerprint_processing():
    """Test fingerprint processing"""
    print("\nTesting fingerprint processing...")
    
    # Create test fingerprint
    fingerprint_image = create_test_fingerprint()
    
    # Save test image
    cv2.imwrite('test_data/test_fingerprint.jpg', fingerprint_image)
    
    # Convert to bytes
    _, buffer = cv2.imencode('.jpg', fingerprint_image)
    fingerprint_data = buffer.tobytes()
    
    # Process fingerprint
    biometric_service = BiometricService()
    fingerprint_vector = biometric_service.process_fingerprint(fingerprint_data)
    
    if fingerprint_vector is not None:
        print(f"Successfully created 128D vector from fingerprint")
        print(f"Vector shape: {fingerprint_vector.shape}")
        print(f"Vector mean: {np.mean(fingerprint_vector):.4f}")
        print(f"Vector std: {np.std(fingerprint_vector):.4f}")
        
        # Save vector
        biometric_service.save_vector(fingerprint_vector, 'test_data/test_fingerprint_vector.npy')
        print("Saved fingerprint vector to test_data/test_fingerprint_vector.npy")
    else:
        print("Failed to process fingerprint")

def test_vector_comparison():
    """Test vector comparison methods"""
    print("\nTesting vector comparison...")
    
    biometric_service = BiometricService()
    
    # Load saved vectors
    face_vector = biometric_service.load_vector('test_data/test_face_vector.npy')
    fingerprint_vector = biometric_service.load_vector('test_data/test_fingerprint_vector.npy')
    
    if face_vector is not None and fingerprint_vector is not None:
        # Create slightly modified vectors for testing
        face_vector_modified = face_vector + np.random.normal(0, 0.1, face_vector.shape)
        fingerprint_vector_modified = fingerprint_vector + np.random.normal(0, 0.1, fingerprint_vector.shape)
        
        # Test face vector comparison
        face_match = biometric_service.compare_face_vectors(face_vector, face_vector_modified)
        print(f"Face vectors match: {face_match}")
        
        # Test fingerprint vector comparison
        fingerprint_match = biometric_service.compare_fingerprint_vectors(fingerprint_vector, fingerprint_vector_modified)
        print(f"Fingerprint vectors match: {fingerprint_match}")
    else:
        print("Failed to load vectors for comparison")

if __name__ == '__main__':
    print("Starting biometric tests...")
    test_face_processing()
    test_fingerprint_processing()
    test_vector_comparison()
    print("\nBiometric tests completed.") 