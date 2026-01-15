import os

# 🔐 API key will be provided by company later
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def score_resume(job_description: str, resume_text: str) -> dict:
    if not OPENAI_API_KEY:
        # Placeholder response for now
        return {
            "score": 0,
            "reason": "AI scoring disabled (API key not provided)",
            "shortlisted": False
        }

    # ---- REAL IMPLEMENTATION (ENABLE LATER) ----
    """
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f'''
    Job Description:
    {job_description}

    Candidate Resume:
    {resume_text}

    Evaluate the resume against the job description.
    Give:
    - Score (0-100)
    - Short reason
    - Shortlisted (true/false, cutoff = 70)

    Return JSON only.
    '''

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.choices[0].message.content)
    """
