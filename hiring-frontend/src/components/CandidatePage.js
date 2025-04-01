import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/CandidatePage.css";
import { useNavigate } from 'react-router-dom';
import { MessageCircle } from 'lucide-react';

const CandidatePage = () => {
    const navigate = useNavigate();
    const [jobList, setJobList] = useState([]);
    const [appliedJobs, setAppliedJobs] = useState(new Set());
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        resume: null
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        // Fetch job listings
        axios.get("http://127.0.0.1:5000/get-jobs")
            .then(response => setJobList(response.data))
            .catch(error => console.error("Error fetching jobs:", error));

        // Fetch applied jobs for the logged-in candidate
        axios.get("http://127.0.0.1:5000/get-applied-jobs", {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
        })
        .then(response => {
            setAppliedJobs(new Set(response.data.applied_jobs));
        })
        .catch(error => console.error("Error fetching applied jobs:", error));

    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleFileChange = (e) => {
        setFormData({ ...formData, resume: e.target.files[0] });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true); // Set submitting state to true
        const applicationData = new FormData();
        applicationData.append("name", formData.name);
        applicationData.append("email", formData.email);
        applicationData.append("phone_no", formData.phone_no);
        applicationData.append("resume", formData.resume);

        try {
            // Send candidate info to the backend
            const response =await axios.post("http://127.0.0.1:5000/candidate-info", applicationData, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            if (response.data.candidate_id) {
                localStorage.setItem("candidate_id", response.data.candidate_id); // ✅ Store candidate_id after submission
                console.log("Candidate ID stored:", response.data.candidate_id);
            } else {
                console.error("Candidate ID not returned by backend.");
            }

            alert("Candidate info updated successfully!");

            // Close the form after submission
            setShowForm(false);
        } catch (error) {
            alert("Error submitting application: " + (error.response?.data?.error || error.message));
        } finally {
            setIsSubmitting(false); // Reset submitting state
        }
    };

    const handleApply = async (jobId) => {
        let candidateId = localStorage.getItem("candidate_id");
    
        if (!candidateId) {
            alert("Candidate ID not found. Please update your candidate info first.");
            return;
        }
    
        console.log("Applying for Job ID:", jobId);
        console.log("Candidate ID:", candidateId);
    
        try {
            const response = await axios.post("http://127.0.0.1:5000/apply-job", {
                job_id: jobId,
                candidate_id: candidateId
            });
    
            if (response.data.error) {
                alert(response.data.error);
            } else {
                alert("Application submitted successfully!");
                setAppliedJobs(new Set([...appliedJobs, jobId])); // Mark job as applied
            }
        } catch (error) {
            alert("Error applying for job: " + (error.response?.data?.error || error.message));
        }
    };
    
    const handleCancelApplication = async (jobId) => {
        let candidateId = localStorage.getItem("candidate_id");
    
        if (!candidateId) {
            alert("Candidate ID not found. Please update your candidate info first.");
            return;
        }
    
        console.log("Cancelling application for Job ID:", jobId);
        console.log("Candidate ID:", candidateId);
    
        try {
            const response = await axios.post("http://127.0.0.1:5000/cancel-application", {
                job_id: jobId,
                candidate_id: candidateId
            });
    
            if (response.data.error) {
                alert(response.data.error);
            } else {
                alert("Application cancelled successfully!");
                const updatedJobs = new Set(appliedJobs);
                updatedJobs.delete(jobId);
                setAppliedJobs(updatedJobs); // Remove job from applied list
            }
        } catch (error) {
            alert("Error cancelling application: " + (error.response?.data?.error || error.message));
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

            <button className="candidate-info-btn" onClick={() => setShowForm(true)}>
                Candidate Info
            </button>

            <div className="job-list">
                {jobList.map((job) => (
                    <div key={job.job_id} className="job-card">
                        <h3>{job.job_role}</h3>
                        <p><strong>Location:</strong> {job.location}</p>
                        <p><strong>Salary:</strong> {job.salary}</p>
                        <p><strong>Experience:</strong> {job.experience} years</p>
                        <a href={`http://127.0.0.1:5000/job-description/${job.job_id}`} target="_blank" rel="noopener noreferrer">View Description</a>
                        {appliedJobs.has(job.job_id) ? (
                            <button className="applied-btn" disabled>Applied</button>
                        ) : (
                            <>
                            <button onClick={() => handleApply(job.job_id)}>Apply</button>
                            
                            </>
                        )}
                        <button onClick={() => handleCancelApplication(job.job_id)}>Revoke</button>
                    </div>
                ))}
            </div>

            {showForm && (
                <div className="modal">
                    <div className="modal-content">
                        <h3>Update Candidate Info</h3>
                        <form onSubmit={handleSubmit}>
                            <input 
                                type="text" 
                                name="name" 
                                placeholder="Full Name" 
                                onChange={handleChange} 
                                required 
                            />
                            <input 
                                type="email" 
                                name="email" 
                                placeholder="Email" 
                                onChange={handleChange} 
                                required 
                            />
                            <input 
                                type="tel" 
                                name="phone_no" 
                                placeholder="Phone Number" 
                                onChange={handleChange} 
                                required 
                            />
                            <input 
                                type="file" 
                                accept=".pdf" 
                                onChange={handleFileChange} 
                                required 
                            />
                            <button type="submit" disabled={isSubmitting}>
                                {isSubmitting ? "Submitting..." : "Submit Info"}
                            </button>
                        </form>
                        <button className="close-btn" onClick={() => setShowForm(false)}>Close</button>
                    </div>
                </div>
            )}

            <button className="logout-btn" onClick={handleLogout}>Logout</button>

            <button className="chatbot-icon" title="Chat with us!">
                <MessageCircle size={24} color="white" />
            </button>
        </div>
    );
};

export default CandidatePage;
