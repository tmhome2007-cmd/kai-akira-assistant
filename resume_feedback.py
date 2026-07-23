import streamlit as st
import re
from langchain_groq import ChatGroq

def calculate_approx_match_score(resume_text: str, job_text: str) -> int:
    """
    Berekent een indicatieve ATS match score op basis van unieke relevante trefwoorden.
    Dit is een eenvoudige, niet-wetenschappelijke benadering voor vroege bèta-fases.
    """
    # Eenvoudige extractie van woorden langer dan 3 tekens uit de vacature
    job_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', job_text.lower()))
    
    # Filter algemene veelvoorkomende Engelse 'stopwoorden'
    stopwords = {
        "with", "that", "this", "from", "have", "will", "your", "more", "their", "about",
        "which", "would", "there", "their", "what", "about", "which", "when", "make",
        "can", "like", "time", "just", "know", "take", "people", "into", "year", "your",
        "good", "some", "could", "them", "see", "other", "than", "then", "now", "look",
        "only", "come", "its", "over", "think", "also", "back", "after", "use", "two",
        "how", "our", "work", "first", "well", "way", "even", "new", "want", "because"
    }
    meaningful_job_words = job_words - stopwords

    if not meaningful_job_words:
        return 50 # Fallback als de tekst te kort is

    resume_words_lower = set(re.findall(r'\b[a-zA-Z]{4,}\b', resume_text.lower()))
    
    # Tel hoeveel relevante woorden uit de vacature op het CV staan
    matching_words = meaningful_job_words.intersection(resume_words_lower)
    
    score = int((len(matching_words) / len(meaningful_job_words)) * 100)
    
    # Houd de score binnen een realistisch bereik voor weergave (bijv. tussen 15% en 95%)
    return max(15, min(score, 95))


def generate_resume_feedback(resume_text: str, job_text: str) -> tuple[str, int]:
    """
    Genereert ATS feedback en geeft een tuple terug: (feedback_tekst, match_percentage).
    """
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=st.secrets["GROQ_API_KEY"],
        temperature=0.0
    )

    prompt = f"""
    You are an expert ATS (Applicant Tracking System) reviewer. Analyze the resume against the job description.

    Resume:
    {resume_text}

    Job Description:
    {job_text}

    Provide feedback covering:
    1. ATS KEYWORDS (Missing vs Present)
    2. STRONG BULLET POINTS (How to improve existing ones)
    3. US FORMATTING CHECKS
    """

    try:
        response = llm.invoke(prompt)
        feedback_text = response.content
    except Exception as e:
        feedback_text = f"Error generating ATS feedback: {e}"

    # Bereken de indicatieve match score
    match_score = calculate_approx_match_score(resume_text, job_text)

    return feedback_text, match_score