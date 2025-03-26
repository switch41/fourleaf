import hashlib
import json
import time
from typing import List, Dict, Any, Optional

class Block:
    def __init__(self, index: int, transactions: List[Dict[str, Any]], timestamp: float, previous_hash: str):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0  # Initialize nonce first
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int = 4) -> None:
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.difficulty = 2

    def create_genesis_block(self) -> None:
        genesis_block = Block(0, [], time.time(), "0")
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, block: Block) -> None:
        self.chain.append(block)

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
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
        self.blockchain.create_genesis_block()
        # Add some demo data
        self.create_demo_data()

    def create_demo_data(self):
        # Add some demo votes
        demo_votes = [
            {"voter_id": "RDV6404990", "party": "Party A"},
            {"voter_id": "KUSHAL001", "party": "Party B"},
            {"voter_id": "DEMO001", "party": "Party C"}
        ]
        
        for vote in demo_votes:
            block = self.create_block(vote["voter_id"], vote["party"])
            self.mine_block(block)
            self.add_block(block)

    def create_block(self, voter_id: str, party: str) -> Block:
        transactions = [{
            'voter_id': voter_id,
            'party': party,
            'timestamp': time.time()
        }]
        
        previous_block = self.blockchain.get_latest_block()
        return Block(
            index=previous_block.index + 1,
            transactions=transactions,
            timestamp=time.time(),
            previous_hash=previous_block.hash
        )

    def mine_block(self, block: Block) -> None:
        block.mine_block(difficulty=2)  # Lower difficulty for demo

    def add_block(self, block: Block) -> None:
        self.blockchain.add_block(block)

    def has_voted(self, voter_id: str) -> bool:
        for block in self.blockchain.chain[1:]:  # Skip genesis block
            for transaction in block.transactions:
                if transaction['voter_id'] == voter_id:
                    return True
        return False

    def get_vote_history(self) -> List[Dict[str, Any]]:
        votes = []
        for block in self.blockchain.chain[1:]:  # Skip genesis block
            for transaction in block.transactions:
                votes.append({
                    'voter_id': transaction['voter_id'],
                    'party': transaction['party'],
                    'timestamp': transaction['timestamp'],
                    'block_hash': block.hash
                })
        return votes

    def get_vote_by_hash(self, block_hash: str) -> Optional[Dict[str, Any]]:
        for block in self.blockchain.chain:
            if block.hash == block_hash:
                return {
                    'transactions': block.transactions,
                    'timestamp': block.timestamp,
                    'hash': block.hash
                }
        return None

    def get_blockchain(self):
        return {
            'chain': [{
                'index': block.index,
                'transactions': block.transactions,
                'timestamp': block.timestamp,
                'hash': block.hash,
                'previous_hash': block.previous_hash,
                'nonce': block.nonce
            } for block in self.blockchain.chain],
            'length': len(self.blockchain.chain)
        } 