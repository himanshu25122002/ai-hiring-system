def email_confidence_score(confidence: str) -> int:
    mapping = {
        "HIGH": 20,
        "MEDIUM": 10,
        "LOW": 0
    }
    return mapping.get(confidence, 0)


def rank_candidates(candidates: list) -> list:
    """
    Calculates rank_score, rank, interview_score, and recommendation
    """

    # STEP 1: Calculate rank_score for each candidate
    for c in candidates:
        parsed = c.get("parsed", {})

        c["rank_score"] = (
            (c.get("score", 0) * 0.6)
            + (len(parsed.get("skills", [])) * 10)
            + email_confidence_score(parsed.get("email_confidence", "LOW"))
            + (parsed.get("experience_years", 0) * 2)
        )

    # STEP 2: Sort candidates by rank_score (highest first)
    ranked = sorted(candidates, key=lambda x: x["rank_score"], reverse=True)

    # STEP 3: Assign rank + recommendation
    for idx, c in enumerate(ranked, start=1):
        c["rank"] = idx

        # Interview score (future use)
        c["interview_score"] = None

        # Recommendation logic
        if c["rank_score"] >= 90:
            c["recommendation"] = "Strong Fit"
        elif c["rank_score"] >= 75:
            c["recommendation"] = "Moderate Fit"
        else:
            c["recommendation"] = "Not Recommended"

    return ranked
