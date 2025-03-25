"""
Polygon smart contract for storing voter verification logs.
"""

from web3 import Web3
from typing import Dict, Any, Optional
from datetime import datetime
import json
from loguru import logger

from ai.config import BLOCKCHAIN_CONFIG, SECURITY_CONFIG

class VoterVerificationContract:
    def __init__(self):
        """Initialize the Polygon contract client."""
        self.config = BLOCKCHAIN_CONFIG["polygon"]
        self._setup_client()
        
    def _setup_client(self):
        """Setup the Web3 client with Polygon network."""
        try:
            # Connect to Polygon network
            self.w3 = Web3(Web3.HTTPProvider(self.config["rpc_url"]))
            
            # Load contract ABI
            with open("contracts/VoterVerification.json", "r") as f:
                contract_json = json.load(f)
                self.contract_abi = contract_json["abi"]
                
            # Initialize contract
            self.contract = self.w3.eth.contract(
                address=self.config["contract_address"],
                abi=self.contract_abi
            )
            
            # Setup account
            self.account = self.w3.eth.account.from_key(self.config["private_key"])
            
        except Exception as e:
            logger.error(f"Error setting up Polygon client: {str(e)}")
            raise
            
    def record_verification(self,
                           voter_id: str,
                           polling_station: str,
                           success: bool,
                           confidence: float,
                           metadata: Dict[str, Any],
                           fabric_tx_id: str) -> str:
        """
        Record verification attempt on Polygon blockchain.
        
        Args:
            voter_id: Voter's unique identifier
            polling_station: Polling station identifier
            success: Whether verification was successful
            confidence: Confidence score
            metadata: Additional verification metadata
            fabric_tx_id: Hyperledger Fabric transaction ID
            
        Returns:
            Transaction hash
        """
        try:
            # Prepare verification record
            record = {
                "voter_id": voter_id,
                "polling_station": polling_station,
                "success": success,
                "confidence": confidence,
                "metadata": metadata,
                "fabric_tx_id": fabric_tx_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Convert record to bytes
            record_bytes = json.dumps(record).encode()
            
            # Create transaction
            transaction = self.contract.functions.recordVerification(
                voter_id,
                polling_station,
                success,
                int(confidence * 100),  # Convert to integer percentage
                record_bytes
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': self.config["gas_limit"],
                'gasPrice': self.w3.to_wei(self.config["gas_price"], 'gwei'),
                'chainId': self._get_chain_id()
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                self.config["private_key"]
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt["transactionHash"].hex()
            
        except Exception as e:
            logger.error(f"Error recording verification on Polygon: {str(e)}")
            raise
            
    def get_verification_history(self,
                                voter_id: str,
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None) -> list:
        """
        Get verification history for a voter.
        
        Args:
            voter_id: Voter's unique identifier
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of verification records
        """
        try:
            # Get verification count
            count = self.contract.functions.getVerificationCount(voter_id).call()
            
            # Get all verification records
            records = []
            for i in range(count):
                record = self.contract.functions.getVerificationRecord(
                    voter_id,
                    i
                ).call()
                
                # Parse record
                record_data = json.loads(record[4].decode())
                
                # Apply time filters if specified
                record_time = datetime.fromisoformat(record_data["timestamp"])
                if start_time and record_time < start_time:
                    continue
                if end_time and record_time > end_time:
                    continue
                    
                records.append(record_data)
                
            return records
            
        except Exception as e:
            logger.error(f"Error getting verification history: {str(e)}")
            raise
            
    def get_polling_station_stats(self,
                                 polling_station: str,
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get verification statistics for a polling station.
        
        Args:
            polling_station: Polling station identifier
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            Statistics dictionary
        """
        try:
            # Get verification count
            count = self.contract.functions.getPollingStationCount(
                polling_station
            ).call()
            
            # Initialize statistics
            stats = {
                "total_verifications": 0,
                "successful_verifications": 0,
                "failed_verifications": 0,
                "average_confidence": 0.0,
                "verification_times": []
            }
            
            # Process records
            total_confidence = 0.0
            for i in range(count):
                record = self.contract.functions.getPollingStationRecord(
                    polling_station,
                    i
                ).call()
                
                # Parse record
                record_data = json.loads(record[4].decode())
                
                # Apply time filters if specified
                record_time = datetime.fromisoformat(record_data["timestamp"])
                if start_time and record_time < start_time:
                    continue
                if end_time and record_time > end_time:
                    continue
                    
                # Update statistics
                stats["total_verifications"] += 1
                if record_data["success"]:
                    stats["successful_verifications"] += 1
                else:
                    stats["failed_verifications"] += 1
                    
                total_confidence += record_data["confidence"]
                stats["verification_times"].append(record_time)
                
            # Calculate average confidence
            if stats["total_verifications"] > 0:
                stats["average_confidence"] = (
                    total_confidence / stats["total_verifications"]
                )
                
            return stats
            
        except Exception as e:
            logger.error(f"Error getting polling station stats: {str(e)}")
            raise
            
    def _get_chain_id(self) -> int:
        """Get the current chain ID."""
        try:
            return self.w3.eth.chain_id
        except Exception as e:
            logger.error(f"Error getting chain ID: {str(e)}")
            raise 