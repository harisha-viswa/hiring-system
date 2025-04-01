// Adding imports
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import CandidatePage from './components/CandidatePage';
import RecruiterPage from './components/RecruiterPage';
import Navbar from "./components/Navbar";

const App = () => {
    return (
        <div>
            <Navbar /> {/* Navbar stays outside Routes to appear on all pages */}
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/candidate" element={<CandidatePage />} />
                <Route path="/recruiter" element={<RecruiterPage />} />
            </Routes>
        </div>
    );
};

export default App;

