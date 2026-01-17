import os
import json
from typing import Dict

# 🔐 API key will be provided by company later
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def score_resume(job_description: str, resume_text: str) -> Dict:
    """
    Returns:
    {
        score: int (0–100),
        reason: str,
        shortlisted: bool
    }
    """

    # -------------------------------
    # FALLBACK MODE (NO API KEY)
    # -------------------------------
    if not OPENAI_API_KEY:
        heuristic_score = heuristic_scoring(job_description, resume_text)

        return {
            "score": heuristic_score,
            "reason": "Heuristic scoring used (AI disabled)",
            "shortlisted": heuristic_score >= 90
        }

    # -------------------------------
    # AI MODE (ENABLE LATER)
    # -------------------------------
    """
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f'''
    You are an ATS resume evaluator.

    Job Description:
    {job_description}

    Candidate Resume:
    {resume_text}

    Evaluate the resume strictly.

    Return JSON ONLY:
    {{
        "score": <0-100>,
        "reason": "<short explanation>",
        "shortlisted": <true|false>
    }}

    Shortlist cutoff = 90.
    '''

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return json.loads(response.choices[0].message.content)
    """


# -------------------------------
# HEURISTIC SCORING (NO AI)
# -------------------------------
def heuristic_scoring(job_description: str, resume_text: str) -> int:
    """
    Simple, deterministic scoring:
    - Skill overlap
    - Resume length sanity
    """

    job_words = set(job_description.lower().split())
    resume_words = set(resume_text.lower().split())

    overlap = job_words.intersection(resume_words)
    overlap_ratio = len(overlap) / max(len(job_words), 1)

    # Skill relevance (70%)
    skill_score = overlap_ratio * 70

    # Resume completeness (30%)
    length_score = min(len(resume_text) / 2000, 1.0) * 30

    final_score = int(skill_score + length_score)

    return min(max(final_score, 0), 100)
