"""
Configuration settings for the fingerprint verification system.
"""

from typing import Dict, Any
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
MODEL_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# Create necessary directories
for directory in [MODEL_DIR, DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# AI Model Configuration
AI_CONFIG: Dict[str, Any] = {
    "input_shape": (224, 224, 1),
    "feature_dim": 512,
    "dropout_rate": 0.5,
    "model_path": str(MODEL_DIR / "fingerprint_model.h5"),
    "tflite_path": str(MODEL_DIR / "fingerprint_model.tflite"),
    "onnx_path": str(MODEL_DIR / "fingerprint_model.onnx"),
}

# Fingerprint Processing Configuration
PROCESSING_CONFIG: Dict[str, Any] = {
    "image_size": (224, 224),
    "gaussian_kernel_size": (5, 5),
    "threshold_block_size": 11,
    "threshold_c": 2,
    "minutiae_threshold": 0.3,
    "ridge_threshold": 0.5,
}

# Verification Configuration
VERIFICATION_CONFIG: Dict[str, Any] = {
    "similarity_threshold": 0.85,
    "use_minutiae": True,
    "minutiae_weight": 0.3,
    "ai_weight": 0.7,
    "max_verification_attempts": 3,
    "verification_timeout": 30,  # seconds
}

# Blockchain Configuration
BLOCKCHAIN_CONFIG: Dict[str, Any] = {
    "fabric": {
        "network_name": "voter_verification_network",
        "channel_name": "voter_channel",
        "chaincode_name": "voter_verification",
        "chaincode_version": "1.0",
        "msp_id": "Org1MSP",
        "peer_endpoint": "localhost:7051",
        "orderer_endpoint": "localhost:7050",
    },
    "polygon": {
        "network": "testnet",  # or "mainnet"
        "contract_address": "",  # To be filled after deployment
        "gas_limit": 500000,
        "gas_price": 50,  # Gwei
    },
    "storage": {
        "ipfs_gateway": "https://ipfs.io/ipfs/",
        "arweave_gateway": "https://arweave.net/",
        "storage_type": "ipfs",  # or "arweave"
    }
}

# Security Configuration
SECURITY_CONFIG: Dict[str, Any] = {
    "hash_algorithm": "sha256",
    "encryption_algorithm": "aes-256-gcm",
    "key_derivation": "pbkdf2",
    "salt_length": 32,
    "key_length": 32,
    "iterations": 100000,
    "token_expiry": 3600,  # seconds
    "max_failed_attempts": 5,
    "lockout_duration": 1800,  # seconds
}

# API Configuration
API_CONFIG: Dict[str, Any] = {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "timeout": 300,  # seconds
    "rate_limit": {
        "requests": 100,
        "period": 60,  # seconds
    },
    "cors_origins": [
        "http://localhost:3000",
        "https://voter-verification.example.com"
    ],
}

# Logging Configuration
LOGGING_CONFIG: Dict[str, Any] = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(BASE_DIR / "logs" / "app.log"),
    "max_size": 10485760,  # 10MB
    "backup_count": 5,
}

# Environment Variables
ENV_VARS: Dict[str, str] = {
    "FABRIC_CA_URL": os.getenv("FABRIC_CA_URL", "http://localhost:7054"),
    "FABRIC_CA_USERNAME": os.getenv("FABRIC_CA_USERNAME", "admin"),
    "FABRIC_CA_PASSWORD": os.getenv("FABRIC_CA_PASSWORD", "adminpw"),
    "POLYGON_PRIVATE_KEY": os.getenv("POLYGON_PRIVATE_KEY", ""),
    "POLYGON_RPC_URL": os.getenv("POLYGON_RPC_URL", "https://polygon-mumbai.infura.io/v3/your-project-id"),
    "IPFS_PROJECT_ID": os.getenv("IPFS_PROJECT_ID", ""),
    "IPFS_PROJECT_SECRET": os.getenv("IPFS_PROJECT_SECRET", ""),
    "ARWEAVE_KEY_FILE": os.getenv("ARWEAVE_KEY_FILE", ""),
}

# Create logs directory
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Update logging config with absolute path
LOGGING_CONFIG["file"] = str(LOGS_DIR / "app.log") 