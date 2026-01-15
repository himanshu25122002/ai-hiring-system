from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
import uuid
import os

from resume_parser import parse_resume
from ai_scorer import score_resume
from interview_ai import generate_interview_question, evaluate_interview
from make_service import trigger_make_webhook

# -----------------------------
# Recommendation Logic
# -----------------------------
def get_final_recommendation(interview_score: int) -> str:
    if interview_score >= 75:
        return "Strong Fit"
    elif interview_score >= 50:
        return "Moderate Fit"
    else:
        return "Not Recommended"

app = FastAPI()

# -----------------------------
# In-memory databases (MVP)
# -----------------------------
jobs_db = {}
candidates_db = {}

UPLOAD_DIR = "uploaded_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -----------------------------
# Models
# -----------------------------
class JobCreateRequest(BaseModel):
    job_title: str
    job_description: str
    skills: str
    experience: str
    culture_traits: str | None = None


class JobCreateResponse(BaseModel):
    job_id: str
    application_link: str

# -----------------------------
# Job Creation
# -----------------------------
@app.post("/jobs/create", response_model=JobCreateResponse)
def create_job(job: JobCreateRequest):
    job_id = str(uuid.uuid4())[:8]

    jobs_db[job_id] = {
        "job_title": job.job_title,
        "job_description": job.job_description,
        "skills": job.skills,
        "experience": job.experience,
        "culture_traits": job.culture_traits
    }

    application_link = f"http://localhost:8501/?job_id={job_id}"

    return {
        "job_id": job_id,
        "application_link": application_link
    }

# -----------------------------
# Resume Upload + Scoring + Shortlisting
# -----------------------------
@app.post("/jobs/{job_id}/upload_resume")
async def upload_resume(
    job_id: str,
    name: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...)
):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX allowed")

    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Resume Parsing
    resume_text = parse_resume(file_path)

    # AI Resume Scoring
    score_result = score_resume(
        job_description=jobs_db[job_id]["job_description"],
        resume_text=resume_text
    )

    candidate_id = str(uuid.uuid4())[:8]
    shortlisted = score_result["score"] >= 70

    candidates_db[candidate_id] = {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "name": name,
        "email": email,
        "resume_text": resume_text,
        "score": score_result["score"],
        "shortlisted": shortlisted,
        "structured_form_filled": False,
        "structured_data": {}
    }

    # -----------------------------
    # MAKE – EMAIL #1 (Structured Data Form)
    # -----------------------------
    if shortlisted:
        trigger_make_webhook(
            os.getenv("MAKE_SHORTLIST_WEBHOOK"),
            {
                "name": name,
                "email": email,
                "job_title": jobs_db[job_id]["job_title"],
                "structured_form_link": "https://forms.gle/CrzrDUNv1Js2gWoj6"
            }
        )

    return {
        "message": "Resume uploaded, parsed & scored",
        "candidate_id": candidate_id,
        "shortlisted": shortlisted,
        "score": score_result["score"]
    }

# -----------------------------
# SEND AI INTERVIEW LINK (EMAIL #2)
# -----------------------------
@app.post("/candidates/{candidate_id}/send-interview-link")
def send_interview_link(candidate_id: str):
    candidate = candidates_db.get(candidate_id)

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    interview_link = f"http://localhost:8501/?candidate_id={candidate_id}"

    trigger_make_webhook(
        os.getenv("MAKE_INTERVIEW_WEBHOOK"),
        {
            "name": candidate["name"],
            "email": candidate["email"],
            "interview_link": interview_link
        }
    )

    return {"message": "AI interview link sent"}

# -----------------------------
# AI INTERVIEW
# -----------------------------
@app.post("/candidates/{candidate_id}/start-interview")
def start_interview(candidate_id: str):
    candidate = candidates_db.get(candidate_id)

    if not candidate or not candidate["shortlisted"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    candidate["interview_started"] = True
    candidate["interview_completed"] = False
    candidate["interview_qna"] = []

    question = generate_interview_question(
        jobs_db[candidate["job_id"]]["job_description"],
        candidate["resume_text"],
        []
    )

    return {"question": question}

@app.post("/candidates/{candidate_id}/answer")
def submit_answer(candidate_id: str, answer: str):
    candidate = candidates_db.get(candidate_id)

    if not candidate or not candidate.get("interview_started"):
        raise HTTPException(status_code=400, detail="Interview not started")

    candidate["interview_qna"].append({"answer": answer})

    if len(candidate["interview_qna"]) >= 5:
        evaluation = evaluate_interview(candidate["interview_qna"])
        final_reco = get_final_recommendation(evaluation["score"])

        candidate["interview_completed"] = True
        candidate["interview_score"] = evaluation["score"]
        candidate["final_recommendation"] = final_reco

        # -----------------------------
        # MAKE – EMAIL #3 (Final Interview Scheduling)
        # -----------------------------
        if final_reco in ["Strong Fit", "Moderate Fit"]:
            trigger_make_webhook(
                os.getenv("MAKE_FINAL_WEBHOOK"),
                {
                    "name": candidate["name"],
                    "email": candidate["email"],
                    "calendar_link": "Will be shared by HR shortly"
                }
            )

        return {
            "message": "Interview completed",
            "score": evaluation["score"],
            "recommendation": final_reco
        }

    return {"next_question": "Please continue"}

# -----------------------------
# HR DASHBOARD
# -----------------------------
@app.get("/jobs/{job_id}/candidates")
def get_candidates_for_job(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job_id,
        "candidates": [
            {
                "candidate_id": c["candidate_id"],
                "name": c["name"],
                "email": c["email"],
                "score": c["score"],
                "final_recommendation": c.get("final_recommendation")
            }
            for c in candidates_db.values()
            if c["job_id"] == job_id
        ]
    }
