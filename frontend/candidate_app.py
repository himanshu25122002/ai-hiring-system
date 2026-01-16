import streamlit as st
import requests

BACKEND_URL = st.secrets.get("BACKEND_URL")

if not BACKEND_URL:
    st.error("BACKEND_URL not set in Streamlit secrets")
    st.stop()

st.title("Job Application Portal")

# Get job_id from URL
job_id = st.query_params.get("job_id")
if isinstance(job_id, list):
    job_id = job_id[0]

if not job_id:
    st.error("Invalid application link. Job ID missing.")
    st.stop()

st.subheader(f"Applying for Job ID: {job_id}")

name = st.text_input("Full Name")
email = st.text_input("Email")
resume = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

if st.button("Submit Application"):
    if not name or not email or not resume:
        st.error("All fields are required")
        st.stop()

    files = {
        "file": (resume.name, resume, resume.type)
    }

    data = {
        "name": name,
        "email": email
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/jobs/{job_id}/upload_resume",
            files=files,
            data=data,
            timeout=120
        )
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        st.stop()

    if response.status_code == 200:
        st.success("✅ Application submitted successfully!")
        st.json(response.json())
    else:
        st.error(f"❌ Submission failed ({response.status_code})")
        st.text(response.text)
