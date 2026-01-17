from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
import uuid
import os

from backend.schemas import JobInput
from backend.resume_parser import parse_resume
from backend.ai_scorer import score_resume
from backend.resume_extractor import extract_resume_data
from backend.google_sheets import append_candidate
from backend.google_drive import (
    extract_folder_id,
    list_files_in_folder,
    download_file
)
from backend.email_validator import calculate_email_confidence
from backend.ranker import rank_candidates
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
        email_confidence = calculate_email_confidence(
            name=parsed_data.get("name", ""),
            email=parsed_data.get("email", ""),
            resume_text=resume_text
        )


        parsed_data["email_confidence"] = email_confidence




        # -------- AI Scoring --------
        score_result = score_resume(
            job_description=role + " " + required_skills,
            resume_text=resume_text
        )

        candidate_id = str(uuid.uuid4())[:8]

        job_data["candidates"].append({
            "candidate_id": candidate_id,
            "file_name": resume.filename,
            "resume_text": resume_text,
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
            "email_confidence": email_confidence,
            "skills": ", ".join(parsed_data.get("skills", [])),
            "experience_years": parsed_data.get("experience_years"),
            "score": score_result["score"],
            "shortlisted": shortlisted,
            "resume_file": resume.filename,
            "confidence": parsed_data.get("confidence")
            "rank": candidate["rank"],
            "rank_score": round(candidate["rank_score"], 2)

        })


    
    job_data["candidates"] = rank_candidates(job_data["candidates"])
    screening_db[job_id] = job_data

    return {
        "message": "Bulk resumes processed successfully",
        "job_id": job_id,
        "total_resumes": len(job_data["candidates"]),
        "shortlisted": len([c for c in job_data["candidates"] if c["shortlisted"]])
    }

@app.post("/screen-resumes-from-drive")
async def screen_resumes_from_drive(
    role: str = Form(...),
    required_skills: str = Form(...),
    experience_level: str = Form(...),
    culture_traits: str = Form(""),
    drive_folder_link: str = Form(...)
):
    job_id = str(uuid.uuid4())[:8]

    folder_id = extract_folder_id(drive_folder_link)
    files = list_files_in_folder(folder_id)

    if not files:
        raise HTTPException(status_code=400, detail="No files found in folder")

    job_data = {
        "job_id": job_id,
        "role": role,
        "candidates": []
    }

    for file in files:
        if not file["name"].endswith((".pdf", ".docx")):
            continue

        file_path = download_file(
            file_id=file["id"],
            filename=f"{job_id}_{file['name']}",
            download_dir=UPLOAD_DIR
        )

        # -------- Resume Parsing --------
        resume_text = parse_resume(file_path)

        parsed_data = extract_resume_data(
            resume_text=resume_text,
            required_skills=[s.strip() for s in required_skills.split(",")]
        )

         email_confidence = calculate_email_confidence(
            name=parsed_data.get("name", ""),
            email=parsed_data.get("email", ""),
            resume_text=resume_text
        )


        parsed_data["email_confidence"] = email_confidence


        score_result = score_resume(
            job_description=f"{role} {required_skills}",
            resume_text=resume_text
        )

        candidate_id = str(uuid.uuid4())[:8]
        shortlisted = score_result["score"] >= 90

        # -------- Save to Google Sheets --------
       job_data["candidates"].append({
            "candidate_id": candidate_id,
            "name": parsed_data.get("name"),
            "email": parsed_data.get("email"),
            "score": score_result["score"],
            "shortlisted": shortlisted
        })

        append_candidate({
            "job_id": job_id,
            "role": role,
            "candidate_id": candidate_id,
            "name": parsed_data.get("name"),
            "email": parsed_data.get("email"),
            "email_confidence": email_confidence,
            "skills": ", ".join(parsed_data.get("skills", [])),
            "experience_years": parsed_data.get("experience_years"),
            "score": score_result["score"],
            "shortlisted": shortlisted,
            "resume_file": resume.filename,
            "confidence": parsed_data.get("confidence")
            "rank": candidate["rank"],
            "rank_score": round(candidate["rank_score"], 2)

        })

        
    job_data["candidates"] = rank_candidates(job_data["candidates"])
    screening_db[job_id] = job_data

    return {
        "message": "Google Drive resumes processed successfully",
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






