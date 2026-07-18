import json
import os
import re
from datetime import datetime

# --- 1. Log Run (Metadata Logger) ---
def log_run(meta: dict, log_filename: str = "run_log.jsonl") -> None:
    """
    Appends a JSON line to a local file with run metadata, including a timestamp.
    Explicitly filters out raw resume or job description texts.
    """
    # Definieer de toegestane veilige sleutels om lekken van ruwe tekst te voorkomen
    safe_keys = {
        "cover_letter_requested", 
        "rubric_passed", 
        "word_count", 
        "total_words", 
        "fabrication_guard_passed",
        "specificity_passed",
        "no_generic_filler_passed"
    }
    
    # Filter de binnenkomende dict zodat alleen veilige metadata overblijft
    filtered_meta = {k: v for k, v in meta.items() if k in safe_keys}
    
    # Voeg altijd de huidige timestamp toe
    filtered_meta["timestamp"] = datetime.now().isoformat()
    
    # Schrijf weg als een enkele regel (JSON Lines format)
    try:
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(filtered_meta) + "\n")
        print(f"[LOG] Run succesvol weggeschreven naar {log_filename}")
    except Exception as e:
        print(f"[LOG FOUT] Kon run niet loggen: {e}")


# --- 2. PII Leak Check (Regex Scanner) ---
def check_for_pii_leak(output_text: str) -> dict:
    """
    Scans generated text for potential PII (emails, phone numbers, and addresses)
    using robust regex patterns. Returns a summary of findings.
    """
    # Regex patronen
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Matcht internationale en lokale formaten (+44..., 06..., etc.)
    phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
    
    # Matcht typische US/EU straatnamen met nummers (bijv. "123 Main St" of "Statiestraat 45")
    address_pattern = r'\b\d+\s+[A-Za-z\s]{3,}(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Pkwy|Straat|Laan|Weg)\b'

    # Voer de scans uit
    emails_found = re.findall(email_pattern, output_text)
    phones_found = re.findall(phone_pattern, output_text)
    addresses_found = re.findall(address_pattern, output_text)

    # Schoon de resultaten op (verwijder duplicaten)
    emails_found = list(set(emails_found))
    phones_found = list(set(phones_found))
    addresses_found = list(set(addresses_found))

    # Bepaal of er überhaupt PII is gevonden
    pii_detected = bool(emails_found or phones_found or addresses_found)

    return {
        "pii_detected": pii_detected,
        "details": {
            "emails": emails_found,
            "phones": phones_found,
            "addresses": addresses_found
        }
    }


# --- Test Block ---
if __name__ == "__main__":
    print("--- START PRIVACY & LOGGING TESTS ---\n")
    
    # ==========================================
    # TEST CASE 1: Veilige data (Geen PII)
    # ==========================================
    print("TEST 1: Schone output controleren...")
    clean_text = """
    Dear Hiring Representative,
    I am highly interested in the data analyst position. I have strong experience 
    with database management and cloud solutions. I look forward to your response.
    Sincerely,
    Applicant
    """
    
    pii_report_1 = check_for_pii_leak(clean_text)
    print("Resultaat scan:")
    print(json.dumps(pii_report_1, indent=2))
    print("-" * 40)
    
    # ==========================================
    # TEST CASE 2: Output met bewuste PII lekken
    # ==========================================
    print("\nTEST 2: Output met bewuste PII controleren...")
    leaky_text = """
    LEO BROWN +44 20 7123 4567 | email: leo.brown@example.com | Glasgow
    123 Main St, London, UK
    
    Dear Hiring Representative,
    Please contact me directly at my number or my email address listed above.
    """
    
    pii_report_2 = check_for_pii_leak(leaky_text)
    print("Resultaat scan:")
    print(json.dumps(pii_report_2, indent=2))
    print("-" * 40)
    
    # ==========================================
    # TEST CASE 3: Run logging (Inclusief filter check)
    # ==========================================
    print("\nTEST 3: Logging testen...")
    
    # We simuleren de data die uit de Streamlit app komt
    sample_meta_from_app = {
        "cover_letter_requested": True,
        "rubric_passed": False,
        "total_words": 299,
        # De logger moet deze twee verboden velden negeren:
        "raw_resume_text": "Alpha Bah - Applied Computer Science student at KdG...",
        "raw_job_text": "We are looking for a Senior Data Analyst who knows Tableau..."
    }
    
    # Log de run
    log_run(sample_meta_from_app, log_filename="test_run_log.jsonl")
    
    # Laat de inhoud van de zojuist geschreven logregel zien
    if os.path.exists("test_run_log.jsonl"):
        with open("test_run_log.jsonl", "r", encoding="utf-8") as f:
            lines = f.readlines()
            print("\nLaatste regel in test_run_log.jsonl (Merk op dat de 'raw' teksten ontbreken):")
            print(lines[-1].strip())
            
        # Opruimen na test
        os.remove("test_run_log.jsonl")
        
    print("\n--- EINDE TESTS ---")