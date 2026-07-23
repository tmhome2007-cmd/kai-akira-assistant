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

# --- Session State Initialization ---
if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0

# --- Beta & Privacy Notice ---
st.info(
    "⚠️ **Early Beta Notice:** Please don't upload resumes containing sensitive personal data "
    "you're not comfortable processing through an AI tool. Only anonymized metadata "
    "(word counts, pass/fail checks) is logged — no resume or job description text is stored."
)

st.markdown("---")

st.subheader("1. Upload Documents")

uploaded_file = st.file_uploader("Upload your Resume (.pdf or .docx)", type=["pdf", "docx"])
job_text = st.text_area("Paste the Job Description here", height=200)

# Optional fields
generate_cover_letter_flag = st.checkbox("Also generate a cover letter", value=True)
company_name = st.text_input("Company Name (Optional)", value="[Company Name]")
company_address = st.text_input("Company Address (Optional)", value="[Company Address]")

# Calculate & display remaining uses dynamically
remaining = max(0, 3 - st.session_state.generation_count)
st.caption(f"Free generations remaining in this session: **{remaining} / 3**")

if st.button("Generate Analysis"):
    # Check limit first
    if st.session_state.generation_count >= 3:
        st.warning("⛔ **You've used your 3 free samples** — pricing/waitlist info coming soon!")
    elif not uploaded_file:
        st.error("Please upload a resume first.")
    elif not job_text.strip():
        st.error("Please paste a job description first.")
    else:
        # Increment counter IMMEDIATELY upon starting a valid generation attempt
        st.session_state.generation_count += 1

        with st.spinner("Processing files and analyzing with AI..."):
            # 1. Extract text
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_path = temp_file.name

            try:
                resume_text = extract_resume_text(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # 2. ATS Feedback & Match Score
            st.markdown("### 📊 ATS Resume Feedback")
            feedback, match_score = generate_resume_feedback(resume_text, job_text)
            
            st.metric(
                label="Approximate ATS Term Match", 
                value=f"~{match_score}%", 
                help="Early-stage indicator comparing key job description terms with your resume."
            )
            st.caption("ℹ️ *This is an approximate, early-stage keyword overlap score, not a scientific ATS algorithm.*")
            st.write(feedback)

            # 3. Cover Letter
            cover_letter = ""
            if generate_cover_letter_flag:
                st.markdown("### ✉️ Tailored Cover Letter")
                cover_letter = generate_cover_letter(resume_text, job_text, company_name, company_address)
                st.write(cover_letter)
                
                # PII Check
                pii_results = check_for_pii_leak(cover_letter)
                has_email = pii_results.get("emails") or pii_results.get("email", [])
                has_phone = pii_results.get("phones") or pii_results.get("phone", [])
                has_address = pii_results.get("addresses") or pii_results.get("address", [])

                if has_email or has_phone or has_address:
                    st.warning(f"⚠️ **PII Alert in Motivatiebrief:** Mogelijke persoonsgegevens gedetecteerd: {pii_results}")

            # 4. Quality Rubric
            st.markdown("### 🔍 Quality Rubric Report")
            text_to_score = cover_letter if generate_cover_letter_flag else feedback
            rubric_results = score_output_against_rubric(text_to_score, resume_text, job_text, target_word_count=350)
            st.json(rubric_results)

            # 5. Log Metadata
            try:
                log_run(
                    cover_letter_requested=generate_cover_letter_flag,
                    rubric_results=rubric_results
                )
            except Exception:
                pass

            st.success(f"Analysis complete! (Used {st.session_state.generation_count}/3 free generations)")