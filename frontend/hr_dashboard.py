import streamlit as st
import requests
import pandas as pd
import os

# -----------------------------
# CONFIG
# -----------------------------
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://127.0.0.1:8000")
GOOGLE_SHEET_CSV_URL = st.secrets.get(
    "GOOGLE_SHEET_CSV_URL",
    ""  # public CSV export link
)

st.set_page_config(
    page_title="HR Resume Screening Dashboard",
    layout="wide"
)

st.title("🧑‍💼 AI Resume Screening – HR Dashboard")

# -----------------------------
# JOB INPUT SECTION
# -----------------------------
st.subheader("📌 Job Details")

col1, col2 = st.columns(2)

with col1:
    role = st.text_input("Job Role")
    required_skills = st.text_input("Required Skills (comma-separated)")

with col2:
    experience_level = st.text_input("Experience Level")
    culture_traits = st.text_input("Culture Traits (optional)")

st.divider()

# -----------------------------
# RESUME INPUT SECTION
# -----------------------------
st.subheader("📂 Resume Input")

upload_mode = st.radio(
    "Choose resume source",
    ["Upload Multiple Resumes", "Google Drive Folder Link"]
)

resumes = None
drive_link = None

if upload_mode == "Upload Multiple Resumes":
    resumes = st.file_uploader(
        "Upload resumes (PDF/DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )
else:
    drive_link = st.text_input("Google Drive Folder Link")

st.divider()

# -----------------------------
# START SCREENING
# -----------------------------
if st.button("🚀 Start Resume Screening"):
    if not role or not required_skills or not experience_level:
        st.error("Please fill all required job details")
        st.stop()

    with st.spinner("Processing resumes..."):
        try:
            if upload_mode == "Upload Multiple Resumes":
                if not resumes:
                    st.error("Please upload resumes")
                    st.stop()

                files = [("resumes", r) for r in resumes]

                response = requests.post(
                    f"{BACKEND_URL}/screen-resumes",
                    data={
                        "role": role,
                        "required_skills": required_skills,
                        "experience_level": experience_level,
                        "culture_traits": culture_traits
                    },
                    files=files,
                    timeout=300
                )

            else:
                response = requests.post(
                    f"{BACKEND_URL}/screen-drive-folder",
                    json={
                        "role": role,
                        "required_skills": required_skills,
                        "experience_level": experience_level,
                        "culture_traits": culture_traits,
                        "drive_folder_link": drive_link
                    },
                    timeout=300
                )

            if response.status_code == 200:
                data = response.json()
                st.success("✅ Resume screening completed")
                st.session_state["job_id"] = data["job_id"]
            else:
                st.error("Screening failed")

        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# -----------------------------
# VIEW RESULTS FROM GOOGLE SHEETS
# -----------------------------
st.subheader("📊 Ranked Candidates")

if GOOGLE_SHEET_CSV_URL:
    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

        if df.empty:
            st.info("No candidates yet. Upload resumes to begin.")
            st.stop()

    # Optional filter by job_id
        job_id = st.session_state.get("job_id")
        if job_id and "job_id" in df.columns:
            df = df[df["job_id"] == job_id]

    # 🔐 SAFE sort (only if column exists)
        if "score" in df.columns:
            df = df.sort_values("score", ascending=False)

    # Shortlist filter
        show_shortlisted = st.checkbox("Show only shortlisted candidates")
        if show_shortlisted and "shortlisted" in df.columns:
            df = df[df["shortlisted"] == True]

    # ✅ Display ONLY existing columns
        visible_columns = [
            col for col in [
               
                "job_id",
                "role",
                "candidate_id",
                "name",
                "email",
                "skills",
                "experience_years",
                "score",
                "shortlisted",
                "resume_file",
                "confidence"

            ]
            if col in df.columns
        ]

        st.dataframe(
            df[visible_columns],
            use_container_width=True
        )

    except Exception as e:
        st.error("Failed to read Google Sheet")
        st.exception(e)



else:
    st.info("Google Sheet CSV link not configured")



