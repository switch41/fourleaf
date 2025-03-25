import hashlib
import json
import time
from typing import List, Dict, Any, Optional

class Block:
    def __init__(self, index: int, timestamp: float, data: Dict[str, Any], previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0  # Initialize nonce first
        self.hash = self.calculate_hash()  # Then calculate hash

    def calculate_hash(self) -> str:
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int = 4) -> None:
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.difficulty = 4
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        genesis_block = Block(0, time.time(), {"message": "Genesis Block"}, "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: Dict[str, Any]) -> Block:
        block = Block(
            len(self.chain),
            time.time(),
            data,
            self.get_latest_block().hash
        )
        block.mine_block(self.difficulty)
        self.chain.append(block)
        return block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
            if current_block.hash[:self.difficulty] != "0" * self.difficulty:
                return False
        return True

class BlockchainService:
    def __init__(self):
        self.blockchain = Blockchain()
        self.voted_ids = set()  # Keep track of voters who have already voted

    def create_block(self, voter_id: str, party: str) -> Block:
        """Create a new block for a vote"""
        vote_data = {
            "type": "vote",
            "voter_id": voter_id,
            "party": party,
            "timestamp": time.time()
        }
        latest_block = self.blockchain.get_latest_block()
        block = Block(
            len(self.blockchain.chain),
            time.time(),
            vote_data,
            latest_block.hash
        )
        return block

    def mine_block(self, block: Block) -> None:
        """Mine a block with the current difficulty"""
        block.mine_block(self.blockchain.difficulty)

    def add_block(self, block: Block) -> None:
        """Add a block to the chain"""
        self.blockchain.chain.append(block)
        self.voted_ids.add(block.data["voter_id"])

    def has_voted(self, voter_id: str) -> bool:
        """Check if a voter has already voted"""
        return voter_id in self.voted_ids

    def get_vote_history(self) -> List[Dict[str, Any]]:
        """Get the complete vote history"""
        votes = []
        for block in self.blockchain.chain[1:]:  # Skip genesis block
            if block.data.get("type") == "vote":
                votes.append({
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "data": block.data,
                    "hash": block.hash
                })
        return votes

    def get_vote_by_hash(self, block_hash: str) -> Optional[Dict[str, Any]]:
        """Get a specific vote by its block hash"""
        for block in self.blockchain.chain:
            if block.hash == block_hash:
                return {
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "data": block.data,
                    "hash": block.hash
                }
        return None

    def get_blockchain(self):
        """Get the current state of the blockchain"""
        return {
            'chain': [block.__dict__ for block in self.blockchain.chain],
            'length': len(self.blockchain.chain),
            'pending_transactions': [tx.__dict__ for tx in self.blockchain.pending_transactions],
            'mining_reward': self.blockchain.mining_reward
        } 