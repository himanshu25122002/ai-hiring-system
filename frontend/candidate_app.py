import streamlit as st
import requests

BACKEND_URL = st.secrets.get("BACKEND_URL")

if not BACKEND_URL:
    st.error("Backend URL not configured")
    st.stop()

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
resume = st.file_uploader("Upload Resume (PDF/DOCX)")

if st.button("Submit Application"):
    if not name or not email or not resume:
        st.error("All fields are required")
    else:
        try:
            r = requests.post(
                f"{BACKEND_URL}/jobs/{job_id}/upload_resume",
                files={"file": resume},
                data={"name": name, "email": email},
                timeout=120
            )

            if r.status_code == 200:
                st.success("Application submitted successfully!")
            else:
                st.error(f"Submission failed ({r.status_code})")
                st.text(r.text)

        except requests.exceptions.ConnectionError:
            st.warning("Backend is waking up. Please retry.")
        except requests.exceptions.Timeout:
            st.error("Backend timeout. Try again.")
