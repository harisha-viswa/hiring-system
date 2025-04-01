import fitz  # PyMuPDF for PDF extraction
import faiss
import os
import numpy as np
import ollama
from sentence_transformers import SentenceTransformer
import streamlit as st

# Initialize sentence transformer for embeddings
embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to generate embeddings for questions
def embed_questions(questions):
    return embeddings_model.encode(questions, convert_to_numpy=True).astype('float32')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = "".join([page.get_text() + "\n" for page in doc])
        return text.strip()
    except Exception as e:
        return f"Error extracting text from PDF: {e}"

# Function to process FAQs
def process_faqs(text):
    if not text:
        return []

    faqs = text.split("\nQ")  # Look for 'Q' as a question separator
    faq_pairs = []
    
    for faq in faqs:
        parts = faq.split("\nA", 1)  # Look for 'A' as an answer separator
        if len(parts) == 2:
            question = "Q" + parts[0].strip()
            answer = "A" + parts[1].strip()
            faq_pairs.append((question, answer))
    
    return faq_pairs

# Function to create FAISS vector database
def create_faq_index(faq_pairs):
    if not faq_pairs:
        return None, None, None

    questions = [q for q, _ in faq_pairs]

    try:
        question_vectors = embed_questions(questions)
        dim = question_vectors.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(question_vectors)
        return index, questions, faq_pairs
    except Exception as e:
        return None, None, None

# Function to retrieve the most relevant FAQ
def retrieve_faq(question, index, questions, faq_pairs):
    if index is None or not questions or not faq_pairs:
        return None, "Error: FAQ index is not initialized."

    try:
        question_vector = np.array(embed_questions([question])).astype('float32')
        _, indices = index.search(question_vector, 1)

        best_match_index = indices[0][0]

        # Check if index is valid
        if best_match_index < 0 or best_match_index >= len(faq_pairs):
            return None, "I couldn't find a suitable answer for your question."

        return faq_pairs[best_match_index]
    except Exception as e:
        return None, f"Error retrieving FAQ: {e}"

# Function to generate chatbot response using Ollama
def chatbot_response(user_question, index, questions, faq_pairs):
    retrieved_question, retrieved_answer = retrieve_faq(user_question, index, questions, faq_pairs)

    if retrieved_question is None:
        return "Sorry, I couldn't find an answer to your question."
    print("Retrieved FAQ Answer:", retrieved_answer)
    # Force the response to be ONLY the retrieved answer
    return retrieved_answer

    company_name = "Hirely"
    company_email = "hirelycareers@gmail.com"

    prompt = f"""
You are an AI answering job application FAQs for {company_name}.
Answer **only** using the provided FAQ answer. **Do not** add explanations or modify the answer.
Return the response **exactly** as it appears in the FAQ.

FAQ Answer: {retrieved_answer.strip()}
"""



    try:
       response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": prompt}])
       return response["message"]["content"] if "message" in response and "content" in response["message"] else "I'm sorry, I couldn't generate a proper response."
    except Exception as e:
        return f"Error generating response: {e}" 
    
# Load and process FAQs
pdf_path = r"C:/Users/Haarini G/Downloads/Job_Application_FAQ.pdf"  # Provide your PDF path
text = extract_text_from_pdf(pdf_path)
faq_pairs = process_faqs(text)

# Create vector database
index, questions, faq_pairs = create_faq_index(faq_pairs)

st.markdown("""
    <style>
        /* Set the main background color to teal */
        body, .stApp {
            background-color: #008080 !important;
            color: white !important;
        }
        
        /* Set the entire app background to teal */
.stApp {
    background-color: #008080 !important; /* Teal */
}

/* Ensure background behind input text area is also teal */
div[data-testid="stTextInput"] {
    background-color: #008080 !important; /* Teal */
    border-radius: 5px;
}

/* Fix the chat input box at the bottom */
div[data-baseweb="textarea"] {
    background-color: #ffffff !important; /* White input field */
    color: #000000 !important; /* Black text */
    border-radius: 5px;
}


/* Ensure chat bubbles have background */
.stChatMessage {
    background-color: #f0f8ff !important; /* Light teal */
    border-radius: 10px;
    padding: 10px;
}
/* Set text color to black */
.stApp, .stChatMessage, .stChatMessage p {
    color: #000000 !important; /* Black text */
}


        /* Sidebar styling */
        .stSidebar {
            background-color: #f0f8ff !important;
            color: #008080 !important;
        }

        /* Change text color in titles and headers */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
            color: #ffffff !important;  /* White text */
        }

        /* Button styling */
        .stButton > button {
            background-color: #ffffff !important;  /* White button */
            color: #008080 !important;  /* Teal text */
            border-radius: 10px;
            border: none;
            font-weight: bold;
        }

        /* Chat messages */
        .stChatMessage {
            background-color: #f0f8ff !important;  /* Light teal chat bubbles */
            border-radius: 10px;
            padding: 10px;
            color: #008080 !important; /* Teal text */
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit UI
st.title("💬 Hirely - Job Application Chatbot")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input box
user_question = st.chat_input("Ask me anything about job applications...")

if user_question:
    # Display user message
    st.chat_message("user").markdown(user_question)

    # Generate response
    bot_response = chatbot_response(user_question, index, questions, faq_pairs)

    # Display bot response
    with st.chat_message("assistant"):
        st.markdown(bot_response)

    # Save chat history
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

