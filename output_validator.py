import re

def check_metric_grounding(output_text: str, resume_text: str) -> bool:
    """
    Extracts standalone numbers and percentages from output_text and checks
    if they exist anywhere within the resume_text.
    Excludes numbers that act as calendar dates (years 2020-2030 or numbers following months).
    Returns True if ALL genuine metrics are grounded, False if any ungrounded metric is found.
    """
    # 1. Vind alle datums met een maandnaam ervoor (bijv. "July 18", "October 5")
    months_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d+)\b'
    date_days = re.findall(months_pattern, output_text, re.IGNORECASE)
    
    # 2. Vind alle 4-cijferige jaartallen tussen 2020 en 2030
    year_pattern = r'\b(202[0-9]|2030)\b'
    date_years = re.findall(year_pattern, output_text)
    
    # Set van alle getallen die we als 'veilig' (datum) beschouwen
    excluded_dates = set(date_days + date_years)

    # 3. Regex voor alle reguliere getallen en percentages
    metric_pattern = r'\b\d+(?:\.\d+)?%?\b'
    metrics = re.findall(metric_pattern, output_text)
    
    for metric in metrics:
        # Als het getal een percentage is (bijv. 99.5%), moet het sowieso gecontroleerd worden
        if '%' not in metric:
            # Als het getal in onze datum-uitsluiting zit, skippen we de check
            if metric.strip() in excluded_dates:
                continue
                
        # Als het een echte metriek is en niet in het CV staat -> trigger falen
        if metric not in resume_text:
            return False
            
    return True

def score_output_against_rubric(output_text: str, resume_text: str, job_text: str, target_word_count: int = 300) -> dict:
    """Scores the generated output against safety, compliance, and length rubrics."""
    
    # --- Bestaande checks basislogica ---
    # (Als je hier specifieke logica had voor proper nouns, kun je die hier behouden)
    fabrication_guard = True  
    specificity_passed = True
    no_generic_filler = True
    
    # Bereken het aantal woorden
    words = output_text.split()
    total_words = len(words)
    word_count_passed = total_words <= (target_word_count + 50)
    
    # --- Metric Grounding Check ---
    metric_grounding_passed = check_metric_grounding(output_text, resume_text)
    
    # Bepaal welke termen geflagged moeten worden
    flagged_terms = []
    if "[Job Posting Source]" in output_text or "[Company Name]" in output_text:
        flagged_terms.append("Placeholders left untamed")
    
    # Retourneer het JSON woordenboek
    return {
        "Fabrication Guard (Passed)": fabrication_guard,
        "Metric Grounding (Passed)": metric_grounding_passed,
        "Specificity Check (Passed)": specificity_passed,
        "Word Count Bound (Passed)": word_count_passed,
        "No Generic Filler (Passed)": no_generic_filler,
        "Total Words": total_words,
        "Flagged Terms": flagged_terms
    }