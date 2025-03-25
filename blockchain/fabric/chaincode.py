"""
Hyperledger Fabric chaincode for voter verification.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
from fabric_sdk_py import Client, User, ChaincodeSpec, ChaincodeProposalRequest
from fabric_sdk_py.fabric_ca_client import FabricCAClient
from loguru import logger

from ai.config import BLOCKCHAIN_CONFIG, SECURITY_CONFIG

class VoterVerificationChaincode:
    def __init__(self):
        """Initialize the chaincode client."""
        self.client = Client()
        self.config = BLOCKCHAIN_CONFIG["fabric"]
        self._setup_client()
        
    def _setup_client(self):
        """Setup the Fabric client with network configuration."""
        try:
            # Load network configuration
            self.client.load_from_config(
                network_config_path="config/network-config.yaml"
            )
            
            # Setup user context
            self.user = User(
                username=self.config["msp_id"],
                msp_id=self.config["msp_id"]
            )
            
            # Setup CA client
            self.ca_client = FabricCAClient(
                endpoint=self.config["ca_url"],
                ca_certs_path="config/ca-cert.pem"
            )
            
            # Enroll user
            self._enroll_user()
            
        except Exception as e:
            logger.error(f"Error setting up Fabric client: {str(e)}")
            raise
            
    def _enroll_user(self):
        """Enroll user with Fabric CA."""
        try:
            # Enroll user
            enrollment = self.ca_client.enroll(
                username=self.config["ca_username"],
                password=self.config["ca_password"]
            )
            
            # Set user credentials
            self.user.enrollment = enrollment
            
            # Set user context
            self.client.set_user_context(self.user)
            
        except Exception as e:
            logger.error(f"Error enrolling user: {str(e)}")
            raise
            
    def store_voter_data(self,
                         voter_id: str,
                         features: bytes,
                         minutiae: Optional[bytes] = None) -> str:
        """
        Store voter fingerprint data on the blockchain.
        
        Args:
            voter_id: Voter's unique identifier
            features: Serialized feature vector
            minutiae: Optional serialized minutiae data
            
        Returns:
            Transaction ID
        """
        try:
            # Create data hash
            data_hash = self._create_data_hash(features, minutiae)
            
            # Prepare chaincode request
            request = ChaincodeProposalRequest(
                chaincode_id=self.config["chaincode_name"],
                fcn="storeVoterData",
                args=[voter_id, data_hash.hex()]
            )
            
            # Send transaction
            response = self.client.chaincode_propose(request)
            
            # Wait for transaction to be committed
            self.client.wait_for_proposal_commit(response)
            
            return response.transaction_id
            
        except Exception as e:
            logger.error(f"Error storing voter data: {str(e)}")
            raise
            
    def verify_voter(self,
                     voter_id: str,
                     features: bytes,
                     minutiae: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Verify voter's fingerprint data.
        
        Args:
            voter_id: Voter's unique identifier
            features: Serialized feature vector
            minutiae: Optional serialized minutiae data
            
        Returns:
            Verification result with metadata
        """
        try:
            # Create data hash
            data_hash = self._create_data_hash(features, minutiae)
            
            # Prepare chaincode request
            request = ChaincodeProposalRequest(
                chaincode_id=self.config["chaincode_name"],
                fcn="verifyVoter",
                args=[voter_id, data_hash.hex()]
            )
            
            # Send transaction
            response = self.client.chaincode_propose(request)
            
            # Wait for transaction to be committed
            self.client.wait_for_proposal_commit(response)
            
            # Parse response
            result = json.loads(response.payload)
            
            # Add verification timestamp
            result["timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Error verifying voter: {str(e)}")
            raise
            
    def record_verification(self,
                           voter_id: str,
                           polling_station: str,
                           success: bool,
                           confidence: float,
                           metadata: Dict[str, Any]) -> str:
        """
        Record verification attempt on the blockchain.
        
        Args:
            voter_id: Voter's unique identifier
            polling_station: Polling station identifier
            success: Whether verification was successful
            confidence: Confidence score
            metadata: Additional verification metadata
            
        Returns:
            Transaction ID
        """
        try:
            # Prepare verification record
            record = {
                "voter_id": voter_id,
                "polling_station": polling_station,
                "success": success,
                "confidence": confidence,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Prepare chaincode request
            request = ChaincodeProposalRequest(
                chaincode_id=self.config["chaincode_name"],
                fcn="recordVerification",
                args=[json.dumps(record)]
            )
            
            # Send transaction
            response = self.client.chaincode_propose(request)
            
            # Wait for transaction to be committed
            self.client.wait_for_proposal_commit(response)
            
            return response.transaction_id
            
        except Exception as e:
            logger.error(f"Error recording verification: {str(e)}")
            raise
            
    def _create_data_hash(self,
                          features: bytes,
                          minutiae: Optional[bytes] = None) -> bytes:
        """
        Create a secure hash of the fingerprint data.
        
        Args:
            features: Serialized feature vector
            minutiae: Optional serialized minutiae data
            
        Returns:
            Hash of the data
        """
        try:
            # Combine data
            if minutiae:
                data = features + minutiae
            else:
                data = features
                
            # Create hash
            return hashlib.sha256(data).digest()
            
        except Exception as e:
            logger.error(f"Error creating data hash: {str(e)}")
            raise 