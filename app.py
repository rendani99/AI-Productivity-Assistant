import streamlit as st
import os
from google import genai
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPTS
import time

# --- SYSTEM CONFIGURATION ---
load_dotenv()

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except (KeyError, FileNotFoundError, AttributeError, Exception):
    api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.error("SYSTEM AUTHENTICATION FAILED: API Key missing.")
    st.stop()

# --- THE EXECUTIVE AUSTIN THEME ---
def apply_austin_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #050505;
            background-image: radial-gradient(circle at 2px 2px, rgba(0, 242, 255, 0.08) 1px, transparent 0);
            background-size: 35px 35px;
            color: #ccd6f6;
            font-family: 'JetBrains Mono', monospace;
        }
        section[data-testid="stSidebar"] {
            background: rgba(10, 25, 47, 0.95) !important;
            backdrop-filter: blur(15px);
            border-right: 1px solid #00f2ff;
        }
        .result-card {
            background: rgba(17, 34, 64, 0.6);
            border: 1px solid #00f2ff;
            padding: 25px;
            border-radius: 4px;
            margin-top: 20px;
            position: relative;
            color: #64ffda;
        }
        .result-card::before {
            content: "INTEL_OUTPUT_v3.2";
            position: absolute;
            top: -10px; left: 15px;
            background: #00f2ff; color: #050505;
            font-size: 10px; padding: 2px 10px; font-weight: bold;
        }
        .stButton>button {
            background: transparent; color: #00f2ff; border: 1px solid #00f2ff;
            border-radius: 2px; text-transform: uppercase; letter-spacing: 2px;
            transition: all 0.4s; height: 3.5em; width: 100%;
        }
        .stButton>button:hover {
            background: #00f2ff !important; color: #050505 !important;
            box-shadow: 0 0 30px rgba(0, 242, 255, 0.5);
        }
        .stTextArea textarea {
            background-color: rgba(2, 12, 27, 0.8) !important;
            color: #00f2ff !important; border: 1px solid #233554 !important;
        }
        [data-testid="stMetricValue"] { color: #64ffda !important; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# --- DATA PERSISTENCE ---
SAVE_FILE = "last_session.txt"
def save_session(text):
    with open(SAVE_FILE, "w", encoding="utf-8") as f: f.write(text)
def load_session():
    return open(SAVE_FILE, "r", encoding="utf-8").read() if os.path.exists(SAVE_FILE) else ""

if "user_input" not in st.session_state:
    st.session_state.user_input = load_session()
if "ai_result" not in st.session_state:
    st.session_state.ai_result = ""

st.set_page_config(page_title="AUSTIN AI", layout="wide")
apply_austin_theme()

# --- HEADER BRANDING ---
c1, c2 = st.columns([0.8, 0.2])
with c1:
    st.markdown("<h1 style='letter-spacing: 4px; color: #00f2ff; margin-bottom: 0;'>AUSTIN AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64ffda; font-weight: 500; font-size: 1.2rem; letter-spacing: 2px;'>BSc MATHEMATICAL SCIENCES | UNIVERSITY OF LIMPOPO</p>", unsafe_allow_html=True)
with c2:
    if st.button("[ RESET_CORE ]"):
        if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
        st.session_state.user_input = ""
        st.session_state.ai_result = ""
        st.rerun()

st.markdown("<hr style='border: 0.5px solid #233554;'>", unsafe_allow_html=True)

# --- SIDEBAR HUD ---
with st.sidebar:
    st.markdown("<h3 style='color: #00f2ff;'>CONTROL_PANEL</h3>", unsafe_allow_html=True)
    task = st.selectbox("ACTIVE_MODULE", list(SYSTEM_PROMPTS.keys()))
    
    st.divider()
    tone = st.select_slider("TONE_SETTING", options=["Casual", "Friendly", "Professional", "Urgent"])
    language = st.selectbox("OUTPUT_LINGUA", ["English", "isiZulu", "Afrikaans", "Sesotho", "French"])

    st.divider()
    st.markdown("<b style='color: #64ffda;'>ENGINEER_STAMP</b>", unsafe_allow_html=True)
    st.markdown("<p style='color: #ccd6f6; margin-bottom: 0;'>R. Austin Mmola</p>", unsafe_allow_html=True)
    st.caption("Computer Science & Statistics")
    st.caption("Midrand Node // 2026")

# --- WORKSPACE ---
tab_cmd, tab_data = st.tabs(["[ TERMINAL ]", "[ METRICS ]"])

with tab_cmd:
    user_input = st.text_area("DATA_INJECTION_POINT", 
                              value=st.session_state.user_input, 
                              height=320)

    if user_input != st.session_state.user_input:
        st.session_state.user_input = user_input
        save_session(user_input)

    if st.button("EXECUTE_TRANSFORMATION"):
        if user_input:
            with st.status("Neural Synthesis in progress...", expanded=True) as status:
                try:
                    time.sleep(0.4)
                    lang_inst = f"Output in {language}." if language != "English" else ""
                    final_prompt = f"Role: {SYSTEM_PROMPTS[task]}\\nConstraint: {tone}. {lang_inst}\\nData: {user_input}"
                    
                    # --- THE FINAL RECOVERY LOOP ---
                    response = None
                    models_to_try = ["gemini-1.5-flash", "gemini-1.0-pro"]
                    
                    for model_name in models_to_try:
                        try:
                            response = client.models.generate_content(
                                model=model_name,
                                contents=final_prompt
                            )
                            if response:
                                break
                        except Exception:
                            continue
                    
                    if response:
                        st.session_state.ai_result = response.text
                        status.update(label="SYNTHESIS COMPLETE", state="complete", expanded=False)
                    else:
                        st.error("ENGINE FAILURE: Permission denied. Please check your API project settings.")
                except Exception as e:
                    st.error(f"SYSTEM_ERROR: {str(e)}")

# --- OUTPUT ARCHITECTURE ---
if st.session_state.ai_result:
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(st.session_state.ai_result)
    st.markdown('</div>', unsafe_allow_html=True)
    st.download_button("📩 EXPORT_LOG", st.session_state.ai_result, file_name="AUSTIN_AI_DATA.txt")

# --- FOOTER ---
st.markdown("<p style='text-align: center; color: #495670; font-size: 0.8rem; margin-top: 50px;'>AUSTIN // BSc MATHEMATICAL SCIENCES // 2026</p>", unsafe_allow_html=True)