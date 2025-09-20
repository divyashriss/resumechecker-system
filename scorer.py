# scorer.py
# Weighted + frequency-aware scoring logic.

import re
from collections import Counter

def clean_text(text):
    t = (text or "").lower()
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def score_resume(keywords, resume_text, weights=None, freq_boost=True):
    """
    keywords: list of JD skills/phrases (strings)
    resume_text: full resume text (string)
    weights: dict mapping skill -> weight (float). if not present, weight=1.
    freq_boost: if True, multiple mentions add small bonus.
    Returns: score (0-100), verdict, color, matched list, missing list, details dict
    """
    resume_clean = clean_text(resume_text)
    total_weight = 0.0
    achieved = 0.0
    matched = []
    missing = []
    # count frequencies if requested
    tokens = resume_clean.split()
    token_counter = Counter(tokens) if freq_boost else None

    for k in keywords:
        k_clean = clean_text(k)
        w = float(weights.get(k, 1.0)) if weights else 1.0
        total_weight += w
        # phrase presence
        pattern = r'\b' + re.escape(k_clean) + r'\b'
        if re.search(pattern, resume_clean):
            matched.append(k)
            # frequency boost: count occurrences of words in phrase
            bonus = 0.0
            if freq_boost and token_counter:
                # approximate phrase freq by min count of words in phrase
                parts = k_clean.split()
                counts = [token_counter.get(p,0) for p in parts]
                count_phrase = min(counts) if counts else 0
                # bonus is small multiplier of (count_phrase - 1)
                if count_phrase > 1:
                    bonus = 0.15 * (count_phrase - 1) * w
            achieved += w + bonus
        else:
            missing.append(k)

    # avoid div by zero
    score = round((achieved / total_weight) * 100, 2) if total_weight > 0 else 0.0
    if score >= 80:
        verdict, color = "High", "green"
    elif score >= 55:
        verdict, color = "Medium", "orange"
    else:
        verdict, color = "Low", "red"

    details = {
        "total_weight": total_weight,
        "achieved_weight": round(achieved,2)
    }
    return score, verdict, color, matched, missing, details

