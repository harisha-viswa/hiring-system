from flask import Flask, request, jsonify
import mysql.connector  # Database connection
import fitz  # PyMuPDF for PDF processing
import spacy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Load SpaCy NLP Model
nlp = spacy.load("en_core_web_sm")

# Predefined skills list (can be improved)
SKILLS_DATABASE = ["python", "javascript", "java", "sql", "firebase", "react", "angular", "machine learning"]

def connect_db():
    """Connect to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@Harisha",
        database="hiring_system"
    )

def fetch_resume_and_job(application_id, job_id):
    """Retrieve resume and job description file paths from the database."""
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT resume_path FROM applications WHERE application_id = %s", (application_id,))
    resume_record = cursor.fetchone()

    cursor.execute("SELECT job_description FROM jobs WHERE job_id = %s", (job_id,))
    job_record = cursor.fetchone()

    conn.close()

    if resume_record and job_record:
        return resume_record["resume_path"], job_record["job_description"]
    else:
        raise ValueError("Resume or Job description not found in database.")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text("text") for page in doc])

def extract_skills(text):
    """Extract skills from text using NLP and predefined skill matching."""
    doc = nlp(text)
    extracted_skills = set()

    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and token.text.lower() in SKILLS_DATABASE:
            extracted_skills.add(token.text.lower())

    return list(extracted_skills)

def compare_skills(job_skills, resume_skills):
    """Compare extracted skills from job description and resume using fuzzy matching."""
    matched_skills = set()

    for skill in resume_skills:
        best_match, score = process.extractOne(skill, job_skills)
        if score > 80:  # Consider it a match if similarity is above 80%
            matched_skills.add(best_match)

    match_score = (len(matched_skills) / max(len(job_skills), 1)) * 100  # Avoid division by zero
    return match_score, matched_skills

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--application_id", type=int, required=True, help="Application ID from the database")
    parser.add_argument("--job_id", type=int, required=True, help="Job ID from the database")
    args = parser.parse_args()

    try:
        resume_path, job_desc_path = fetch_resume_and_job(args.application_id, args.job_id)

        # Extract text from PDFs
        job_text = extract_text_from_pdf(job_desc_path)
        resume_text = extract_text_from_pdf(resume_path)

        # Extract skills
        job_skills = extract_skills(job_text)
        resume_skills = extract_skills(resume_text)

        # Compare skills
        match_score, matched_skills = compare_skills(job_skills, resume_skills)

        # Display results
        print("\n🔹 **Extracted Job Description Skills:**", job_skills)
        print("🔹 **Extracted Resume Skills:**", resume_skills)
        print("\n✅ **Match Score:** {:.2f}%".format(match_score))

        # Selection criteria
        if match_score >= 80:
            print("🎉 ✅ **Candidate Selected!** ✅ 🎉")
        else:
            print("❌ **Candidate Not Selected - Improve Skill Match.** ❌")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
