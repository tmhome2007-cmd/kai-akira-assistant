import os
import fitz  # PyMuPDF
import docx
import re

def clean_spaced_text(text: str) -> str:
    """Cleans up text formatting and fixes disjointed email addresses."""
    cleaned_lines = []
    for line in text.split('\n'):
        marker_line = line.replace("  ", " [WORD_BOUND] ")
        no_spaces = re.sub(r'(?<=\b\w)\s(?=\w\b)', '', marker_line)
        fixed_line = no_spaces.replace("[WORD_BOUND]", " ")
        
        if "@" in fixed_line:
            fixed_line = re.sub(r'\s*@\s*', '@', fixed_line)
            fixed_line = re.sub(r'(?<=\w)\s*\.\s*(?=\w)', '.', fixed_line)
        
        fixed_line = re.sub(r'\s+([.,])', r'\1', fixed_line)
        fixed_line = re.sub(r'\s+', ' ', fixed_line).strip()
        
        if fixed_line:
            cleaned_lines.append(fixed_line)
    return "\n".join(cleaned_lines)

def extract_resume_text(file_path: str) -> str:
    """Reads a resume file (.pdf or .docx) and returns plain text."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at: '{file_path}'")
    
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    extracted_text = []
    
    if extension == '.pdf':
        doc = fitz.open(file_path)
        for page in doc:
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: (b[1], b[0]))
            for block in blocks:
                block_text = block[4].strip()
                if block_text:
                    extracted_text.append(clean_spaced_text(block_text))
                    
    elif extension == '.docx':
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                extracted_text.append(paragraph.text.strip())
    else:
        raise ValueError(f"Unsupported extension: '{extension}'")
    
    return "\n\n".join(extracted_text)

if __name__ == "__main__":
    print("Module resume_extractor loaded cleanly.")