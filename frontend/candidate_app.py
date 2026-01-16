import streamlit as st
import requests

# -----------------------------
# Backend configuration
# -----------------------------
BACKEND_URL = st.secrets.get("BACKEND_URL")

if not BACKEND_URL:
    st.error("Backend URL not configured")
    st.stop()

# -----------------------------
# UI
# -----------------------------
st.title("Job Application Portal")

job_id = st.query_params.get("job_id")

if isinstance(job_id, list):
    job_id = job_id[0]

if not job_id:
    st.info("Please use the application link provided by HR.")
    st.stop()

st.subheader(f"Applying for Job ID: {job_id}")

name = st.text_input("Full Name")
email = st.text_input("Email")
resume = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

# -----------------------------
# Submit Application
# -----------------------------
if st.button("Submit Application"):
    if not name or not email or not resume:
        st.error("All fields are required")
        st.stop()

    # Prepare multipart form data
    files = {
        "file": (resume.name, resume.getvalue())
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
    except requests.exceptions.ConnectionError:
        st.warning("Backend is waking up. Please try again in a few seconds.")
        st.stop()
    except requests.exceptions.Timeout:
        st.error("Backend timeout. Please retry.")
        st.stop()

    if response.status_code == 200:
        res = response.json()
        st.success("Application submitted successfully 🎉")

        if res.get("shortlisted"):
            st.info("You have been shortlisted! Please check your email for next steps.")
        else:
            st.info("Thank you for applying. We will get back to you.")

    else:
        st.error("Submission failed. Please try again.")
