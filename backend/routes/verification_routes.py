from flask import Blueprint, request, jsonify
from services.fingerprint_service import FingerprintService
from services.face_service import FaceService
from utils.auth_decorator import require_auth

verification_bp = Blueprint('verification', __name__)
fingerprint_service = FingerprintService()
face_service = FaceService()

@verification_bp.route('/verify', methods=['POST'])
@require_auth
def verify():
    data = request.get_json()
    voter_id = data.get('voter_id')
    verification_type = data.get('type', 'fingerprint')
    
    if not voter_id:
        return jsonify({'error': 'Voter ID is required'}), 400
        
    if verification_type == 'fingerprint':
        fingerprint_data = data.get('fingerprint_data')
        if not fingerprint_data:
            return jsonify({'error': 'Fingerprint data is required'}), 400
            
        result = fingerprint_service.verify_fingerprint(voter_id, fingerprint_data)
        if result:
            return jsonify({
                'success': True,
                'message': 'Fingerprint verified successfully'
            })
            
    elif verification_type == 'face':
        face_data = data.get('face_data')
        if not face_data:
            return jsonify({'error': 'Face data is required'}), 400
            
        result = face_service.verify_face(voter_id, face_data)
        if result:
            return jsonify({
                'success': True,
                'message': 'Face verified successfully'
            })
            
    return jsonify({
        'success': False,
        'error': 'Verification failed'
    }), 401

@verification_bp.route('/register', methods=['POST'])
def register_fingerprint():
    """Endpoint to register a fingerprint"""
    try:
        # Check if image is in the request
        if 'fingerprint' not in request.files:
            # Try to get base64 encoded image from form data
            if 'fingerprint_base64' in request.form:
                # Decode base64 image
                encoded_data = request.form['fingerprint_base64']
                nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
                fingerprint_image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            else:
                return jsonify({"error": "No fingerprint image provided"}), 400
        else:
            # Read image from file
            file = request.files['fingerprint']
            nparr = np.fromstring(file.read(), np.uint8)
            fingerprint_image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        # Get voter ID
        voter_id = request.form.get('voter_id')
        
        if not voter_id:
            return jsonify({"error": "Voter ID is required"}), 400
            
        # Get additional metadata
        metadata = {}
        for key in request.form:
            if key not in ['voter_id', 'fingerprint_base64']:
                metadata[key] = request.form.get(key)
                
        # Register fingerprint
        success = fingerprint_service.register_fingerprint(
            fingerprint_image, 
            voter_id, 
            metadata
        )
        
        if success:
            return jsonify({"success": True, "message": "Fingerprint registered successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to register fingerprint"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@verification_bp.route('/verify-face', methods=['POST'])
def verify_face():
    """Endpoint to verify a face"""
    try:
        # Check if image is in the request
        if 'face' not in request.files and 'face_base64' not in request.form:
            return jsonify({"error": "No face image provided"}), 400
            
        if 'face_base64' in request.form:
            # Decode base64 image
            encoded_data = request.form['face_base64']
            nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
            face_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            # Read image from file
            file = request.files['face']
            nparr = np.fromstring(file.read(), np.uint8)
            face_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Get voter ID and polling station
        voter_id = request.form.get('voter_id')
        polling_station = request.form.get('polling_station')
        
        if not voter_id:
            return jsonify({"error": "Voter ID is required"}), 400
            
        # Process face data and verify
        # In a real implementation, use the face_service for proper verification
        # For this example, we'll return a simulated result
        
        # Simulate verification (replace with actual verification)
        success = True  # For demo purposes
        confidence = 0.92  # For demo purposes
        
        result = {
            "success": success,
            "confidence": confidence,
            "metadata": {
                "verification_method": "face_recognition",
                "polling_station": polling_station
            },
            "transaction_hash": str(uuid.uuid4())
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 