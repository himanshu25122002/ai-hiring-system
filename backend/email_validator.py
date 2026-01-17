import re

DISPOSABLE_DOMAINS = {
    "mailinator.com",
    "tempmail.com",
    "10minutemail.com",
    "guerrillamail.com",
    "yopmail.com"
}


def is_valid_format(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def is_disposable(email: str) -> bool:
    domain = email.split("@")[-1].lower()
    return domain in DISPOSABLE_DOMAINS


def name_email_similarity(name: str, email: str) -> float:
    """
    Check how much candidate name matches email username
    """
    username = email.split("@")[0].lower()
    name_parts = name.lower().split()

    matches = sum(1 for part in name_parts if part in username)
    return matches / max(len(name_parts), 1)


def calculate_email_confidence(name: str, email: str, resume_text: str) -> str:
    if not email:
        return "LOW"

    score = 0

    # 1️⃣ Format check
    if is_valid_format(email):
        score += 30
    else:
        return "LOW"

    # 2️⃣ Disposable domain check
    if not is_disposable(email):
        score += 30
    else:
        return "LOW"

    # 3️⃣ Name similarity
    similarity = name_email_similarity(name, email)
    if similarity >= 0.5:
        score += 20
    elif similarity >= 0.2:
        score += 10

    # 4️⃣ Resume context presence
    if email.lower() in resume_text.lower():
        score += 20

    # Final decision
    if score >= 80:
        return "HIGH"
    elif score >= 50:
        return "MEDIUM"
    else:
        return "LOW"
