import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from flask_cors import CORS
from services.auth_service import AuthService
from services.biometric_service import BiometricService
from services.blockchain_service import BlockchainService
from services.face_service import FaceService
from services.fingerprint_service import FingerprintService
from functools import wraps
import jwt
import time
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Update CORS configuration for Render deployment
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://fourleaf-frontend.onrender.com"  # Render frontend URL
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize services
auth_service = AuthService()
biometric_service = BiometricService()
blockchain_service = BlockchainService()
face_service = FaceService()
fingerprint_service = FingerprintService()

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
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400

        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # For demo purposes, using hardcoded credentials
        # In production, this should use a proper database and password hashing
        if username == 'admin' and password == 'admin123':
            token = jwt.encode({
                'user': username,
                'exp': time.time() + JWT_EXPIRATION
            }, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            logger.info(f"Successful login for user: {username}")
            return jsonify({
                'success': True,
                'token': token,
                'message': 'Login successful'
            })
        
        logger.warning(f"Failed login attempt for user: {username}")
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during login'
        }), 500

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
    
    # For demo purposes, always return success
    return jsonify({
        'message': 'Face verification successful (Demo Mode)',
        'vector_path': f'data/vectors/{voter_id}_face.npy'
    })

@app.route('/verify/fingerprint', methods=['POST'])
@require_auth
def verify_fingerprint():
    data = request.get_json()
    voter_id = data.get('voterId')
    
    if not voter_id:
        return jsonify({'message': 'Missing voter ID'}), 400
    
    # For demo purposes, always return success
    return jsonify({
        'message': 'Fingerprint verification successful (Demo Mode)',
        'vector_path': f'data/vectors/{voter_id}_fingerprint.npy'
    })

@app.route('/verify/voter-id', methods=['POST'])
@require_auth
def verify_voter_id():
    data = request.get_json()
    voter_id = data.get('voterId')
    
    if not voter_id:
        return jsonify({'message': 'Missing voter ID'}), 400
    
    # For demo purposes, always return success
    return jsonify({
        'message': 'Voter ID verification successful (Demo Mode)',
        'verified': True
    })

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
        logger.error(f"Error fetching blockchain: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 