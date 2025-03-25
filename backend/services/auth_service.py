import jwt
import time
from typing import Dict, Optional
import os
from dotenv import load_dotenv
from .data_service import DataService

load_dotenv()

class AuthService:
    def __init__(self):
        self.secret_key = "your-secret-key-here"  # In production, use environment variable
        self.token_expiry = 3600  # 1 hour
        self.data_service = DataService()
        self.users = {
            "admin": {
                "password": "admin123",
                "role": "admin",
                "name": "Admin User"
            }
        }
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and generate JWT token
        Args:
            username: The username
            password: The password
        Returns:
            JWT token if authentication successful, None otherwise
        """
        # For demo purposes, accept admin/admin123
        if username == "admin" and password == "admin123":
            return self.generate_token(username)
        return None
    
    def generate_token(self, username: str) -> str:
        """
        Generate a JWT token
        Args:
            username: The username
        Returns:
            JWT token
        """
        payload = {
            "username": username,
            "exp": int(time.time()) + self.token_expiry
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> bool:
        """
        Verify a JWT token
        Args:
            token: The JWT token to verify
        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
    
    def is_admin(self, token: str) -> bool:
        """
        Check if the token belongs to an admin user
        Args:
            token: The JWT token to check
        Returns:
            bool: True if user is admin, False otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload.get("username") == "admin"
        except:
            return False 