from flask import Flask, request, jsonify
import mysql.connector  
import fitz  
import re
import spacy
from fuzzywuzzy import fuzz
import pdfplumber
import argparse
from sentence_transformers import SentenceTransformer, util
import os
class ResumeMatcher:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.model = SentenceTransformer("all-mpnet-base-v2")
        self.skills_database = set([
            "python", "java", "javascript", "c++", "c#", "sql", "firebase", "mongodb",
            "react", "reactjs", "angular", "node.js", "machine learning", "deep learning",
            "artificial intelligence", "data science", "nlp", "pandas", "numpy", "tensorflow",
            "pytorch", "django", "flask", "spring boot", "aws", "azure", "docker", "kubernetes",
            "git", "github", "html", "css", "bootstrap", "tailwind", "typescript"
        ])
    
    def preprocess_text(self, text):
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text) 
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text) 
        return " ".join(text.split()) 
    
    def connect_db(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root@Harisha",
            database="hiring_db_system"
        )
    
    def fetch_resume_and_job(self, job_id, candidate_id):
        
        conn = self.connect_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT resume FROM candidate_details WHERE candidate_id = %s", (candidate_id,))
        resume_record = cursor.fetchone()

        cursor.execute("SELECT job_description FROM jobs_description WHERE job_id = %s", (job_id,))
        job_record = cursor.fetchone()

        conn.close()

        if not resume_record or not job_record:
            return None, None
        
        return resume_record["resume"], job_record["job_description"]
    
    def extract_text_from_pdf(self,pdf_path):
        try:
            doc = fitz.open(pdf_path)
            text = " ".join(page.get_text("text") for page in doc)  # FIXED CALL
            if not text.strip():
                print(f"No text extracted from {pdf_path}")
            return text.strip() or "No text extracted"
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return "Error reading PDF"
    def extract_skills(self, text):
        doc = self.nlp(text)
        extracted_skills = set()

        for token in doc:
            word = token.text.lower()
            if word in self.skills_database:
                extracted_skills.add(word)

        for chunk in doc.noun_chunks:
            phrase = chunk.text.lower()
            if phrase in self.skills_database:
                extracted_skills.add(phrase)

        return list(extracted_skills)
    
    def calculate_similarity(self, text1, text2):
        text1 = self.preprocess_text(text1)
        text2 = self.preprocess_text(text2)
        
        embeddings1 = self.model.encode(text1, convert_to_tensor=True)
        embeddings2 = self.model.encode(text2, convert_to_tensor=True)
        
        similarity_score = util.pytorch_cos_sim(embeddings1, embeddings2).item() * 100
        return similarity_score
    
    def compare_skills(self, job_skills, resume_skills):
        if not job_skills:
            return 0, set()

        matched_skills = set(job_skills) & set(resume_skills)
        match_score = (len(matched_skills) / len(job_skills)) * 100
        return match_score, matched_skills
    
    def match_resume_to_job(self, job_desc, resume_text):
        job_skills = self.extract_skills(job_desc)
        resume_skills = self.extract_skills(resume_text)

        skill_match, matched_skills = self.compare_skills(job_skills, resume_skills)
        content_similarity = self.calculate_similarity(job_desc, resume_text)

        if skill_match == 100:
            final_score = (0.4 * content_similarity) + (0.6 * skill_match)
        elif skill_match >= 90:
            final_score = (0.5 * content_similarity) + (0.5 * skill_match)
        else:
            final_score = (0.6 * content_similarity) + (0.4 * skill_match)

        final_score = min(final_score, 100)

        return final_score, skill_match, content_similarity, matched_skills
    
    def match_resume(self, job_id, candidate_id):
        
        
        print(job_id,candidate_id)
        
        
        job_desc_path,resume_path  = self.fetch_resume_and_job(job_id, candidate_id)
        
        print(job_desc_path,resume_path )
        

        if not resume_path or not job_desc_path:
            return {"error": "Resume or Job description not found in the database."}
        if not os.path.exists(job_desc_path):
            return {"error": f"Job description file not found: {job_desc_path}"}
        if not os.path.exists(resume_path):
            return {"error": f"Resume file not found: {resume_path}"}
        
        job_text = self.extract_text_from_pdf(job_desc_path)
        resume_text = self.extract_text_from_pdf(resume_path)

        final_score, skill_match, content_similarity, matched_skills = self.match_resume_to_job(job_text, resume_text)

        selection = "Candidate Selected" if final_score >= 75 else "Candidate Not Selected"

        result_dict = {
            "candidate_selection": selection,
            "final_score": float("{:.2f}".format(final_score)),
            "content_similarity": float("{:.2f}".format(content_similarity)),
            "skill_match": skill_match,
            "matched_skills": matched_skills
        }

        print(result_dict)
        
        return result_dict
       
