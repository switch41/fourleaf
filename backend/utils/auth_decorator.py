from functools import wraps
from flask import request, jsonify
from services.auth_service import AuthService

auth_service = AuthService()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
            
        try:
            # Remove 'Bearer ' from token
            token = auth_header.split(' ')[1]
            user = auth_service.verify_token(token)
            
            if not user:
                return jsonify({'error': 'Invalid token'}), 401
                
            # Add user to request context
            request.user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 401
            
    return decorated

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
            
        try:
            # Remove 'Bearer ' from token
            token = auth_header.split(' ')[1]
            
            if not auth_service.is_admin(token):
                return jsonify({'error': 'Admin access required'}), 403
                
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 401
            
    return decorated 