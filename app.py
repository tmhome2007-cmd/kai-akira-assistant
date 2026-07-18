import streamlit as st
import os
import tempfile

from resume_extractor import extract_resume_text
from resume_feedback import generate_resume_feedback
from cover_letter_generator import generate_cover_letter
from output_validator import score_output_against_rubric
from utils import log_run, check_for_pii_leak

st.title("Kai Akira — Resume & Cover Letter Assistant")
st.caption("ATS-aware resume and cover letter tailoring. No guarantees, no hype — just faster, sharper applications.")

# --- Beta & Privacy Waarschuwing ---
st.info(
    "⚠️ **Early Beta Notice:** Please don't upload resumes containing sensitive personal data "
    "you're not comfortable processing through an AI tool. Only anonymized metadata "
    "(word counts, pass/fail checks) is logged — no resume or job description text is stored."
)

st.markdown("---")

st.subheader("1. Upload Documents")

uploaded_file = st.file_uploader("Upload your Resume (.pdf or .docx)", type=["pdf", "docx"])
job_text = st.text_area("Paste the Job Description here", height=200)

# Optionele velden voor de brief layout
generate_cover_letter_flag = st.checkbox("Also generate a cover letter", value=True)
company_name = st.text_input("Company Name (Optional)", value="[Company Name]")
company_address = st.text_input("Company Address (Optional)", value="[Company Address]")

if st.button("Generate Analysis"):
    if not uploaded_file:
        st.error("Please upload a resume first.")
    elif not job_text.strip():
        st.error("Please paste a job description first.")
    else:
        with st.spinner("Processing files and analyzing with AI..."):
            # 1. Extraheer de tekst uit het geüploade bestand
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_path = temp_file.name

            try:
                resume_text = extract_resume_text(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # 2. Genereer ATS Feedback
            st.markdown("### 📊 ATS Resume Feedback")
            feedback = generate_resume_feedback(resume_text, job_text)
            st.write(feedback)

            # 3. Genereer Motivatiebrief indien aangevinkt
            cover_letter = ""
            if generate_cover_letter_flag:
                st.markdown("### ✉️ Tailored Cover Letter")
                cover_letter = generate_cover_letter(resume_text, job_text, company_name, company_address)
                st.write(cover_letter)
                
                # Check direct op PII lekken in de brief
                pii_results = check_for_pii_leak(cover_letter)
                if pii_results["emails"] or pii_results["phones"] or pii_results["addresses"]:
                    st.warning(f"⚠️ **PII Alert in Motivatiebrief:** Mogelijke persoonsgegevens gedetecteerd: {pii_results}")

            # 4. Kwaliteitscontrole (Hier hebben we nu job_text correct toegevoegd!)
            st.markdown("### 🔍 Quality Rubric Report")
            text_to_score = cover_letter if generate_cover_letter_flag else feedback
            rubric_results = score_output_against_rubric(text_to_score, resume_text, job_text)
            st.json(rubric_results)

            # 5. Log de metadata anoniem
            log_run(
                cover_letter_requested=generate_cover_letter_flag,
                rubric_results=rubric_results,
                raw_resume_text=resume_text,
                raw_job_text=job_text
            )

            st.success("Analysis complete! Session metadata successfully logged.")