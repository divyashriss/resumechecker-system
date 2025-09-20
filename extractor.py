# extractor.py
# Responsible for reading PDFs and extracting/canonicalizing text and skills.

import pdfplumber
import re

# Master skill list (tuned from your JDs + resumes). Add/modify as needed.
SKILL_SET = [
    "python", "pandas", "numpy", "sql", "power bi", "tableau",
    "matplotlib", "seaborn", "spark", "pyspark", "hadoop", "kafka",
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "scikit-learn",
    "excel", "power query", "dax", "sql server", "aws", "azure",
    "docker", "github", "git", "data visualization", "data analysis",
    "etl", "data engineering", "statistics", "probability"
]

# Normalize multi-word variants
NORMALIZE_MAP = {
    "pyspark": "pyspark",
    "powerbi": "power bi",
    "power-bi": "power bi",
    "deep-learning": "deep learning",
    "machine-learning": "machine learning",
    "nlp": "nlp",
}

def read_pdf(path_or_file):
    """
    Accepts a path string (local path) OR a file-like object provided by Streamlit uploader.
    Returns cleaned text.
    """
    text = ""
    # If a path string given:
    if isinstance(path_or_file, str):
        with pdfplumber.open(path_or_file) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
    else:
        # file-like object from Streamlit
        with pdfplumber.open(path_or_file) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""

    # basic cleanup
    text = re.sub(r'\s+', ' ', (text or "")).strip()
    return text

def clean_text(text):
    txt = (text or "").lower()
    # normalize punctuation and weird chars
    txt = re.sub(r'[\(\)\[\]\,\/\-\–\—]', ' ', txt)
    txt = re.sub(r'[^a-z0-9\s]', ' ', txt)
    txt = re.sub(r'\s+', ' ', txt).strip()
    # replace normalization map
    for k,v in NORMALIZE_MAP.items():
        txt = txt.replace(k, v)
    return txt

def extract_skills(text, skill_list=None):
    """
    Extract skills/phrases from text by phrase matching against SKILL_SET.
    Returns a sorted unique list (appearance order).
    """
    if skill_list is None:
        skill_list = SKILL_SET
    txt = clean_text(text)
    found = []
    # check longer skills first for multi-word matching
    candidates = sorted(skill_list, key=lambda x: -len(x.split()))
    for skill in candidates:
        skill_clean = clean_text(skill)
        # exact phrase search (word boundaries)
        pattern = r'\b' + re.escape(skill_clean) + r'\b'
        if re.search(pattern, txt):
            found.append(skill)
    # preserve order and uniqueness
    seen = set()
    unique = []
    for s in found:
        if s not in seen:
            unique.append(s)
            seen.add(s)
    return unique
