from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_bcrypt import Bcrypt  # type: ignore
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
import pymysql
import os
import random


#library are updated

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
        return pymysql.connect(
            host="localhost",
            user="root",
            password="root@Harisha",
            database="hiring_system",
            cursorclass=pymysql.cursors.DictCursor
        )
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
        return jsonify({"error": "Invalid JSON format"}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user['password'], password):
            access_token = create_access_token(identity={"email": user['email'], "user_type": user['user_type']})
            return jsonify({"token": access_token, "user_type": user['user_type']}), 200

        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
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
    job_desc = request.files['job_description']

    if job_desc and job_desc.filename.endswith('.pdf'):
        file_path = os.path.join(UPLOAD_FOLDER, f"{job_id}.pdf")
        job_desc.save(file_path)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO jobs (job_id, job_role, experience, salary, location, job_description) VALUES (%s, %s, %s, %s, %s, %s)",
                   (job_id, job_role, experience, salary, location, file_path))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Job created successfully", "job_id": job_id}), 201

@app.route('/get-jobs', methods=['GET'])
def get_jobs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT job_id, job_role, experience, salary, location FROM jobs")
    jobs = cursor.fetchall()
    conn.close()
    return jsonify(jobs)

@app.route('/job-description/<int:job_id>', methods=['GET'])
def get_job_description(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT job_description FROM jobs WHERE job_id = %s", (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    if job and os.path.exists(job['job_description']):
        return send_file(job['job_description'], as_attachment=True)
    return jsonify({"error": "File not found"}), 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
