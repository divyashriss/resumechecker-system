import re
import fitz  # PyMuPDF
import docx

# Default skill set for extraction (can expand later)
SKILL_SET = [
    "python", "sql", "pandas", "numpy", "power bi", "tableau",
    "machine learning", "nlp", "spark", "pyspark", "excel", "statistics",
    "deep learning", "keras", "tensorflow", "scikit-learn"
]

def read_pdf(file_path):
    """
    Extract raw text from PDF.
    Accepts file path or file-like object
    """
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f"PDF read error: {e}")
    return text

def read_docx(file_path):
    """
    Extract raw text from DOCX file
    """
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"DOCX read error: {e}")
    return text

def clean_text(text):
    """
    Normalize text: lowercase, remove special chars, extra spaces
    """
    t = (text or "").lower()
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def extract_skills(text, skill_list=None):
    """
    Extract skills from resume/JD text
    """
    skill_list = skill_list or SKILL_SET
    text_clean = clean_text(text)
    extracted = [s for s in skill_list if s in text_clean]
    return extracted

