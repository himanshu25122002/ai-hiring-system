import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.title("HR Dashboard")

job_id = st.text_input("Enter Job ID")

if st.button("Fetch Candidates"):
    response = requests.get(f"{BACKEND_URL}/jobs/{job_id}/candidates")

    if response.status_code != 200:
        st.error("Invalid Job ID")
    else:
        data = response.json()["candidates"]

        if not data:
            st.info("No candidates yet")
        else:
            for c in data:
                st.subheader(f"Candidate ID: {c['candidate_id']}")
                st.write("Resume Score:", c["score"])
                st.write("Shortlisted:", c["shortlisted"])
                st.write("Interview Completed:", c["interview_completed"])
                st.write("Interview Score:", c["interview_score"])
                st.write("Final Recommendation:", c["final_recommendation"])
                st.divider()
