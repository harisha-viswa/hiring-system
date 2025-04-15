import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/Recruiter.css';


const RecruiterPage = () => {
    const navigate = useNavigate();
    const [showForm, setShowForm] = useState(false);
    const [jobList, setJobList] = useState([]);
    const [formData, setFormData] = useState({
        job_role: '',
        experience: '',
        salary: '',
        location: '',
        job_description: null
    });
    const [applicants, setApplicants] = useState([]);
    const [selectedJobId, setSelectedJobId] = useState(null);
    useEffect(() => {
        axios.get("http://127.0.0.1:5000/get-jobs")
            .then(response => setJobList(response.data))
            .catch(error => console.error("Error fetching jobs:", error));
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user_type');
        navigate('/');
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file && file.size > 20 * 1024 * 1024) {  // 20MB limit
            alert("File size must be less than 20MB.");
            return;
        }
        setFormData({ ...formData, job_description: file });
    };
    const handleViewApplicants = async (job_id) => {
        try {
            const response = await axios.post("http://127.0.0.1:5000/get-applicants", {
                job_id: job_id
            });
            console.log("Applicants fetched:", response.data);
            setApplicants(response.data);
            setSelectedJobId(job_id);
        } catch (error) {
            console.error("Full error object:", error);
            alert("Error fetching applicants: " + (error.response?.data?.error || error.message || "Unknown error"));
        }
    };
    const handleSelect = (applicantId) => {
        console.log(`Applicant ${applicantId} selected`);
        // You can also make a POST/PUT request to your backend here to update status
      };
      
      const handleNotSelect = (applicantId) => {
        console.log(`Applicant ${applicantId} not selected`);
        // Same idea, send update to backend
      };
      

    const handleSubmit = async (e) => {
        e.preventDefault();

        const formDataToSend = new FormData();
        formDataToSend.append("job_role", formData.job_role);
        formDataToSend.append("experience", formData.experience);
        formDataToSend.append("salary", formData.salary);
        formDataToSend.append("location", formData.location);
        formDataToSend.append("job_description", formData.job_description);

        try {
            await axios.post("http://127.0.0.1:5000/create-job", formDataToSend, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            alert("Job Created Successfully!");

            const response = await axios.get("http://127.0.0.1:5000/get-jobs");
            setJobList(response.data);

            setShowForm(false);
            setFormData({ job_role: '', experience: '', salary: '', location: '', job_description: null });
        } catch (error) {
            alert("Error creating job: " + (error.response?.data?.error || error.message));
        }
    };

    return (
        <>
            <h2>Recruiter Dashboard</h2>
            <p className='heading'>Welcome, Recruiter! You can post job listings here.</p>
            <div className="parent-container">
                <button className="create_new_job" onClick={() => setShowForm(true)}>Create New Job</button>
                <button className='logout' onClick={handleLogout}>Logout</button>
            </div>
           

            {showForm && (
                <div className="modal">
                    <div className="modal-content">
                        <h3>Create Job</h3>
                        <form onSubmit={handleSubmit}>
                            <input type="text" name="job_role" placeholder="Job Role" onChange={handleChange} required />
                            <input type="number" name="experience" placeholder="Years of Experience" onChange={handleChange} required />
                            <input type="number" name="salary" placeholder="Salary" onChange={handleChange} required />
                            <input type="text" name="location" placeholder="Location" onChange={handleChange} required />
                            <input type="file" accept="application/pdf" onChange={handleFileChange} required />
                            <button type="submit">Submit</button>
                        </form>
                        <button onClick={() => setShowForm(false)}>Close</button>
                    </div>
                </div>
            )}

            <h3 >Job Listings</h3>
            <div className="job-listings">
                {jobList.map((job) => (
                    <div key={job.job_id} className="job-card">
                        <h4>{job.job_role}</h4>
                        <p><strong>Location:</strong> {job.location}</p>
                        <p><strong>Salary:</strong> {job.salary}</p>
                        <p><strong>Experience:</strong> {job.experience} years</p>
                        <a href={`http://127.0.0.1:5000/job-description/${job.job_id}`} target="_blank" rel="noopener noreferrer">
                            View Job Description
                        </a>
                        <button onClick={() => handleViewApplicants(job.job_id)}>View Applicants</button>
                    </div>
                ))}

            </div>
            <div className="recruiter-page">
            {selectedJobId && (
        <div className="overlay">
        <div className="applicant-list">
        <button className="close-button" onClick={() => setSelectedJobId(null)}>X</button>
        <h3>Applicants for Job ID: {selectedJobId}</h3>
        {applicants.length > 0 ? (
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>phone_no</th>
                        <th>Resume</th>
                        <th>Final Score</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                {applicants.map((applicant, index) => {
                    console.log("Resume path:", applicant.resume); // ✅ Log resume path here

                    return (
                    <tr key={index}>
                        <td>{applicant.name}</td>
                        <td>{applicant.email}</td>
                        <td>{applicant.phone_no}</td>
                        <td>
                            <a
                                href={`http://localhost:5000/download-resume/${applicant.resume.replace(/^.*[\\/]/, '')}`}
                                download
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Download Resume
                            </a>
                        </td>
                        <td>{applicant.final_score}</td>
                        <td>
                            <div className='button-group'>
                            <button
                            onClick={() => handleSelect(applicant.id)}
                            className="selected-btn"
                            >
                            Selected
                            </button>
                            <button
                            onClick={() => handleNotSelect(applicant.id)}
                            className="not-selected-btn"
                            >
                            Not Selected
                            </button>
                            </div>
                        </td>
                    </tr>
                    );
                })}
                </tbody>

            </table>
        ) : (
            <p>No applicants found for this job.</p>
        )}
        
        </div>
    </div>
        )}
     </div>
        </>
    );
};

export default RecruiterPage;
