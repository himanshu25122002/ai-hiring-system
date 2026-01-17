import re
from typing import Dict, List


EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)


def extract_email(text: str) -> str | None:
    """
    Extract email using regex.
    Returns first valid email found.
    """
    matches = EMAIL_REGEX.findall(text)
    return matches[0] if matches else None


def extract_name(text: str) -> str | None:
    """
    Heuristic:
    - Assume name is in first 5 lines
    - Ignore lines with email/phone
    """
    lines = text.splitlines()[:5]

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "@" in line or any(char.isdigit() for char in line):
            continue
        if len(line.split()) <= 4:
            return line

    return None


def extract_skills(text: str, skill_list: List[str]) -> List[str]:
    """
    Match skills from predefined list
    """
    found = []
    text_lower = text.lower()

    for skill in skill_list:
        if skill.lower() in text_lower:
            found.append(skill)

    return found


def estimate_experience_years(text: str) -> float | None:
    """
    Heuristic:
    Look for patterns like '3 years', '2.5 yrs'
    """
    match = re.search(r"(\d+(\.\d+)?)\s*(years|yrs)", text.lower())
    if match:
        return float(match.group(1))

    return None


def extract_resume_data(
    resume_text: str,
    required_skills: List[str]
) -> Dict:
    """
    Master extractor
    """
    email = extract_email(resume_text)
    name = extract_name(resume_text)
    skills = extract_skills(resume_text, required_skills)
    experience = estimate_experience_years(resume_text)

    confidence = 0.0
    if email:
        confidence += 0.4
    if name:
        confidence += 0.2
    if skills:
        confidence += 0.2
    if experience:
        confidence += 0.2

    return {
        "name": name,
        "email": email,
        "skills": skills,
        "experience_years": experience,
        "confidence": round(confidence, 2)
    }
