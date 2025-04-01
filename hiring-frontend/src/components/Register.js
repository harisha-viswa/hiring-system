import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Register = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '', email: '', password: '', confirmPassword: '', phone: '', user_type: 'candidate'
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setError('');  // Clear error on input change
    };

    const validatePassword = (password) => {
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        return passwordRegex.test(password);
    };

    const validateEmail = (email) => {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@gmail\.com$/;
        return emailRegex.test(email);
    };

    const validatePhone = (phone) => {
        const phoneRegex = /^\d{10}$/;
        return phoneRegex.test(phone);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Basic validation
        if (!formData.name || !formData.email || !formData.password || !formData.confirmPassword || !formData.phone) {
            return setError("All fields are required.");
        }

        if (!validateEmail(formData.email)) {
            return setError("Email must be a valid Gmail address ending with @gmail.com.");
        }

        if (formData.password !== formData.confirmPassword) {
            return setError("Passwords do not match!");
        }

        if (!validatePassword(formData.password)) {
            return setError("Password must be at least 8 characters long, include an uppercase letter, a lowercase letter, a number, and a special character.");
        }

        if (!validatePhone(formData.phone)) {
            return setError("<span style='color: red;'>Phone number must be exactly 10 digits.</span>");
        }

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            console.log("Response:", formData);
            await axios.post("http://127.0.0.1:5000/register", formData);

            setSuccess("User registered successfully!");
            setTimeout(() => navigate("/"), 2000); // Redirect after success
        } catch (error) {
            setError(error.response?.data?.error || "Something went wrong.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-container">
            <h2>Register</h2>
            {error && <p className="error-message" style={{ color: 'red' }}>{error}</p>}
            {success && <p className="success-message">{success}</p>}

            <form onSubmit={handleSubmit}>
                <input type="text" name="name" placeholder="Name" value={formData.name} onChange={handleChange} required />
                <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleChange} required />
                <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} required />
                <input type="password" name="confirmPassword" placeholder="Confirm Password" value={formData.confirmPassword} onChange={handleChange} required />
                <input type="text" name="phone" placeholder="Phone" value={formData.phone} onChange={handleChange} required />
                
                <select name="user_type" value={formData.user_type} onChange={handleChange}>
                    <option value="candidate">Candidate</option>
                    <option value="recruiter">Recruiter</option>
                </select>

                <button type="submit" disabled={loading}>
                    {loading ? "Registering..." : "Register"}
                </button>
            </form>
        </div>
    );
};

export default Register;
