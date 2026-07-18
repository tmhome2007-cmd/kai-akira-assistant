import re

def check_metric_grounding(output_text: str, resume_text: str) -> bool:
    """
    Extracts standalone numbers and percentages from output_text and checks
    if they exist anywhere within the resume_text.
    Returns True if ALL metrics are grounded, False if any ungrounded metric is found.
    """
    # Regex om getallen (bijv. 9, 300) en percentages (bijv. 99.5%) te vinden
    # Zoekt naar cijfers, optioneel gevolgd door een % teken of een decimaal getal
    metric_pattern = r'\b\d+(?:\.\d+)?%?\b'
    
    metrics = re.findall(metric_pattern, output_text)
    
    for metric in metrics:
        # Als het getal/percentage niet in het CV staat, hebben we een hallucinatie
        if metric not in resume_text:
            return False
            
    return True

def score_output_against_rubric(output_text: str, resume_text: str, job_text: str, target_word_count: int = 300) -> dict:
    """Scores the generated output against safety, compliance, and length rubrics."""
    
    # --- Bestaande checks (voorbeelden van hoe jouw huidige structuur eruitziet) ---
    # (Pas dit aan zodat dit matcht met jouw exacte huidige variabelen)
    fabrication_guard = True  # Jouw bestaande proper noun check logic hier
    specificity_passed = True
    no_generic_filler = True
    
    # Bereken het aantal woorden
    words = output_text.split()
    total_words = len(words)
    word_count_passed = total_words <= (target_word_count + 50)
    
    # --- Nieuwe Metric Grounding Check ---
    metric_grounding_passed = check_metric_grounding(output_text, resume_text)
    
    # Bepaal welke termen geflagged moeten worden (optioneel, indien nodig voor je UI)
    flagged_terms = []
    if "[Job Posting Source]" in output_text or "[Company Name]" in output_text:
        flagged_terms.append("Placeholders left untamed")
    
    # Retourneer het uitgebreide JSON-achtige woordenboek
    return {
        "Fabrication Guard (Passed)": fabrication_guard,
        "Metric Grounding (Passed)": metric_grounding_passed,  # <-- Nieuwe key
        "Specificity Check (Passed)": specificity_passed,
        "Word Count Bound (Passed)": word_count_passed,
        "No Generic Filler (Passed)": no_generic_filler,
        "Total Words": total_words,
        "Flagged Terms": flagged_terms
    }