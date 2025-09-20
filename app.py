# app.py - main Streamlit app (drop into repo root)
import streamlit as st
import pandas as pd
import os
from extractor import read_pdf, extract_skills, clean_text, SKILL_SET
from scorer import score_resume
from feedback import generate_feedback
import matplotlib.pyplot as plt
import streamlit as st
from utils import score_resume

st.title("Resume Checker 🔍")

# Hiring person inputs requirements
st.subheader("Enter Job Requirements / Skills")
jd_input = st.text_area(
    "Paste job description or required skills here:",
    placeholder="e.g. Python, SQL, Machine Learning, Communication, AWS"
)

# Convert JD input into keyword list
keywords = [k.strip() for k in jd_input.split(",") if k.strip()]

# Resume input
resume_text = st.text_area("Paste Resume Text", height=250)

if st.button("Check Resume"):
    if not keywords:
        st.warning("⚠️ Please enter at least one requirement/skill.")
    elif not resume_text.strip():
        st.warning("⚠️ Please paste the resume text.")
    else:
        # Run scoring
        score, verdict, color, matched, missing, details = score_resume(keywords, resume_text)

        st.markdown(f"### Final Score: *{score}%*")
        st.markdown(f"Verdict: <span style='color:{color}'>{verdict}</span>", unsafe_allow_html=True)

        st.write("✅ Matched Skills:", matched)
        st.write("❌ Missing Skills:", missing)
        st.write("📊 Details:", details)

st.set_page_config(page_title="Resume Relevance - Pro", layout="wide")
st.title("🚀 Resume Relevance Checker")

# --- UI: choose mode ---
mode = st.radio("Mode", ["Upload JD & Resumes", "Auto-scan sample_data (local)"])

# optional: let user override core skill weights
default_weights = {
    "python": 2.5, "sql": 2.0, "pandas": 1.5, "numpy": 1.2,
    "power bi": 1.5, "tableau": 1.5, "machine learning": 2.0, "nlp": 2.0,
    "spark": 1.5, "pyspark": 1.5
}

st.sidebar.header("Adjust Skill Weights (optional)")
weights = {}
for k,v in default_weights.items():
    val = st.sidebar.number_input(k, min_value=0.0, max_value=5.0, value=float(v), step=0.1)
    weights[k] = val

# Uploader or auto-scan
if mode == "Upload JD & Resumes":
    jd_file = st.file_uploader("Upload JD (PDF)", type=["pdf"])
    resumes = st.file_uploader("Upload resumes (PDF) — multiple", type=["pdf"], accept_multiple_files=True)
else:
    # Look for sample_data folder in repo root
    sample_folder = "sample_data"
    jd_file = None
    resumes = []
    if os.path.isdir(sample_folder):
        # JDs -> files with jd in name
        jd_files = [os.path.join(sample_folder,f) for f in os.listdir(sample_folder) if f.lower().startswith("jd") and f.lower().endswith(".pdf")]
        resume_files = [os.path.join(sample_folder,f) for f in os.listdir(sample_folder) if f.lower().startswith("resume") and f.lower().endswith(".pdf")]
        if jd_files:
            jd_file = jd_files[0]
        resumes = resume_files

if st.button("Evaluate ▶️"):
    if not jd_file:
        st.error("No JD detected. Upload JD or ensure sample_data/jd*.pdf exists.")
        st.stop()
    if not resumes:
        st.error("No resumes found. Upload or add sample_data/resume*.pdf")
        st.stop()

    # Read JD text and extract skills
    jd_text = read_pdf(jd_file)
    jd_skills = extract_skills(jd_text, skill_list=SKILL_SET)
    if not jd_skills:
        # fallback: use SKILL_SET intersection with JD text tokens
        jd_lower = clean_text(jd_text)
        jd_skills = [s for s in SKILL_SET if s in jd_lower]

    st.subheader("🔎 Extracted JD Skills / Phrases")
    st.write(", ".join(jd_skills[:40]) if jd_skills else "No skill phrases auto-extracted.")

    # Evaluate each resume
    rows = []
    global_skill_counter = {}
    for r in resumes:
        # r might be path string or file-like
        rname = r if isinstance(r, str) else r.name
        rtext = read_pdf(r)
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

        # aggregate skills counts
        for s in matched:
            global_skill_counter[s] = global_skill_counter.get(s, 0) + 1

    df = pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)

    # Summary stats + ranking
    st.subheader("🏆 Summary & Ranking")
    st.write("Top candidates by relevance score:")
    st.dataframe(df[["Resume","Score","Verdict"]])

    # Bar chart of scores
    st.subheader("📊 Score Distribution")
    chart_df = df.set_index("Resume")["Score"]
    st.bar_chart(chart_df)


    st.subheader("🧾 Detailed results")
    for idx, r in df.iterrows():
        st.markdown(f"### {r['Resume']} — {r['Score']}% — **{r['Verdict']}**")
        st.markdown(r["Feedback"])
        st.write("---")

    # Download CSV
    st.download_button("💾 Download full results CSV", df.to_csv(index=False).encode(), "results.csv", "text/csv")



