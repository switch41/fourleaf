import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

const Login = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        try {
            const response = await axios.post('http://localhost:5000/login', {
                username,
                password
            });
            
            if (response.data.token) {
                // Store token in localStorage
                localStorage.setItem('token', response.data.token);
                
                // Set default authorization header for all future requests
                axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
                
                // Call the onLogin callback with the token
                onLogin(response.data.token);
            } else {
                setError('Invalid response from server');
            }
        } catch (err) {
            console.error('Login error:', err);
            setError(err.response?.data?.error || 'Login failed. Please try again.');
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>Voter Verification System</h2>
                <p className="login-subtitle">Please login to continue</p>
                {error && <div className="error-message">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username">Username:</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            placeholder="Enter your username"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password:</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="Enter your password"
                        />
                    </div>
                    <button type="submit">Login</button>
                </form>
                <div className="login-info">
                    <p>Demo Credentials:</p>
                    <p>Username: admin</p>
                    <p>Password: admin123</p>
                </div>
            </div>
        </div>
    );
};

export default Login; 