import React from 'react';
import { useNavigate } from 'react-router-dom';

const CandidatePage = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user_type');
        navigate('/');
    };

    return (
        <div className="dashboard">
            <h2>Candidate Dashboard</h2>
            <p>Welcome, Candidate! You can apply for jobs here.</p>
            <button onClick={handleLogout}>Logout</button>
        </div>
    );
};

export default CandidatePage;
