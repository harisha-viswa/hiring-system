import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/CandidatePage.css";
import { useNavigate } from 'react-router-dom';


const CandidatePage = () => {
    const navigate = useNavigate();
    const [jobList, setJobList] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [selectedJobId, setSelectedJobId] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        resume: null
    });

    useEffect(() => {
        axios.get("http://127.0.0.1:5000/get-jobs")
            .then(response => setJobList(response.data))
            .catch(error => console.error("Error fetching jobs:", error));
    }, []);

    const handleApply = (jobId) => {
        setSelectedJobId(jobId);
        setShowForm(true);
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleFileChange = (e) => {
        setFormData({ ...formData, resume: e.target.files[0] });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const applicationData = new FormData();
        applicationData.append("name", formData.name);
        applicationData.append("email", formData.email);
        applicationData.append("phone", formData.phone);
        applicationData.append("resume", formData.resume);
        applicationData.append("job_id", selectedJobId);

        try {
            await axios.post("http://127.0.0.1:5000/apply-job", applicationData, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            alert("Application submitted successfully!");
            setShowForm(false);
        } catch (error) {
            alert("Error submitting application: " + (error.response?.data?.error || error.message));
        }

       
    };
    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user_type');
        navigate('/');

    };

    return (
        <div className="candidate-container">
            <h2>Candidate Dashboard</h2>
            <p>Explore job opportunities and apply!</p>

            <div className="job-list">
                {jobList.map((job) => (
                    <div key={job.job_id} className="job-card">
                        <h3>{job.job_role}</h3>
                        <p><strong>Location:</strong> {job.location}</p>
                        <p><strong>Salary:</strong> {job.salary}</p>
                        <p><strong>Experience:</strong> {job.experience} years</p>
                        <a href={`http://127.0.0.1:5000/job-description/${job.job_id}`} target="_blank" rel="noopener noreferrer">View Description</a>
                        <button onClick={() => handleApply(job.job_id)}>Apply</button>
                    </div>
                ))}
            </div>

            {showForm && (
                <div className="modal">
                    <div className="modal-content">
                        <h3>Apply for Job</h3>
                        <form onSubmit={handleSubmit}>
                            <input type="text" name="name" placeholder="Full Name" onChange={handleChange} required />
                            <input type="email" name="email" placeholder="Email" onChange={handleChange} required />
                            <input type="tel" name="phone" placeholder="Phone Number" onChange={handleChange} required />
                            <input type="file" accept=".pdf" onChange={handleFileChange} required />
                            <button type="submit">Submit Application</button>
                        </form>
                        <button className="close-btn" onClick={() => setShowForm(false)}>Close</button>
                    </div>
                </div>
            )}

            <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
    );
};

export default CandidatePage;
