import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_interview_question(job_description: str, resume_text: str, previous_qna: list):
    if not OPENAI_API_KEY:
        return "Tell me about your most relevant experience for this role."

    """
    REAL IMPLEMENTATION (ENABLE LATER)

    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f'''
    Job Description:
    {job_description}

    Candidate Resume:
    {resume_text}

    Previous Questions and Answers:
    {previous_qna}

    Ask the next interview question.
    '''

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
    """
def evaluate_interview(interview_qna: list):
    if not OPENAI_API_KEY:
        return {
            "score": 0,
            "feedback": "Interview evaluation disabled (API key not provided)"
        }

    """
    REAL IMPLEMENTATION (ENABLE LATER)

    prompt = f'''
    Evaluate the interview based on the following Q&A:
    {interview_qna}

    Give:
    - Score (0-100)
    - Short feedback
    '''

    """
