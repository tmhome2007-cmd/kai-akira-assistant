import re

def score_output_against_rubric(output_text: str, resume_text: str) -> dict:
    """
    Evaluates programmatic integrity by tracking vocabulary matches.
    Updated to prevent flagging capitalized words at the start of sentences.
    """
    resume_lower = resume_text.lower()
    output_lower = output_text.lower()
    
    # Extra filters voor grammatica en template placeholders
    # Voeg de specifieke bedrijfs- en afdelingsnamen toe aan de whitelist in output_validator.py
    common_formatting_words = {
        "dear", "sincerely", "resume", "start", "end", "hiring", "representative",
        "university", "february", "january", "march", "april", "may", "june", "july",
        "august", "september", "october", "november", "december", "street", "name",
        "please", "thank", "while", "although", "intern", "support", "system",
        "administration", "position", "role", "opportunity", "candidate", "application",
        "data", "mining", "reporting", "capabilities", "analytical", "skills",
        "quantitative", "management", "solutions", "project", "team", "experience",
        "excel", "access", "cloud", "network", "security", "here", "additionally", 
        "date", "current", "company", "address", "glasgow", "edinburgh", "leo", "brown",
        "amp", "assurance", "advisory"  # <-- Voeg deze hier handmatig toe
    }
    
    # Zoek naar hoofdletters, maar sluit woorden uit die direct na een punt en spatie komen (begin van een zin)
    # Dit voorkomt dat woorden als "Additionally" of "Here" geflagged worden.
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', output_text)
    
    potential_terms = []
    for sentence in sentences:
        # Match alle capitalized woorden in de zin
        words = re.findall(r'\b[A-Z][a-zA-Z0-9_/.-]*\b', sentence)
        if words:
            # Als het eerste woord van de zin gecapitalized is, negeer het voor de verificatie
            # tenzij het een bekende tool is (maar die filteren we via common_formatting_words of resume check)
            for idx, word in enumerate(words):
                if idx == 0 and sentence.strip().startswith(word):
                    continue
                potential_terms.append(word)

    fabricated_terms = []
    for term in potential_terms:
        term_clean = term.lower().strip()
        if term_clean in common_formatting_words or len(term_clean) <= 2:
            continue
        if term_clean not in resume_lower:
            fabricated_terms.append(term)
            
    no_fabrication = len(fabricated_terms) == 0
    contains_digits = len(re.findall(r'\b\d+\b', output_text)) >= 2
    has_specificity = contains_digits and len(re.findall(r'\b[A-Z][a-zA-Z0-9_/.-]*\b', output_text)) >= 5
    word_count = len(output_text.split())
    correct_length = 210 <= word_count <= 390
    
    forbidden_fillers = ["hard worker", "passionate about", "team player", "think outside the box"]
    found_fillers = [filler for filler in forbidden_fillers if filler in output_lower]
    no_generic_filler = len(found_fillers) == 0

    return {
        "no_fabrication": no_fabrication,
        "has_specificity": has_specificity,
        "correct_length": correct_length,
        "no_generic_filler": no_generic_filler,
        "meta_metrics": {
            "word_count": word_count,
            "flagged_unverified_terms": list(set(fabricated_terms)),
            "detected_fillers": found_fillers
        }
    }

if __name__ == "__main__":
    print("Module output_validator loaded cleanly.")