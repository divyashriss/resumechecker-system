import re

def clean_text(text):
    """Lowercase and remove non-alphanumeric characters"""
    return re.sub(r'[^a-z0-9 ]', '', text.lower())

def score_resume(keywords, resume_text, weights=None):
    resume_text_clean = clean_text(resume_text)
    matched = []
    missing = []
    total_weight = 0
    obtained_weight = 0

    for k in keywords:
        key_clean = clean_text(k)
        weight = weights.get(k, 1) if weights else 1
        total_weight += weight
        if key_clean in resume_text_clean:
            matched.append(k)
            obtained_weight += weight
        else:
            missing.append(k)

    score = round((obtained_weight/total_weight)*100,2) if total_weight > 0 else 0

    if score >= 75: verdict, color = "High", "green"
    elif score >= 50: verdict, color = "Medium", "orange"
    else: verdict, color = "Low", "red"

    return score, verdict, color, matched, missing

