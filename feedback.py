# feedback.py
# Builds human-friendly feedback based on matches & missing skills.

def generate_feedback(resume_name, score, matched, missing, top_matched_n=5):
    """
    Returns a short structured feedback string.
    """
    # Strong points
    if matched:
        top = ", ".join(matched[:top_matched_n])
        strong = f"✅ Strong in: {top}."
    else:
        strong = "✅ Strong in: None detected."

    # Missing high-impact skills
    if missing:
        miss_short = ", ".join(missing[:6])
        missing_msg = f"⚠️ Missing/weak: {miss_short}."
    else:
        missing_msg = "⚠️ Missing: None."

    # Actionable suggestions
    if score >= 80:
        suggestion = "💡 Candidate is a strong fit. Prepare for interview and focus on role-specific projects."
    elif score >= 55:
        suggestion = "💡 Decent fit — suggest adding relevant projects/certifications for missing skills to improve fit."
    else:
        suggestion = "💡 Low fit — recommend upskilling on missing core technologies and adding practical projects."

    feedback = f"{strong} {missing_msg} Overall Fit: {score}%. {suggestion}"
    return feedback
