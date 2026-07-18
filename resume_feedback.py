import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def generate_resume_feedback(resume_text: str, job_text: str) -> str:
    """Generates analytical feedback on missing parameters using Groq Cloud API."""
    try:
        # Haalt de API-sleutel veilig op uit de Streamlit Cloud Secrets
        llm = ChatGroq(
            model="llama3-8b-8192", 
            groq_api_key=st.secrets["GROQ_API_KEY"], 
            temperature=0.0
        )
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert AI Career Coach and ATS specialist. "
                "Compare the candidate's resume with the job description and provide feedback.\n"
                "CRITICAL: When rewriting bullet points, you MUST ONLY use technologies and skills "
                "already explicitly written in the user's resume. Never assume or add skills like Tableau, "
                "SQL, or Python unless they are already present in the source text.\n\n"
                "Use ONLY these three headers for your output:\n\n"
                "### ATS KEYWORDS\n\n"
                "### STRONG BULLET POINTS\n\n"
                "### US FORMATTING CHECKS"
            )),
            ("user", (
                "Resume:\n{resume_text}\n\nJob Description:\n{job_text}"
            ))
        ])
        
        chain = prompt_template | llm
        response = chain.invoke({"resume_text": resume_text, "job_text": job_text})
        return response.content  # Groq geeft een ChatMessage object terug, we pakken de .content
    except Exception as e:
        return f"Error connecting to Groq Cloud API: {e}"