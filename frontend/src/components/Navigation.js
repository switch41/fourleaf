import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navigation.css';

const Navigation = () => {
    const navigate = useNavigate();
    const isAuthenticated = !!localStorage.getItem('token');

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    if (!isAuthenticated) return null;

    return (
        <nav className="navigation">
            <div className="nav-brand">
                <Link to="/verify">Voter Verification System</Link>
            </div>
            <div className="nav-links">
                <Link to="/verify">Verify Voter</Link>
                <Link to="/blockchain">View Blockchain</Link>
                <button onClick={handleLogout} className="logout-button">
                    Logout
                </button>
            </div>
        </nav>
    );
};

export default Navigation; 