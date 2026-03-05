import streamlit as st
import requests

st.set_page_config(page_title="AI Resume Ranker", layout="wide")

st.title("🤖 AI Resume Screening & Candidate Ranking")
st.markdown("---")

# Input Section
jd = st.text_area("Paste Job Description (JD) here:", height=200)
uploaded_files = st.file_uploader("Upload Resumes (Multiple PDFs allowed)", type="pdf", accept_multiple_files=True)

# app/frontend.py mein button logic ke andar ye add karo
if st.button("Rank Now"):
    if jd and uploaded_files:
        try:
            with st.spinner('Analyzing...'):
                files = [("files", (f.name, f.getvalue(), "application/pdf")) for f in uploaded_files]
                data = {"job_description": jd}
                
                # Timeout add karna zaroori hai
                response = requests.post("http://127.0.0.1:8000/rank", data=data, files=files, timeout=10)
                
                if response.status_code == 200:
                    results = response.json()['rankings']
                    st.success("Analysis Complete!")
                    st.table(results)
                else:
                    st.error(f"Backend Error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("🚨 Backend (FastAPI) is NOT running. Please start Terminal 1 first!")
    else:
        st.warning("Please upload files and JD.")