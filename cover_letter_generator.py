import os
import streamlit as st
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def generate_cover_letter(resume_text: str, job_text: str, company_name: str = "[Company Name]", company_address: str = "[Company Address]") -> str:
    """Generates a structured US-style cover letter using Groq Cloud API."""
    try:
        # Haalt de API-sleutel veilig op uit de Streamlit Cloud Secrets
        llm = ChatGroq(
            model="llama-3.1-8b-instant",  # <-- Dit was "llama3-8b-8192"
            groq_api_key=st.secrets["GROQ_API_KEY"], 
            temperature=0.0
        )
        
        prompt_template = ChatPromptTemplate.from_messages([
           ("system", (
                "You are an expert technical cover letter writer.\n"
                "Output a cover letter that STRICTLY matches this structure. "
                "Do NOT add introductory notes like 'Here is the generated cover letter:'. Start directly with the layout:\n\n"
                "[Candidate Name]\n"
                "[Candidate Phone] * [Candidate Email]\n"
                "[Current Date]\n"
                "{company_name}\n"
                "{company_address}\n\n"
                "Dear {company_name} Hiring Representative,\n\n"
                "[Opening Paragraph]\n\n"
                "[1-2 Body Paragraphs]\n\n"
                "[Closing Paragraph]\n\n"
                "Sincerely,\n"
                "[Candidate Name]\n\n"
                
                "CRITICAL INSTRUCTIONS FOR TRUTH AND INTEGRITY:\n"
                "1. You are ONLY allowed to mention hard skills, tools, and tech stacks (e.g., Tableau, SQL, Python, Excel) if they are explicitly written inside the Candidate Resume text.\n"
                "2. If the Job Posting requires tools (like Tableau or SQL) that are NOT on the resume, you must NEVER claim the candidate has experience with them. Instead, focus entirely on the candidate's actual infrastructure, scripting, or technical support experience as a foundation for learning new systems.\n"
                "3. Extract education, jobs, and history completely dynamically from the resume. Do not fabricate narratives or reuse past examples."
            )),
            ("user", "Candidate Resume:\n### START RESUME ###\n{resume_text}\n### END RESUME ###\n\nJob Posting:\n### START JOB ###\n{job_text}\n### END JOB ###")
        ])
        
        chain = prompt_template | llm
        response = chain.invoke({
            "resume_text": resume_text,
            "job_text": job_text,
            "company_name": company_name,
            "company_address": company_address
        })
        return response.content
    except Exception as e:
        return f"An error occurred: {e}"