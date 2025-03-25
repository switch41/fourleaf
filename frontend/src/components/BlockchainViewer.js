import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './BlockchainViewer.css';

const BlockchainViewer = () => {
  const [votes, setVotes] = useState([]);
  const [selectedVote, setSelectedVote] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchVoteHistory();
  }, []);

  const fetchVoteHistory = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/blockchain/votes', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setVotes(response.data.votes);
      setError('');
    } catch (err) {
      setError('Failed to fetch vote history');
      console.error('Error fetching votes:', err);
    } finally {
      setLoading(false);
    }
  };

  const viewVoteDetails = async (blockHash) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:5000/blockchain/vote/${blockHash}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedVote(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch vote details');
      console.error('Error fetching vote details:', err);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  return (
    <div className="blockchain-viewer">
      <h2>Blockchain Vote History</h2>
      
      {loading && <div className="loading">Loading vote history...</div>}
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="votes-list">
        {votes.map((vote) => (
          <div key={vote.hash} className="vote-card">
            <div className="vote-header">
              <h3>Block #{vote.index}</h3>
              <span className="timestamp">{formatTimestamp(vote.timestamp)}</span>
            </div>
            <div className="vote-details">
              <p><strong>Voter ID:</strong> {vote.voter_id}</p>
              <p><strong>Party:</strong> {vote.party}</p>
              <p className="hash"><strong>Block Hash:</strong> {vote.hash}</p>
            </div>
            <button 
              onClick={() => viewVoteDetails(vote.hash)}
              className="view-details-button"
            >
              View Details
            </button>
          </div>
        ))}
      </div>

      {selectedVote && (
        <div className="vote-modal">
          <div className="modal-content">
            <h3>Vote Details</h3>
            <div className="modal-details">
              <p><strong>Block Index:</strong> {selectedVote.index}</p>
              <p><strong>Timestamp:</strong> {formatTimestamp(selectedVote.timestamp)}</p>
              <p><strong>Voter ID:</strong> {selectedVote.data.voter_id}</p>
              <p><strong>Party:</strong> {selectedVote.data.party}</p>
              <p className="hash"><strong>Block Hash:</strong> {selectedVote.hash}</p>
            </div>
            <button 
              onClick={() => setSelectedVote(null)}
              className="close-button"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default BlockchainViewer; 