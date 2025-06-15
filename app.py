import streamlit as st
from pdfminer.high_level import extract_text
import spacy
import requests
from urllib.parse import urlparse

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def extract_job_desc_from_url(url):
    """Extract text from URL (supports LinkedIn, Indeed, etc.)"""
    try:
        if "linkedin.com" in url:
            return "LinkedIn detected - paste the description manually for now"
        response = requests.get(url)
        return response.text[:5000]  # Limit to first 5000 chars
    except:
        return None

def analyze_resume(resume_text, job_desc):
    # Your existing analysis logic
    doc = nlp(job_desc.lower())
    job_kw = {token.text for token in doc if not token.is_stop and token.is_alpha}
    
    doc = nlp(resume_text.lower())
    resume_kw = {token.text for token in doc if not token.is_stop and token.is_alpha}
    
    missing = job_kw - resume_kw
    score = len(resume_kw & job_kw) / len(job_kw) * 100
    return score, missing

# Streamlit UI
st.title("AI Resume Optimizer")

tab1, tab2 = st.tabs(["Text Input", "URL Input"])

with tab1:
    job_desc_text = st.text_area("Paste Job description", height=200)

with tab2:
    job_url = st.text_input("Or enter Job Posting URL")
    if job_url:
        if not urlparse(job_url).scheme:
            st.warning("Please include http:// or https://")
        else:
            job_desc_url = extract_job_desc_from_url(job_url)
            if job_desc_url:
                st.text_area("Extracted Text", job_desc_url, height=200)

uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

if uploaded_file:
    resume_text = extract_text(uploaded_file) if uploaded_file.name.endswith('.pdf') else uploaded_file.getvalue().decode()
    
    if st.button("Analyze"):
        job_desc = job_desc_text if job_desc_text else job_desc_url
        if not job_desc:
            st.error("Please provide either text or URL")
        else:
            score, missing = analyze_resume(resume_text, job_desc)
            st.success(f"Match Score: {score:.1f}%")
            if missing:
                st.write("Missing keywords:", ", ".join(missing))