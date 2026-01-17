def email_confidence_score(confidence: str) -> int:
    mapping = {
        "HIGH": 20,
        "MEDIUM": 10,
        "LOW": 0
    }
    return mapping.get(confidence, 0)


def rank_candidates(candidates: list) -> list:
    """
    Adds rank_score and rank position to each candidate
    """

    for c in candidates:
        c["rank_score"] = (
            (c.get("score", 0) * 0.6)
            + (len(c.get("parsed", {}).get("skills", [])) * 10)
            + email_confidence_score(c.get("parsed", {}).get("email_confidence", "LOW"))
            + (c.get("parsed", {}).get("experience_years", 0) * 2)
        )

    # Sort descending
    ranked = sorted(candidates, key=lambda x: x["rank_score"], reverse=True)

    # Assign rank numbers
    for idx, c in enumerate(ranked, start=1):
        c["rank"] = idx

    return ranked
