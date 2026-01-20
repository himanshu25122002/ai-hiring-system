import streamlit as st
import requests
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://127.0.0.1:8000")

# Public CSV export link of Google Sheet
GOOGLE_SHEET_CSV_URL = st.secrets.get(
    "GOOGLE_SHEET_CSV_URL",
    ""  # must be set in Streamlit secrets
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

# -----------------------------
# START SCREENING
# -----------------------------
if st.button("🚀 Start Resume Screening"):
    if not role or not required_skills or not experience_level:
        st.warning("Please fill all job details.")
    else:
        with st.spinner("Processing resumes..."):
            try:
                if upload_mode == "Upload Multiple Resumes":
                    if not resumes:
                        st.warning("Please upload resumes.")
                    else:
                        files = [("resumes", r) for r in resumes]
                        response = requests.post(
                            f"{BACKEND_URL}/screen-resumes",
                            data={
                                "role": role,
                                "required_skills": required_skills,
                                "experience_level": experience_level,
                                "culture_traits": culture_traits,
                            },
                            files=files,
                            timeout=120
                        )
                else:
                    if not drive_link:
                        st.warning("Please enter Google Drive folder link.")
                    else:
                        response = requests.post(
                            f"{BACKEND_URL}/screen-resumes-drive",
                            data={
                                "role": role,
                                "required_skills": required_skills,
                                "experience_level": experience_level,
                                "culture_traits": culture_traits,
                                "drive_link": drive_link
                            },
                            timeout=120
                        )

                if response.status_code == 200:
                    data = response.json()
                    st.success(
                        f"Processed {data['total_resumes']} resumes | "
                        f"Shortlisted: {data['shortlisted']}"
                    )
                    st.session_state["job_id"] = data["job_id"]
                else:
                    st.error("Backend error while screening resumes")

            except Exception as e:
                st.error("Failed to connect to backend")
                st.exception(e)

st.divider()

# -----------------------------
# RANKED CANDIDATES SECTION
# -----------------------------
st.subheader("📊 Ranked Candidates")

if not GOOGLE_SHEET_CSV_URL:
    st.info("Google Sheet CSV link not configured.")
else:
    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

        if df.empty:
            st.warning("No candidates found yet.")
        else:
            # Optional filter by job_id
            job_id = st.session_state.get("job_id")
            if job_id and "job_id" in df.columns:
                df = df[df["job_id"] == job_id]

            # Sort by interview score first, then rank_score
            if "interview_score" in df.columns:
                df = df.sort_values(
                    by=["interview_score", "rank_score"],
                    ascending=False
                )
            elif "rank_score" in df.columns:
                df = df.sort_values(by="rank_score", ascending=False)

            # Shortlist filter
            show_shortlisted = st.checkbox("Show only shortlisted candidates")
            if show_shortlisted and "shortlisted" in df.columns:
                df = df[df["shortlisted"] == True]

            # Highlight strong interview performers
            if "interview_score" in df.columns:
                df["Interview Status"] = df["interview_score"].apply(
                    lambda x: "🔥 Strong" if x >= 80 else "⚠️ Moderate" if x >= 60 else "❌ Weak"
                )

            visible_columns = [
                col for col in [
                    "rank",
                    "name",
                    "email",
                    "score",
                    "interview_score",
                    "Interview Status",
                    "recommendation",
                    "shortlisted",
                    "confidence"
                ] if col in df.columns
            ]

            st.dataframe(
                df[visible_columns],
                use_container_width=True
            )

    except Exception as e:
        st.warning("Google Sheet not accessible yet")
        st.exception(e)

show_final_selected = st.checkbox("Show final interview candidates only")

if show_final_selected and "final_selected" in df.columns:
    df = df[df["final_selected"] == True]

st.dataframe(
    df.style.apply(
        lambda row: ["background-color: #dcfce7" if row.get("final_selected") else "" for _ in row],
        axis=1
    )
)



