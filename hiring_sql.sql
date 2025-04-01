use hiring_db_system;

select * from job_application;


CREATE TABLE candidate_details (
    candidate_id VARCHAR(255),
    name VARCHAR(255),
    email VARCHAR(255),
    phone_no INT,
    resume VARCHAR(255)
);

select * from candidate_details;

CREATE TABLE jobs_description (
    job_id INT PRIMARY KEY,
    job_role VARCHAR(255),
    experience VARCHAR(255),
    salary DECIMAL(10, 2),
    location VARCHAR(255),
    job_description VARCHAR(255)
);



INSERT INTO jobs_description (job_id, job_role, experience, salary, location, job_description)
VALUES(1, 'Web Developer', '2-5 years', 70000.00, 'New York', 'uploads/2700.pdf');

INSERT INTO candidate_details (candidate_id, name, email, phone_no, resume)
VALUES
('001', 'John Doe', 'johndoe@example.com', 1234567890, 'uploads/harisha.programmer@gmail.com_resume.pdf');



select * from job_application;

SELECT resume FROM candidate_details WHERE candidate_id =001;

SELECT job_description FROM jobs_description WHERE job_id =1;

select * from users;

select * from jobs_description;


select * from candidate_details;