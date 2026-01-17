import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -------------------------------------------------
# Generate Interview Question
# -------------------------------------------------
def generate_interview_question(
    job_description: str,
    resume_text: str,
    previous_qna: list
):
    """
    Generates next interview question based on job, resume & history
    """

    # Fallback (NO API KEY)
    if not OPENAI_API_KEY:
        if not previous_qna:
            return "Tell me about your most relevant experience for this role."
        elif len(previous_qna) == 1:
            return "Describe a challenging problem you solved recently."
        elif len(previous_qna) == 2:
            return "How do you usually communicate complex ideas to teammates?"
        elif len(previous_qna) == 3:
            return "Tell me about a situation where you had to adapt quickly."
        else:
            return "Why do you think you are a good fit for this role?"

    # REAL IMPLEMENTATION (enable later)
    """
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f'''
    Job Description:
    {job_description}

    Candidate Resume:
    {resume_text}

    Previous Q&A:
    {previous_qna}

    Ask the next interview question.
    '''

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
    """

# -------------------------------------------------
# Evaluate Interview
# -------------------------------------------------
def evaluate_interview(interview_qna: list):
    """
    Evaluates interview performance and returns structured scorecard
    """

    # Fallback scoring (NO API KEY)
    if not OPENAI_API_KEY:
        total_answers = len(interview_qna)
        avg_length = sum(len(q["answer"].split()) for q in interview_qna) / max(total_answers, 1)

        skill_fit = min(100, avg_length * 2)
        communication = min(100, avg_length * 1.5)
        problem_solving = min(100, avg_length * 1.2)
        culture_fit = min(100, avg_length)

        final_score = int(
            (skill_fit + communication + problem_solving + culture_fit) / 4
        )

        recommendation = (
            "Strong Fit" if final_score >= 75
            else "Moderate Fit" if final_score >= 50
            else "Not Recommended"
        )

        return {
            "final_score": final_score,
            "skill_fit": int(skill_fit),
            "communication": int(communication),
            "problem_solving": int(problem_solving),
            "culture_fit": int(culture_fit),
            "recommendation": recommendation,
            "feedback": "Rule-based evaluation (OpenAI disabled)"
        }

    # REAL IMPLEMENTATION (enable later)
    """
    prompt = f'''
    Evaluate the interview based on the following Q&A:
    {interview_qna}

    Return JSON with:
    - skill_fit (0-100)
    - communication (0-100)
    - problem_solving (0-100)
    - culture_fit (0-100)
    - final_score (0-100)
    - recommendation (Strong Fit / Moderate Fit / Not Recommended)
    - short feedback
    '''
    """
