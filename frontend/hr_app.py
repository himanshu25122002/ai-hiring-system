import streamlit as st
import requests
import os

st.set_page_config(page_title="HR Job Creation", layout="centered")

st.title("HR – Create Job")

# Load backend URL safely
BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL:
    st.error("BACKEND_URL is not set in Streamlit secrets")
    st.stop()

# Job form
job_title = st.text_input("Job Title")
job_description = st.text_area("Job Description")
skills = st.text_input("Required Skills")
experience = st.text_input("Experience")
culture_traits = st.text_input("Culture Traits (optional)")

if st.button("Create Job"):
    if not job_title or not job_description:
        st.warning("Please fill required fields")
    else:
        payload = {
            "job_title": job_title,
            "job_description": job_description,
            "skills": skills,
            "experience": experience,
            "culture_traits": culture_traits
        }

        try:
            with st.spinner("Creating job..."):
                res = requests.post(
                    f"{BACKEND_URL}/jobs/create",
                    json=payload,
                    timeout=15
                )

            if res.status_code == 200:
                data = res.json()
                st.success("Job created successfully 🎉")
                st.code(data["application_link"], language="text")
            else:
                st.error(f"Backend error: {res.text}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Is it awake?")
        except requests.exceptions.Timeout:
            st.error("⏳ Backend timeout. Please retry.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
