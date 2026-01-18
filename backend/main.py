from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
import uuid
import os

from backend.resume_parser import parse_resume
from backend.resume_extractor import extract_resume_data
from backend.ai_scorer import score_resume
from backend.email_validator import calculate_email_confidence
from backend.duplicate_detector import is_duplicate_resume
from backend.ranker import rank_candidates
from backend.google_sheets import append_candidate
from backend.google_drive import (
    extract_folder_id,
    list_files_in_folder,
    download_file
)
from backend.interview_ai import (
    generate_interview_question,
    evaluate_interview
)
from backend.make_service import trigger_make_webhook

# -------------------------------------------------
# App Init
# -------------------------------------------------
app = FastAPI(
    title="AI Resume Screening Backend",
    version="2.0"
)

UPLOAD_DIR = "uploaded_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Cache only (Google Sheets = DB)
screening_db = {}

# =================================================
# STEP 1A: HR uploads MULTIPLE resumes (manual)
# =================================================
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
    required_skills_list = [s.strip() for s in required_skills.split(",")]

    job_data = {
        "job_id": job_id,
        "role": role,
        "required_skills": required_skills_list,
        "experience_level": experience_level,
        "culture_traits": culture_traits,
        "candidates": []
    }

    for resume in resumes:
        if not resume.filename.lower().endswith((".pdf", ".docx")):
            continue

        file_path = f"{UPLOAD_DIR}/{job_id}_{resume.filename}"
        with open(file_path, "wb") as f:
            f.write(await resume.read())

        resume_text = parse_resume(file_path)

        # ---- Duplicate Detection ----
        if is_duplicate_resume(resume_text, job_data["candidates"]):
            continue

        parsed_data = extract_resume_data(
            resume_text=resume_text,
            required_skills=required_skills_list
        )

        email_confidence = calculate_email_confidence(
            name=parsed_data.get("name", ""),
            email=parsed_data.get("email", ""),
            resume_text=resume_text
        )

        score_result = score_resume(
            job_description=f"{role} {required_skills}",
            resume_text=resume_text
        )

        candidate_id = str(uuid.uuid4())[:8]
        shortlisted = score_result["score"] >= 90
       

        job_data["candidates"].append({
            "candidate_id": candidate_id,
            "name": parsed_data.get("name"),
            "email": parsed_data.get("email"),
            "email_confidence": email_confidence,
            "skills": parsed_data.get("skills", []),
            "experience_years": parsed_data.get("experience_years"),
            "score": score_result["score"],
            "shortlisted": shortlisted,
            "resume_file": resume.filename,
            "confidence": parsed_data.get("confidence", 0)
            "interview_score": None,
            "recommendation": "PENDING"

        })

    # ---- Ranking ----
    job_data["candidates"] = rank_candidates(job_data["candidates"])

    # ---- Save to Google Sheets ----
    for candidate in job_data["candidates"]:
        append_candidate({
            "job_id": job_id,
            "role": role,
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "email": candidate["email"],
            "email_confidence": candidate["email_confidence"],
            "skills": ", ".join(candidate["skills"]),
            "experience_years": candidate["experience_years"],
            "score": candidate["score"],
            "shortlisted": candidate["shortlisted"],
            "resume_file": candidate["resume_file"],
            "confidence": candidate["confidence"],
            "rank": candidate["rank"],
            "rank_score": round(candidate["rank_score"], 2),
            "interview_score": candidate["interview_score"],
            "recommendation": candidate["recommendation"]



        })

    screening_db[job_id] = job_data

    return {
        "message": "Resumes processed & ranked successfully",
        "job_id": job_id,
        "total_resumes": len(job_data["candidates"]),
        "shortlisted": len([c for c in job_data["candidates"] if c["shortlisted"]])
    }

# =================================================
# STEP 1B: HR provides GOOGLE DRIVE folder link
# =================================================
@app.post("/screen-resumes-from-drive")
async def screen_resumes_from_drive(
    role: str = Form(...),
    required_skills: str = Form(...),
    experience_level: str = Form(...),
    culture_traits: str = Form(""),
    drive_folder_link: str = Form(...)
):
    job_id = str(uuid.uuid4())[:8]
    required_skills_list = [s.strip() for s in required_skills.split(",")]

    folder_id = extract_folder_id(drive_folder_link)
    files = list_files_in_folder(folder_id)

    if not files:
        raise HTTPException(status_code=400, detail="No files found in folder")

    job_data = {
        "job_id": job_id,
        "role": role,
        "required_skills": required_skills_list,
        "experience_level": experience_level,
        "culture_traits": culture_traits,
        "candidates": []
    }

    for file in files:
        if not file["name"].lower().endswith((".pdf", ".docx")):
            continue

        file_path = download_file(
            file_id=file["id"],
            filename=f"{job_id}_{file['name']}",
            download_dir=UPLOAD_DIR
        )

        resume_text = parse_resume(file_path)

        if is_duplicate_resume(resume_text, job_data["candidates"]):
            continue

        parsed_data = extract_resume_data(
            resume_text=resume_text,
            required_skills=required_skills_list
        )

        email_confidence = calculate_email_confidence(
            name=parsed_data.get("name", ""),
            email=parsed_data.get("email", ""),
            resume_text=resume_text
        )

        score_result = score_resume(
            job_description=f"{role} {required_skills}",
            resume_text=resume_text
        )

        candidate_id = str(uuid.uuid4())[:8]
        shortlisted = score_result["score"] >= 70

        job_data["candidates"].append({
            "candidate_id": candidate_id,
            "name": parsed_data.get("name"),
            "email": parsed_data.get("email"),
            "email_confidence": email_confidence,
            "skills": parsed_data.get("skills", []),
            "experience_years": parsed_data.get("experience_years"),
            "score": score_result["score"],
            "shortlisted": shortlisted,
            "resume_file": file["name"],
            "confidence": parsed_data.get("confidence", 0)
        })

    job_data["candidates"] = rank_candidates(job_data["candidates"])

    for candidate in job_data["candidates"]:
        append_candidate({
            "job_id": job_id,
            "role": role,
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "email": candidate["email"],
            "email_confidence": candidate["email_confidence"],
            "skills": ", ".join(candidate["skills"]),
            "experience_years": candidate["experience_years"],
            "score": candidate["score"],
            "shortlisted": candidate["shortlisted"],
            "resume_file": candidate["resume_file"],
            "confidence": candidate["confidence"],
            "rank": candidate["rank"],
            "rank_score": round(candidate["rank_score"], 2)
        })

    screening_db[job_id] = job_data

    return {
        "message": "Google Drive resumes processed & ranked successfully",
        "job_id": job_id,
        "total_resumes": len(job_data["candidates"]),
        "shortlisted": len([c for c in job_data["candidates"] if c["shortlisted"]])
    }



@app.post("/candidates/{candidate_id}/start-interview")
def start_interview(candidate_id: str):
    candidate = None
    job = None

    for job_data in screening_db.values():
        for c in job_data["candidates"]:
            if c["candidate_id"] == candidate_id:
                candidate = c
                job = job_data
                break

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate["interview"] = {
        "started": True,
        "completed": False,
        "qna": []
    }

    question = generate_interview_question(
        job_description=job["role"],
        resume_text=candidate.get("resume_text", ""),
        previous_qna=[]
    )

    return {
        "candidate_id": candidate_id,
        "question": question,
        "round": 1
    }


@app.post("/candidates/{candidate_id}/answer")
def submit_interview_answer(
    candidate_id: str,
    answer: str = Form(...)
):
    candidate = None
    job = None

    for job_data in screening_db.values():
        for c in job_data["candidates"]:
            if c["candidate_id"] == candidate_id:
                candidate = c
                job = job_data
                break

    if not candidate or not candidate.get("interview", {}).get("started"):
        raise HTTPException(status_code=400, detail="Interview not started")

    interview = candidate["interview"]
    round_no = len(interview["qna"]) + 1

    # Save Q&A
    interview["qna"].append({
        "round": round_no,
        "question": "Dynamic AI Question",
        "answer": answer
    })

    # Save EACH Q&A to Google Sheets
    append_candidate({
        "job_id": job["job_id"],
        "candidate_id": candidate_id,
        "interview_round": round_no,
        "question": "Dynamic AI Question",
        "answer": answer
    })

    # Stop after 5 questions
    if round_no >= 5:
        evaluation = evaluate_interview(interview["qna"])

        candidate["interview"]["completed"] = True
        candidate["interview"]["evaluation"] = evaluation

        # Save FINAL evaluation to Google Sheets
        append_candidate({
            "job_id": job["job_id"],
            "candidate_id": candidate_id,
            "skill_fit": evaluation.get("skill_fit"),
            "communication": evaluation.get("communication"),
            "problem_solving": evaluation.get("problem_solving"),
            "culture_fit": evaluation.get("culture_fit"),
            "final_score": evaluation.get("final_score"),
            "recommendation": evaluation.get("recommendation"),
            "feedback": evaluation.get("feedback")
        })

        return {
            "evaluation": evaluation
        }

    # Generate NEXT question
    next_question = generate_interview_question(
        job_description=job["role"],
        resume_text=candidate.get("resume_text", ""),
        previous_qna=interview["qna"]
    )

    return {
        "question": next_question,
        "round": round_no + 1
    }


# =================================================
# HR: View Results
# =================================================
@app.get("/jobs/{job_id}/results")
def get_screening_results(job_id: str):
    job = screening_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# =================================================
# Health Check
# =================================================
@app.get("/")
def health():
    return {"status": "Backend running"}





