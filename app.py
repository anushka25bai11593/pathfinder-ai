import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import json
import os
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="PathFinder AI",
    page_icon="🚀",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- API CONFIG ----------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# ---------------- FUNCTION ----------------
def get_structured_analysis(resume_text, jd_text):
    prompt = f"""
    Act as a Senior Technical Recruiter. Analyze the Resume against the Job Description.

    Return ONLY a valid JSON:
    {{
      "match_score": number (0-100),
      "missing_skills": [3-5 skills],
      "strengths": [2 strengths],
      "roadmap": {{
        "Month 1": "...",
        "Month 2": "...",
        "Month 3": "..."
      }}
    }}

    Resume: {resume_text}
    JD: {jd_text}
    """
    response = model.generate_content(prompt)

    text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

# ---------------- HEADER ----------------
st.markdown("""
# 🚀 PathFinder AI  
### Bridge the Gap to Your Next Internship
""")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Settings")
    role = st.selectbox("Target Role", ["SDE", "Data Scientist", "AI/ML Engineer"])
    st.markdown("---")
    st.caption("Powered by Gemini AI")

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    jd = st.text_area(
        "📄 Job Description",
        placeholder="Paste job description here...",
        height=200
    )

with col2:
    uploaded_file = st.file_uploader("📤 Upload Resume (PDF)", type="pdf")

# ---------------- BUTTON ----------------
st.markdown("<br>", unsafe_allow_html=True)
analyze = st.button("🚀 Analyze & Build Roadmap", use_container_width=True)

# ---------------- SESSION STATE ----------------
if "data" not in st.session_state:
    st.session_state.data = None

# ---------------- MAIN LOGIC ----------------
if analyze:
    if uploaded_file and jd:

        with st.spinner("Analyzing your resume... 🤖"):
            
            # Extract PDF text
            reader = pdf.PdfReader(uploaded_file)
            resume_text = ""
            for page in reader.pages:
                if page.extract_text():
                    resume_text += page.extract_text()

            # Resume preview
            st.subheader("📄 Resume Preview")
            st.text(resume_text[:500])

            # AI Analysis
            data = get_structured_analysis(resume_text, jd)
            st.session_state.data = data

    else:
        st.warning("⚠️ Please upload resume and paste job description.")

# ---------------- DISPLAY RESULTS ----------------
if st.session_state.data:

    data = st.session_state.data
    st.divider()

    # -------- MATCH SCORE --------
    st.markdown("## 📊 Match Score")
    st.progress(data['match_score'] / 100)
    st.metric("Score", f"{data['match_score']}%")

    # -------- PIE CHART --------
    labels = ["Matched", "Missing"]
    sizes = [data['match_score'], 100 - data['match_score']]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    st.pyplot(fig)

    # -------- SKILLS + STRENGTHS --------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🛠️ Missing Skills")
        for skill in data['missing_skills']:
            st.markdown(f"<div class='card'>⚡ {skill}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("### 💪 Strengths")
        for s in data['strengths']:
            st.markdown(f"<div class='card'>✅ {s}</div>", unsafe_allow_html=True)

    # -------- ROADMAP --------
    st.markdown("## 📅 3-Month Roadmap")

    col1, col2, col3 = st.columns(3)
    months = list(data['roadmap'].items())

    for i, col in enumerate([col1, col2, col3]):
        with col:
            st.markdown(f"""
            <div class='card'>
                <h4>{months[i][0]}</h4>
                <p>{months[i][1]}</p>
            </div>
            """, unsafe_allow_html=True)

    # -------- DOWNLOAD --------
    st.download_button(
        "📥 Download Roadmap",
        json.dumps(data, indent=2),
        file_name="career_roadmap.json"
    )

    # -------- RE-ANALYZE --------
    if st.button("🔄 Re-analyze"):
        st.session_state.data = None
        st.rerun()