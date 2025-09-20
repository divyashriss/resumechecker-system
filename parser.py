import re
from extractor import clean_text, SKILL_SET, extract_skills

def parse_jd(text, skill_list=None):
    """
    Parse JD text to extract structured info:
    - role_title
    - must_have_skills
    - good_to_have_skills
    - qualifications
    """

    text_clean = clean_text(text)

    # --- Extract role title ---
    role_title = ""
    # try to find line with 'position', 'role', 'job title'
    role_match = re.search(r'(?:position|role|job title)[:\-]?\s*(.+)', text, re.IGNORECASE)
    if role_match:
        role_title = role_match.group(1).strip()
    else:
        # fallback: first line capitalized words
        lines = text.split("\n")
        for line in lines:
            if line.strip() and len(line.strip().split()) < 10:
                role_title = line.strip()
                break

    # --- Extract skills ---
    skill_list = skill_list or SKILL_SET
    must_have_skills = []
    good_to_have_skills = []

    # Simple heuristic: sections containing 'must', 'required', 'minimum' -> must-have
    must_match = re.findall(r'(?:must|required|min(?:imum)?)[:\-]?\s*(.+)', text, re.IGNORECASE)
    for s in must_match:
        must_have_skills.extend(extract_skills(s, skill_list))

    # sections containing 'good', 'nice', 'preferred', 'plus' -> good-to-have
    good_match = re.findall(r'(?:good|preferred|nice|plus)[:\-]?\s*(.+)', text, re.IGNORECASE)
    for s in good_match:
        good_to_have_skills.extend(extract_skills(s, skill_list))

    # remove duplicates
    must_have_skills = list(set(must_have_skills))
    good_to_have_skills = list(set(good_to_have_skills) - set(must_have_skills))

    # --- Extract qualifications ---
    # simple heuristic: lines containing 'degree', 'bachelor', 'master', 'mba', 'phd'
    qual_keywords = ['degree', 'bachelor', 'master', 'mba', 'phd', 'engineering', 'science']
    qualifications = []
    for line in text.split("\n"):
        line_low = line.lower()
        if any(k in line_low for k in qual_keywords):
            qualifications.append(line.strip())
    qualifications = list(set(qualifications))

    return {
        "role_title": role_title,
        "must_have_skills": must_have_skills,
        "good_to_have_skills": good_to_have_skills,
        "qualifications": qualifications
    }
