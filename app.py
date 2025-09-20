import streamlit as st
import pandas as pd
import os
from extractor import read_pdf, read_docx, extract_skills, clean_text, SKILL_SET
from parser import parse_jd
from scorer import score_resume
from feedback import generate_feedback
from requirement import get_requirements

st.set_page_config(page_title="Resume Relevance Checker", layout="wide")
st.title("🚀 Resume Relevance Checker - Placement Dashboard")

# --- Mode selection ---
mode = st.radio("Mode", ["Upload JD & Resumes", "Auto-scan sample_data (local)"])

# --- Sidebar: skill weights ---
st.sidebar.header("Adjust Skill Weights (optional)")
default_weights = {
    "python": 2.5, "sql": 2.0, "pandas": 1.5, "numpy": 1.2,
    "power bi": 1.5, "tableau": 1.5, "machine learning": 2.0, "nlp": 2.0,
    "spark": 1.5, "pyspark": 1.5
}
weights = {}
for k,v in default_weights.items():
    weights[k] = st.sidebar.number_input(k, min_value=0.0, max_value=5.0, value=float(v), step=0.1)

# --- JD & Resume Upload ---
if mode == "Upload JD & Resumes":
    jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf","docx"])
    resumes = st.file_uploader("Upload resumes (PDF/DOCX) — multiple", type=["pdf","docx"], accept_multiple_files=True)
else:
    # Auto scan local folder
    sample_folder = "sample_data"
    jd_file = None
    resumes = []
    if os.path.isdir(sample_folder):
        jd_files = [os.path.join(sample_folder,f) for f in os.listdir(sample_folder) if f.lower().startswith("jd")]
        resume_files = [os.path.join(sample_folder,f) for f in os.listdir(sample_folder) if f.lower().startswith("resume")]
        jd_file = jd_files[0] if jd_files else None
        resumes = resume_files

# --- Run evaluation ---
if st.button("Evaluate ▶️"):
    if not jd_file:
        st.error("No JD detected. Upload JD or ensure sample_data/jd*.pdf exists.")
        st.stop()
    if not resumes:
        st.error("No resumes found. Upload or add sample_data/resume*.pdf")
        st.stop()

    # Read JD and extract text
    jd_text = read_pdf(jd_file) if jd_file.name.endswith(".pdf") else read_docx(jd_file)
    requirements = parse_jd(jd_text)
    jd_skills = requirements['must_have_skills'] + requirements['good_to_have_skills']

    st.subheader("🔎 JD Requirements Extracted")
    st.write(f"**Role:** {requirements['role']}")
    st.write("**Must-have skills:** "+", ".join(requirements['must_have_skills']))
    st.write("**Good-to-have skills:** "+", ".join(requirements['good_to_have_skills']))
    st.write("**Qualifications:** "+", ".join(requirements['qualifications']))

    # Evaluate each resume
    rows = []
    for r in resumes:
        rname = r if isinstance(r,str) else r.name
        rtext = read_pdf(r) if rname.lower().endswith(".pdf") else read_docx(r)
        score, verdict, color, matched, missing, details = score_resume(jd_skills, rtext, weights)
        feedback = generate_feedback(rname, score, matched, missing)
        rows.append({
            "Resume": rname,
            "Score": score,
            "Verdict": verdict,
            "Matched": "; ".join(matched),
            "Missing": "; ".join(missing),
            "Feedback": feedback
        })

    df = pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)

    st.subheader("🏆 Top Candidates")
    st.dataframe(df[["Resume","Score","Verdict"]])

    st.subheader("📊 Score Distribution")
    st.bar_chart(df.set_index("Resume")["Score"])

    st.subheader("🧾 Detailed Results")
    for idx, r in df.iterrows():
        st.markdown(f"### {r['Resume']} — {r['Score']}% — **{r['Verdict']}**")
        st.markdown(r["Feedback"])
        st.write("---")

    st.download_button("💾 Download CSV", df.to_csv(index=False).encode(), "results.csv", "text/csv")
