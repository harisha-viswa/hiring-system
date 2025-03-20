from flask import Flask, request, jsonify
import torch
import fitz  # PyMuPDF for PDF processing
import argparse
import mysql.connector  # Database connection
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

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

def load_model():
    """Load the Named Entity Recognition (NER) model."""
    model_name = "dbmdz/bert-large-cased-finetuned-conll03-english"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    nlp_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    return nlp_pipeline

def extract_skills_experience(nlp_pipeline, text):
    """Extract skills and experience using NLP model."""
    entities = nlp_pipeline(text)
    skills = set()
    experience = None
    
    for entity in entities:
        word = entity["word"].replace("##", "")  # Remove subword artifacts
        if len(word) > 2:  # Ignore short words
            if entity["entity_group"] == "MISC":
                skills.add(word.lower())  # Convert skills to lowercase for consistency
            elif entity["entity_group"] == "ORG" and any(char.isdigit() for char in word):
                experience = word
    
    return list(skills), experience

def compare_skills(job_skills, resume_skills):
    """Compare extracted skills from job description and resume."""
    job_skills_set = set(job_skills)
    resume_skills_set = set(resume_skills)
    intersection = job_skills_set.intersection(resume_skills_set)
    score = (len(intersection) / max(len(job_skills_set), 1)) * 100  # Avoid division by zero
    return score, intersection

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--application_id", type=int, required=True, help="Application ID from the database")
    parser.add_argument("--job_id", type=int, required=True, help="Job ID from the database")
    args = parser.parse_args()
    
    try:
        resume_path, job_desc_path = fetch_resume_and_job(args.application_id, args.job_id)
        
        # Extract text from PDFs only
        job_text = extract_text_from_pdf(job_desc_path)
        resume_text = extract_text_from_pdf(resume_path)
        
        # Load NLP model
        nlp_pipeline = load_model()
        
        # Extract skills & experience
        job_skills, job_exp = extract_skills_experience(nlp_pipeline, job_text)
        resume_skills, resume_exp = extract_skills_experience(nlp_pipeline, resume_text)
        
        # Compare skills
        match_score, matched_skills = compare_skills(job_skills, resume_skills)
        
        # Display results
        print("\n🔹 **Extracted Job Description Skills:**", job_skills)
        print("🔹 **Required Experience:**", job_exp)
        print("\n🔹 **Extracted Resume Skills:**", resume_skills)
        print("🔹 **Candidate Experience:**", resume_exp)
        print("\n✅ **Match Score:** {:.2f}%".format(match_score))
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")