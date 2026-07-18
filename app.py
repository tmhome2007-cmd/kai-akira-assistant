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

# --- Nieuwe Beta & Privacy Waarschuwing ---
st.info(
    "⚠️ **Early Beta Notice:** Please don't upload resumes containing sensitive personal data "
    "you're not comfortable processing through an AI tool. Only anonymized metadata "
    "(word counts, pass/fail checks) is logged — no resume or job description text is stored."
)

st.markdown("---")

st.subheader("1. Upload Documents")

uploaded_file = st.file_uploader("Upload your Resume (.pdf or .docx)", type=["pdf", "docx"])
job_text = st.text_area("Paste the Target Job Description here:", height=250)
generate_cover_letter_flag = st.checkbox("Also generate a cover letter", value=False)
submit_button = st.button("Generate Analysis", type="primary")

if submit_button:
    if not uploaded_file or not job_text.strip():
        st.error("Missing input parameters. Provide both a file and job description.")
    else:
        with st.spinner("Processing with local pipeline..."):
            try:
                # 1. Tijdelijk bestand opslaan en uitlezen
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
                    temp_file.write(uploaded_file.read())
                    temp_file_path = temp_file.name

                resume_text = extract_resume_text(temp_file_path)
                os.remove(temp_file_path)

                # Bereid de basis-metadata voor de run logging voor
                log_meta = {
                    "cover_letter_requested": generate_cover_letter_flag,
                    "rubric_passed": False,
                    "total_words": 0,
                    "fabrication_guard_passed": False,
                    "specificity_passed": False,
                    "no_generic_filler_passed": False
                }

                # 2. ATS Feedback genereren
                st.markdown("### 📊 ATS Resume Feedback")
                feedback_output = generate_resume_feedback(resume_text, job_text)
                st.markdown(feedback_output)
                
                # Check feedback op PII-lekken
                pii_feedback = check_for_pii_leak(feedback_output)
                if pii_feedback["pii_detected"]:
                    st.warning(f"⚠️ **PII Alert in Feedback:** Mogelijke persoonsgegevens gedetecteerd: {pii_feedback['details']}")
                
                st.markdown("---")

                # 3. optioneel: Motivatiebrief genereren
                if generate_cover_letter_flag:
                    st.markdown("### ✉️ Tailored Cover Letter")
                    cover_letter_output = generate_cover_letter(resume_text, job_text)
                    st.markdown(cover_letter_output)
                    
                    # Check motivatiebrief op PII-lekken
                    pii_cl = check_for_pii_leak(cover_letter_output)
                    if pii_cl["pii_detected"]:
                        st.warning(f"⚠️ **PII Alert in Motivatiebrief:** Mogelijke persoonsgegevens gedetecteerd: {pii_cl['details']}")
                    
                    # 4. Kwaliteitscontrole uitvoeren
                    with st.expander("🔍 Quality Rubric Report"):
                        report = score_output_against_rubric(cover_letter_output, resume_text)
                        
                        rubric_passed = (
                            report["no_fabrication"] and 
                            report["has_specificity"] and 
                            report["correct_length"] and 
                            report["no_generic_filler"]
                        )
                        
                        st.json({
                            "Fabrication Guard (Passed)": report["no_fabrication"],
                            "Specificity Check (Passed)": report["has_specificity"],
                            "Word Count Bound (Passed)": report["correct_length"],
                            "No Generic Filler (Passed)": report["no_generic_filler"],
                            "Total Words": report["meta_metrics"]["word_count"],
                            "Flagged Terms": report["meta_metrics"]["flagged_unverified_terms"]
                        })
                        
                        # Update de loggegevens op basis van de rubric-uitslag
                        log_meta["rubric_passed"] = rubric_passed
                        log_meta["total_words"] = report["meta_metrics"]["word_count"]
                        log_meta["fabrication_guard_passed"] = report["no_fabrication"]
                        log_meta["specificity_passed"] = report["has_specificity"]
                        log_meta["no_generic_filler_passed"] = report["no_generic_filler"]

                # 5. Log de run anoniem naar run_log.jsonl
                log_run(log_meta)
                st.success("Analysis complete! Session metadata successfully logged.")

            except Exception as e:
                st.error(f"Execution failed: {e}")