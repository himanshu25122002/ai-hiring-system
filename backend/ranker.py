def email_confidence_score(confidence: str) -> int:
    mapping = {
        "HIGH": 20,
        "MEDIUM": 10,
        "LOW": 0
    }
    return mapping.get(confidence, 0)


def interview_score_weight(score: int) -> int:
    return score * 0.5   # interview has strong impact


def generate_recommendation(final_score: float) -> str:
    if final_score >= 85:
        return "Strong Fit"
    elif final_score >= 70:
        return "Moderate Fit"
    else:
        return "Not Recommended"


def rank_candidates(candidates: list) -> list:
    """
    Adds rank_score, rank, and recommendation
    """

    for c in candidates:
        interview_score = c.get("interview_score", 0)

        c["rank_score"] = (
            (c.get("score", 0) * 0.4) +
            interview_score_weight(interview_score) +
            (len(c.get("skills", [])) * 5) +
            email_confidence_score(c.get("email_confidence", "LOW")) +
            (c.get("experience_years", 0) * 2)
        )

        c["recommendation"] = generate_recommendation(c["rank_score"])

    ranked = sorted(candidates, key=lambda x: x["rank_score"], reverse=True)

    for idx, c in enumerate(ranked, start=1):
        c["rank"] = idx

    return ranked
