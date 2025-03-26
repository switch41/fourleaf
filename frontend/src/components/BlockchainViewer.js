import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './BlockchainViewer.css';

const BlockchainViewer = () => {
    const [blockchainData, setBlockchainData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchBlockchainData();
    }, []);

    const fetchBlockchainData = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get('http://localhost:5000/blockchain', {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (response.data.success) {
                setBlockchainData(response.data.blockchain);
            } else {
                setError('Failed to fetch blockchain data');
            }
        } catch (err) {
            setError('Failed to fetch blockchain data');
            console.error('Error fetching blockchain:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="blockchain-viewer loading">Loading blockchain data...</div>;
    if (error) return <div className="blockchain-viewer error">{error}</div>;
    if (!blockchainData) return <div className="blockchain-viewer">No blockchain data available</div>;

    return (
        <div className="blockchain-viewer">
            <h2>Blockchain Data</h2>
            <div className="blockchain-stats">
                <p>Total Blocks: {blockchainData.length}</p>
            </div>
            <div className="blocks-container">
                {blockchainData.chain.map((block, index) => (
                    <div key={block.hash} className="block-card">
                        <h3>Block #{block.index}</h3>
                        <div className="block-details">
                            <p><strong>Hash:</strong> {block.hash}</p>
                            <p><strong>Previous Hash:</strong> {block.previous_hash}</p>
                            <p><strong>Timestamp:</strong> {new Date(block.timestamp * 1000).toLocaleString()}</p>
                            <p><strong>Nonce:</strong> {block.nonce}</p>
                        </div>
                        <div className="transactions">
                            <h4>Transactions</h4>
                            {block.transactions.map((tx, txIndex) => (
                                <div key={txIndex} className="transaction">
                                    <p><strong>Voter ID:</strong> {tx.voter_id}</p>
                                    <p><strong>Party:</strong> {tx.party}</p>
                                    <p><strong>Time:</strong> {new Date(tx.timestamp * 1000).toLocaleString()}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default BlockchainViewer; 