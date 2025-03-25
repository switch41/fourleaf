import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import VoterVerification from './components/VoterVerification';
import BlockchainViewer from './components/BlockchainViewer';
import axios from 'axios';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on app load
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const handleLogin = (token) => {
    setIsAuthenticated(true);
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
        {isAuthenticated && (
          <header className="App-header">
            <h1>Voter Verification System</h1>
            <nav>
              <button onClick={handleLogout} className="logout-button">Logout</button>
            </nav>
          </header>
        )}
        <Routes>
          <Route 
            path="/login" 
            element={
              isAuthenticated ? 
                <Navigate to="/verify" /> : 
                <Login onLogin={handleLogin} />
            } 
          />
          <Route 
            path="/verify" 
            element={
              isAuthenticated ? 
                <VoterVerification /> : 
                <Navigate to="/login" />
            } 
          />
          <Route 
            path="/blockchain" 
            element={
              isAuthenticated ? 
                <BlockchainViewer /> : 
                <Navigate to="/login" />
            } 
          />
          <Route 
            path="/" 
            element={
              isAuthenticated ? 
                <Navigate to="/verify" /> : 
                <Navigate to="/login" />
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 