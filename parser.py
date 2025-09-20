import pdfplumber

def read_pdf(file):
    """Read text from PDF and tidy it"""
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""
    return " ".join(text.split())
