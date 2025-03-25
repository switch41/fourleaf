import json
import os

class DataService:
    def __init__(self):
        # Dummy dataset for testing
        self.voters = {
            "VOTER001": {
                "id": "VOTER001",
                "name": "John Doe",
                "has_voted": False,
                "party": None
            },
            "VOTER002": {
                "id": "VOTER002",
                "name": "Jane Smith",
                "has_voted": False,
                "party": None
            },
            "VOTER003": {
                "id": "VOTER003",
                "name": "Bob Johnson",
                "has_voted": False,
                "party": None
            }
        }

    def get_voter(self, voter_id):
        return self.voters.get(voter_id)

    def record_vote(self, voter_id, party):
        if voter_id in self.voters:
            self.voters[voter_id]["has_voted"] = True
            self.voters[voter_id]["party"] = party
            return True
        return False

    def get_fingerprint_data(self, voter_id):
        # In a real implementation, this would retrieve fingerprint data from a database
        # For demo purposes, we'll return a dummy value
        return f"DUMMY_FINGERPRINT_{voter_id}"

    def get_face_data(self, voter_id):
        # In a real implementation, this would retrieve face data from a database
        # For demo purposes, we'll return a dummy value
        return f"DUMMY_FACE_{voter_id}"

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"voters": [], "officials": []}

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def verify_official(self, username, password):
        for official in self.data["officials"]:
            if official["username"] == username and official["password"] == password:
                return official
        return None

    def update_voter_status(self, voter_id, has_voted=True):
        for voter in self.data["voters"]:
            if voter["voter_id"] == voter_id:
                voter["has_voted"] = has_voted
                self.save_data()
                return True
        return False 