from flask import Flask, request, jsonify
from flask_cors import CORS
from services.blockchain_service import BlockchainService
from services.fingerprint_service import FingerprintService
from services.biometric_service import BiometricService
from functools import wraps
import jwt
import os
import time
import base64

app = Flask(__name__)
CORS(app)

# Initialize services
blockchain_service = BlockchainService()
fingerprint_service = FingerprintService()
biometric_service = BiometricService()

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 3600  # 1 hour

# Create necessary directories
os.makedirs('data/faces', exist_ok=True)
os.makedirs('data/fingerprints', exist_ok=True)
os.makedirs('data/vectors', exist_ok=True)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
    return decorated

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # For demo purposes, using hardcoded credentials
    if username == 'admin' and password == 'admin123':
        token = jwt.encode({
            'user': username,
            'exp': time.time() + JWT_EXPIRATION
        }, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return jsonify({'token': token})
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/scanner/status', methods=['GET'])
@require_auth
def get_scanner_status():
    """Get the current status of the fingerprint scanner"""
    try:
        status = fingerprint_service.get_scanner_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'message': f'Failed to get scanner status: {str(e)}',
            'connected': False
        }), 500

@app.route('/scanner/connect', methods=['POST'])
@require_auth
def connect_scanner():
    data = request.get_json()
    port = data.get('port', 'COM3')
    
    if fingerprint_service.connect(port):
        return jsonify({'message': 'Scanner connected successfully'})
    return jsonify({'message': 'Failed to connect scanner'}), 400

@app.route('/verify/face', methods=['POST'])
@require_auth
def verify_face():
    data = request.get_json()
    voter_id = data.get('voterId')
    face_data = data.get('faceData')
    
    if not voter_id or not face_data:
        return jsonify({'message': 'Missing voter ID or face data'}), 400
    
    try:
        # Process face image to get 128D vector
        face_vector = biometric_service.process_face_image(face_data)
        if face_vector is None:
            return jsonify({'message': 'No face detected in image'}), 400
        
        # Save face image
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        face_path = f'data/faces/{voter_id}_{timestamp}.jpg'
        face_bytes = base64.b64decode(face_data.split(',')[1])
        with open(face_path, 'wb') as f:
            f.write(face_bytes)
        
        # Save face vector
        vector_path = f'data/vectors/{voter_id}_face.npy'
        biometric_service.save_vector(face_vector, vector_path)
        
        return jsonify({
            'message': 'Face verification successful',
            'vector_path': vector_path
        })
    except Exception as e:
        return jsonify({'message': f'Face verification failed: {str(e)}'}), 500

@app.route('/verify/fingerprint', methods=['POST'])
@require_auth
def verify_fingerprint():
    data = request.get_json()
    voter_id = data.get('voterId')
    
    if not voter_id:
        return jsonify({'message': 'Missing voter ID'}), 400
    
    try:
        # Check scanner connection status
        scanner_status = fingerprint_service.get_scanner_status()
        if not scanner_status['connected']:
            return jsonify({
                'message': 'Fingerprint scanner is not connected',
                'status': scanner_status
            }), 400
        
        # Capture fingerprint data
        fingerprint_data = fingerprint_service.capture_fingerprint()
        if fingerprint_data is None:
            return jsonify({
                'message': 'Failed to capture fingerprint. Please try again.',
                'status': scanner_status
            }), 400
        
        # Process fingerprint to get 128D vector
        fingerprint_vector = biometric_service.process_fingerprint(fingerprint_data)
        if fingerprint_vector is None:
            return jsonify({
                'message': 'Failed to process fingerprint data',
                'status': scanner_status
            }), 400
        
        # Save fingerprint image
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        fingerprint_path = f'data/fingerprints/{voter_id}_{timestamp}.jpg'
        with open(fingerprint_path, 'wb') as f:
            f.write(fingerprint_data)
        
        # Save fingerprint vector
        vector_path = f'data/vectors/{voter_id}_fingerprint.npy'
        biometric_service.save_vector(fingerprint_vector, vector_path)
        
        return jsonify({
            'message': 'Fingerprint verification successful',
            'vector_path': vector_path,
            'status': scanner_status
        })
    except Exception as e:
        return jsonify({
            'message': f'Fingerprint verification failed: {str(e)}',
            'status': fingerprint_service.get_scanner_status()
        }), 500

@app.route('/vote', methods=['POST'])
@require_auth
def cast_vote():
    data = request.get_json()
    voter_id = data.get('voterId')
    party = data.get('party')
    
    if not voter_id or not party:
        return jsonify({'message': 'Missing voter ID or party'}), 400
    
    try:
        # Check if voter has already voted
        if blockchain_service.has_voted(voter_id):
            return jsonify({'message': 'Voter has already cast their vote'}), 400
        
        # Create and mine new block
        block = blockchain_service.create_block(voter_id, party)
        blockchain_service.mine_block(block)
        
        # Add block to chain
        blockchain_service.add_block(block)
        
        return jsonify({
            'message': 'Vote recorded successfully',
            'block_hash': block.hash
        })
    except Exception as e:
        return jsonify({'message': f'Failed to record vote: {str(e)}'}), 500

@app.route('/blockchain', methods=['GET'])
@require_auth
def get_blockchain():
    try:
        blockchain_data = blockchain_service.get_blockchain()
        return jsonify({
            'success': True,
            'blockchain': blockchain_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 