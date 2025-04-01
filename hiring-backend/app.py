from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_bcrypt import Bcrypt  # type: ignore
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
import pymysql
import os
from werkzeug.utils import secure_filename
from resume_matcher import ResumeMatcher
import random


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
jwt = JWTManager(app)

# Database Connection Function
def get_db_connection():
    try:
        # Connect to MySQL without specifying a database
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="root@Harisha",
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # Create the database if it does not exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS hiring_db_system")
        conn.commit()
        conn.close()

        # Connect to the database after ensuring it exists
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="root@Harisha",
            database="hiring_db_system",
            cursorclass=pymysql.cursors.DictCursor
        )

        return conn
    except pymysql.MySQLError as e:
        print(f"Database connection error: {e}")
        return None


# Register User
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON format"}), 400

    required_fields = ['name', 'email', 'password', 'phone', 'user_type']
    
    # Ensure all fields are present
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    name, email, password, phone, user_type = data['name'], data['email'], data['password'], data['phone'], data['user_type']
    
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = get_db_connection()
    
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            # Check if the users table exists, if not create it
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    user_type VARCHAR(50) NOT NULL
                )
            """)
            conn.commit()

            # Insert user data
            cursor.execute("INSERT INTO users (name, email, password, phone, user_type) VALUES (%s, %s, %s, %s, %s)",
                           (name, email, hashed_pw, phone, user_type))
            conn.commit()

        return jsonify({"message": "User registered successfully"}), 201
    except pymysql.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# Login User
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True, silent=True)
    if not data:
        print("Invalid JSON format received")
        return jsonify({"error": "Invalid JSON format"}), 400

    email = data.get('email')
    password = data.get('password')
    print(f"🔍 Login attempt for email: {email}")
    if not email or not password:
        print("Missing email or password")
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    if conn is None:
        print("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        if user:
            print(f"User found: {user['email']} (Type: {user['user_type']})")
            print(f"Stored Hash: {user['password']}")
            print(f"Entered Password: {password}")
        if user and bcrypt.check_password_hash(user['password'], password):
            access_token = create_access_token(identity={"email": user['email'], "user_type": user['user_type']})
            print("Password matched, login successful")
            return jsonify({"token": access_token, "user_type": user['user_type']}), 200
        print("Invalid credentials")
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route('/create-job', methods=['POST'])
def create_job():
    job_id = random.randint(1000, 9999)
    job_role = request.form['job_role']
    experience = request.form['experience']
    salary = request.form['salary']
    location = request.form['location']
    job_description = request.files['job_description']

    if job_description and job_description.filename.endswith('.pdf'):
        file_path = os.path.join(UPLOAD_FOLDER, f"{job_id}.pdf")
        job_description.save(file_path)
            

    conn = get_db_connection()
    
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500


    with conn.cursor() as cursor:
        # Check if the jobs_description table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs_description (
                job_id INT PRIMARY KEY,
                job_role VARCHAR(255),
                experience VARCHAR(255),
                salary DECIMAL(10, 2),
                location VARCHAR(255),
                job_description VARCHAR(255)
            )
        """)
        conn.commit()

        # Insert user data
        cursor.execute("INSERT INTO jobs_description (job_id, job_role, experience, salary, location, job_description) VALUES (%s, %s, %s, %s, %s, %s)",
                    (job_id, job_role, experience, salary, location, file_path))
        conn.commit()    
    
    return jsonify({"message": "Job created successfully", "job_id": job_id}), 201



@app.route('/get-jobs', methods=['GET'])
def get_jobs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT job_id, job_role, experience, salary, location FROM jobs_description")
    jobs = cursor.fetchall()
    conn.close()
    return jsonify(jobs)


@app.route('/job-description/<int:job_id>', methods=['GET'])
def get_job_description(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT job_description FROM jobs_description WHERE job_id = %s", (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    if job and os.path.exists(job['job_description']):
        return send_file(job['job_description'], as_attachment=True)
    return jsonify({"error": "File not found"}), 404



@app.route('/apply-job', methods=['POST'])
def apply_job():
    data=request.json 
    job_id = data.get('job_id')
    candidate_id = data.get('candidate_id')

    if not all([job_id, candidate_id]):
        return jsonify({"error": "All fields are required"}), 400


    matcher = ResumeMatcher() 
    result = matcher.match_resume(job_id, candidate_id)

    final_score = result.get('final_score')
    
    
    print(f"Final Score: {final_score}")

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        with conn.cursor() as cursor:
            # Check if the jobs_description table exists, if not create it
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_application (
                    job_id INT NOT NULL,
                    candidate_id VARCHAR(50) NOT NULL,
                    final_score VARCHAR(50) 
                )
            """)
            conn.commit()
            # Insert user data
            cursor.execute("""INSERT INTO job_application (job_id, candidate_id, final_score) VALUES (%s, %s, %s)""", (job_id, candidate_id, final_score))
            conn.commit()    
        conn.close()
        return jsonify({"message": "Application submitted successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Send the actual error message

@app.route('/cancel-application', methods=['POST'])
def cancel_application():
    data = request.json
    job_id = data.get('job_id')
    candidate_id = data.get('candidate_id')

    if not all([job_id, candidate_id]):
        return jsonify({"error": "Both job_id and candidate_id are required"}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        with conn.cursor() as cursor:
            # Check if application exists
            cursor.execute("SELECT * FROM job_application WHERE job_id = %s AND candidate_id = %s", (job_id, candidate_id))
            application = cursor.fetchone()

            if not application:
                return jsonify({"error": "Application not found"}), 404

            # Delete the application record
            cursor.execute("DELETE FROM job_application WHERE job_id = %s AND candidate_id = %s", (job_id, candidate_id))
            conn.commit()

        conn.close()
        return jsonify({"message": "Application deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


    
    
@app.route('/candidate-info', methods=['POST'])
def candidate_info():
    
    candidate_id = random.randint(1000, 9999)
    name = request.form['name']
    email = request.form['email']
    phone_no = request.form['phone_no']
    resume = request.files['resume']
    if resume and resume.filename.endswith('.pdf'):
        file_path = os.path.join(UPLOAD_FOLDER, f"{candidate_id}.pdf")
        resume.save(file_path)
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    with conn.cursor() as cursor:
        # Check if the jobs_description table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidate_details (
                candidate_id VARCHAR(50),
                name VARCHAR(255),
                email VARCHAR(255),
                phone_no VARCHAR(255),
                resume VARCHAR(255)
            )
        """)
        conn.commit()
        # Insert user data
        cursor.execute("INSERT INTO candidate_details (candidate_id, name, email, phone_no, resume) VALUES (%s, %s, %s, %s, %s)",(candidate_id, name, email, phone_no, file_path))
        conn.commit()    
    return jsonify({"message": "Candidate details created successfully", "candidate_id": candidate_id}), 201
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)