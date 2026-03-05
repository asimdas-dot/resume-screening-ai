import streamlit as st
import pandas as pd
import re
import io
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- NLP LOGIC ---
def clean_text(text):
    if not text: return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def rank_resumes(job_description, resumes_list):
    cleaned_jd = clean_text(job_description)
    cleaned_resumes = [clean_text(r['text']) for r in resumes_list]
    
    if not cleaned_jd or not any(cleaned_resumes):
        return []

    corpus = [cleaned_jd] + cleaned_resumes
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    results = []
    for i, score in enumerate(scores):
        results.append({
            "Rank": 0, # Placeholder
            "Candidate Name": resumes_list[i]['filename'],
            "Match Score (%)": round(float(score) * 100, 2)
        })
    
    # Sort and add Rank
    ranked = sorted(results, key=lambda x: x['Match Score (%)'], reverse=True)
    for idx, item in enumerate(ranked):
        item["Rank"] = idx + 1
    return ranked

# --- STREAMLIT UI ---
st.set_page_config(page_title="AI Resume Screener", layout="wide")

st.title("🤖 AI Resume Screening & Ranking System")
st.info("Direct Mode: No Backend API needed. Processing locally.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Job Details")
    jd_input = st.text_area("Paste Job Description here:", height=300)

with col2:
    st.subheader("Upload Resumes")
    uploaded_files = st.file_uploader("Upload PDF Resumes", type="pdf", accept_multiple_files=True)

if st.button("🚀 Start AI Ranking"):
    if jd_input and uploaded_files:
        with st.spinner('Reading PDFs and calculating scores...'):
            resumes_data = []
            for file in uploaded_files:
                try:
                    text = extract_text(io.BytesIO(file.getvalue()))
                    resumes_data.append({"filename": file.name, "text": text})
                except Exception as e:
                    st.error(f"Error reading {file.name}: {e}")

            if resumes_data:
                final_rankings = rank_resumes(jd_input, resumes_data)
                
                st.success("Ranking Complete!")
                st.markdown("### 🏆 Candidate Ranking")
                
                # Display as a nice Table
                df = pd.DataFrame(final_rankings)
                st.table(df)
                
                # Chart
                st.bar_chart(df.set_index('Candidate Name')['Match Score (%)'])
            else:
                st.error("Could not extract text from any PDF.")
    else:
        st.warning("Please provide both Job Description and Resumes.")