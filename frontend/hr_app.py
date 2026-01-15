import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.title("HR Job Creation Portal")

with st.form("job_form"):
    job_title = st.text_input("Job Title")
    job_description = st.text_area("Job Description")
    skills = st.text_input("Required Skills")
    experience = st.selectbox("Experience", ["0-1", "1-3", "3-5", "5+"])
    culture_traits = st.text_area("Culture Traits")

    submit = st.form_submit_button("Create Job")

if submit:
    payload = {
        "job_title": job_title,
        "job_description": job_description,
        "skills": skills,
        "experience": experience,
        "culture_traits": culture_traits
    }

    res = requests.post(f"{BACKEND_URL}/jobs/create", json=payload)

    if res.status_code == 200:
        data = res.json()
        st.success("Job Created Successfully!")
        st.write("Job ID:", data["job_id"])
        st.write("Candidate Application Link:")
        st.code(f"http://localhost:8501/?job_id={data['job_id']}")
