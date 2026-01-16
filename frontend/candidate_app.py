import streamlit as st
import requests
import os

BACKEND_URL = st.secrets.get("BACKEND_URL")

if not BACKEND_URL:
    st.error("Backend URL not configured")
    st.stop()




BACKEND_URL = "http://127.0.0.1:8000"

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
        files = {"file": resume}
        try:

            r = requests.post(
                f"{BACKEND_URL}/jobs/{job_id}/upload_resume",
                files=files,
                data=data,

                timeout=120

            )
        except requests.exceptions.ConnectionError:
            st.warning("Backend is waking up. Please click Submit again in a few seconds.")
            st.stop()
        except requests.exceptions.Timeout:
            st.error("Backend took too long. Please retry.")
            st.stop()



        if r.status_code == 200:
            st.success("Application submitted successfully!")
        else:
            st.error("Submission failed")



