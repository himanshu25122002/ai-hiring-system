def email_confidence_score(confidence: str) -> int:
    mapping = {
        "HIGH": 20,
        "MEDIUM": 10,
        "LOW": 0
    }
    return mapping.get(confidence, 0)


def interview_score_safe(score):
    """
    Handle None interview scores safely
    """
    if score is None:
        return 0
    return score


def rank_candidates(candidates: list) -> list:
    """
    Adds:
    - rank_score
    - rank
    - recommendation
    """

    for c in candidates:
        resume_score = c.get("score", 0)
        interview_score = interview_score_safe(c.get("interview_score"))
        skills_count = len(c.get("skills", []))
        experience_years = c.get("experience_years", 0)
        email_score = email_confidence_score(c.get("email_confidence", "LOW"))

        # 🔥 FINAL RANK SCORE
        c["rank_score"] = (
            resume_score * 0.4 +
            interview_score * 0.4 +
            skills_count * 5 +
            experience_years * 2 +
            email_score
        )

        # 🎯 FINAL RECOMMENDATION
        if interview_score >= 75 and resume_score >= 70:
            c["recommendation"] = "STRONG_FIT"
        elif interview_score >= 50:
            c["recommendation"] = "MODERATE_FIT"
        else:
            c["recommendation"] = "NOT_RECOMMENDED"

    # Sort by rank_score
    ranked = sorted(candidates, key=lambda x: x["rank_score"], reverse=True)

    # Assign rank numbers
    for idx, c in enumerate(ranked, start=1):
        c["rank"] = idx

    return ranked
