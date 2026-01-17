from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
import uuid
import os

from backend.schemas import JobInput
from backend.resume_parser import parse_resume
from backend.ai_scorer import score_resume
from backend.resume_extractor import extract_resume_data
from backend.google_sheets import append_candidate

app = FastAPI(
    title="AI Resume Screening Backend",
    version="2.0"
)

UPLOAD_DIR = "uploaded_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory store (later Google Sheets / DB)
screening_db = {}

# -------------------------------------------------
# STEP 1: HR submits job + multiple resumes
# -------------------------------------------------
@app.post("/screen-resumes")
async def screen_resumes(
    role: str = Form(...),
    required_skills: str = Form(...),   # comma-separated
    experience_level: str = Form(...),
    culture_traits: str = Form(""),
    resumes: List[UploadFile] = File(...)
):
    if not resumes:
        raise HTTPException(status_code=400, detail="No resumes uploaded")

    job_id = str(uuid.uuid4())[:8]

    job_data = {
        "job_id": job_id,
        "role": role,
        "required_skills": [s.strip() for s in required_skills.split(",")],
        "experience_level": experience_level,
        "culture_traits": [c.strip() for c in culture_traits.split(",") if c],
        "candidates": []
    }

    for resume in resumes:
        if not resume.filename.endswith((".pdf", ".docx")):
            continue

        file_path = f"{UPLOAD_DIR}/{job_id}_{resume.filename}"
        with open(file_path, "wb") as f:
            f.write(await resume.read())

        # -------- Resume Parsing --------
        resume_text = parse_resume(file_path)

        parsed_data = extract_resume_data(
            resume_text=resume_text,
            required_skills=job_data["required_skills"]
        )


        # -------- AI Scoring --------
        score_result = score_resume(
            job_description=role + " " + required_skills,
            resume_text=resume_text
        )

        candidate_id = str(uuid.uuid4())[:8]

        job_data["candidates"].append({
            "candidate_id": candidate_id,
            "file_name": resume.filename,
            "parsed": parsed_data,
            "score": score_result["score"],
            "shortlisted": score_result["score"] >= 90
        })
         append_candidate({
            "job_id": job_id,
            "role": role,
            "candidate_id": candidate_id,
            "name": parsed_data.get("name"),
            "email": parsed_data.get("email"),
            "skills": ", ".join(parsed_data.get("skills", [])),
            "experience_years": parsed_data.get("experience_years"),
            "score": score_result["score"],
            "shortlisted": shortlisted,
            "resume_file": resume.filename,
            "confidence": parsed_data.get("confidence")
        })
    
    
    screening_db[job_id] = job_data

    return {
        "message": "Bulk resumes processed successfully",
        "job_id": job_id,
        "total_resumes": len(job_data["candidates"]),
        "shortlisted": len([c for c in job_data["candidates"] if c["shortlisted"]])
    }

# -------------------------------------------------
# HR: View parsed + scored resumes
# -------------------------------------------------
@app.get("/jobs/{job_id}/results")
def get_screening_results(job_id: str):
    job = screening_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job

# -------------------------------------------------
# Health check
# -------------------------------------------------
@app.get("/")
def health():
    return {"status": "Backend running"}


