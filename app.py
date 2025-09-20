import streamlit as st
from parser import read_pdf
from scorer import score_resume
import pandas as pd

st.title("Resume Relevance Checker 🚀")

# Upload JD PDF
jd_file = st.file_uploader("Upload Job Description (PDF)", type=["pdf"])
# Upload Resume PDFs
resumes = st.file_uploader("Upload Resumes (PDF)", type=["pdf"], accept_multiple_files=True)

# Define important skills with weights
important_skills = {
    "Python": 2,
    "SQL": 2,
    "Power BI": 1.5,
    "Pandas": 1.5,
    "Machine Learning": 2,
    "NLP": 2
}

if st.button("Evaluate ▶️"):
    if not jd_file:
        st.error("Please upload JD first!")
        st.stop()
    if not resumes:
        st.error("Please upload at least one resume!")
        st.stop()

    # Extract text from JD
    jd_text = read_pdf(jd_file)

    # Extract top 10 keywords from JD
    words = [w.lower() for w in jd_text.split() if len(w) > 2]
    keywords = list(dict.fromkeys(words))[:10]
    st.write("Keywords for evaluation:", ", ".join(keywords))

    results = []
    for r in resumes:
        resume_text = read_pdf(r)
        score, verdict, color, matched, missing = score_resume(keywords, resume_text, important_skills)
        results.append({
            "Resume": r.name,
            "Score": score,
            "Verdict": verdict,
            "Matched": ", ".join(matched),
            "Missing": ", ".join(missing)
        })

    df = pd.DataFrame(results)
    st.dataframe(df.style.applymap(lambda x: f'color: {color}', subset=['Verdict']))
    st.download_button("Download CSV", df.to_csv(index=False).encode(), "results.csv", "text/csv")
