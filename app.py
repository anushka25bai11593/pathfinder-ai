import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import json
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="PathFinder AI",
    page_icon="🚀",
    layout="wide"
)

# ---------------- CUSTOM CSS (FUTURISTIC THEME) ----------------
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
}

/* Main container */
.main {
    background: transparent;
}

/* Title */
h1 {
    text-align: center;
    font-size: 3rem;
    background: linear-gradient(90deg, #a855f7, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Cards */
.card {
    background: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.4);
    margin-bottom: 15px;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #a855f7, #6366f1);
    color: white;
    border-radius: 10px;
    height: 3em;
    font-size: 16px;
}

/* Inputs */
textarea, input {
    background-color: rgba(255,255,255,0.05) !important;
    color: white !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.6);
}

</style>
""", unsafe_allow_html=True)

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key=os.getenv("AIzaSyAlvzCUv5jKpHY8rXMEyxtWyl3B-gQb-_Y"))
model = genai.GenerativeModel('gemini-1.5-flash')

# ---------------- AI FUNCTION ----------------
def get_structured_analysis(resume_text, jd_text):
    prompt = f"""
    Act as a Senior Technical Recruiter. Analyze the Resume against the Job Description.

    Return ONLY JSON:
    {{
      "match_score": number,
      "missing_skills": [],
      "strengths": [],
      "roadmap": {{
        "Month 1": "",
        "Month 2": "",
        "Month 3": ""
      }}
    }}

    Resume: {resume_text}
    JD: {jd_text}
    """
    response = model.generate_content(prompt)
    text = response.text.replace("```json", "").replace("```", "")
    return json.loads(text)

# ---------------- HEADER ----------------
st.markdown("""
# 🚀 PathFinder AI  
### ✨ From Rejected → Recruited with GenAI
""")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Control Panel")
    role = st.selectbox("🎯 Target Role", ["SDE", "Data Scientist", "AI/ML Engineer"])
    st.markdown("---")
    st.caption("⚡ Powered by Gemini 1.5 Flash")

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    jd = st.text_area("📄 Job Description", height=220)

with col2:
    uploaded_file = st.file_uploader("📤 Upload Resume", type="pdf")

st.markdown("<br>", unsafe_allow_html=True)

analyze = st.button("🚀 Analyze & Generate Roadmap", use_container_width=True)

# ---------------- SESSION ----------------
if "data" not in st.session_state:
    st.session_state.data = None

# ---------------- MAIN LOGIC ----------------
if analyze:
    if uploaded_file and jd:

        with st.spinner("⚡ Analyzing... entering AI pipeline..."):

            reader = pdf.PdfReader(uploaded_file)
            resume_text = ""
            for page in reader.pages:
                if page.extract_text():
                    resume_text += page.extract_text()

            st.markdown("### 📄 Resume Preview")
            st.code(resume_text[:500])

            data = get_structured_analysis(resume_text, jd)
            st.session_state.data = data

    else:
        st.warning("⚠️ Upload resume + enter job description")

# ---------------- RESULTS ----------------
if st.session_state.data:
    data = st.session_state.data

    st.markdown("---")

    # MATCH SCORE
    st.markdown("## 📊 Match Score")
    st.progress(data['match_score']/100)
    st.markdown(f"<h2 style='text-align:center'>{data['match_score']}%</h2>", unsafe_allow_html=True)

    # SKILLS + STRENGTHS
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🛠 Missing Skills")
        for skill in data['missing_skills']:
            st.markdown(f"<div class='card'>⚡ {skill}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("### 💪 Strengths")
        for s in data['strengths']:
            st.markdown(f"<div class='card'>✅ {s}</div>", unsafe_allow_html=True)

    # ROADMAP
    st.markdown("## 📅 90-Day Career Roadmap")

    col1, col2, col3 = st.columns(3)
    roadmap = list(data['roadmap'].items())

    for i, col in enumerate([col1, col2, col3]):
        with col:
            st.markdown(f"""
            <div class='card'>
            <h3>{roadmap[i][0]}</h3>
            <p>{roadmap[i][1]}</p>
            </div>
            """, unsafe_allow_html=True)

    # DOWNLOAD
    st.download_button(
        "📥 Download Roadmap",
        json.dumps(data, indent=2),
        file_name="roadmap.json"
    )

    # RESET
    if st.button("🔄 Re-analyze"):
        st.session_state.data = None
        st.rerun()