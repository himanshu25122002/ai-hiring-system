from difflib import SequenceMatcher

def text_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def is_duplicate_resume(candidate, existing_candidates, threshold=0.90):
    """
    Checks if a candidate resume is duplicate
    """

    for existing in existing_candidates:

        # 1️⃣ Strong signal: Email match
        if (
            candidate["parsed"].get("email")
            and candidate["parsed"].get("email") == existing["parsed"].get("email")
        ):
            return True, "EMAIL_MATCH"

        # 2️⃣ Resume text similarity
        sim = text_similarity(
            candidate.get("resume_text", ""),
            existing.get("resume_text", "")
        )
        if sim >= threshold:
            return True, f"TEXT_SIMILARITY_{round(sim, 2)}"

        # 3️⃣ Weak signal: same name + skill overlap
        if (
            candidate["parsed"].get("name") == existing["parsed"].get("name")
            and len(
                set(candidate["parsed"].get("skills", []))
                & set(existing["parsed"].get("skills", []))
            ) >= 3
        ):
            return True, "NAME_SKILL_OVERLAP"

    return False, None
