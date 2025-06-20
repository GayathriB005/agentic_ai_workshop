# streamlit_app.py

import streamlit as st
import os
from agent_1_market_scraper import run_marketplace_scraper
from agent_2_audience_detector import run_audience_detector
from agent_3_feedback_synthesizer import run_feedback_synthesizer_live  # Updated
from agent_4_persona_generator import run_persona_generator
from agent_5_persona_refiner import run_persona_refiner

st.set_page_config(page_title="Agentic AI System", layout="centered")
st.title("🧠 Agentic AI System for Market Research and Persona Generation")

# Initialize session state
for key in [
    "agent1_output", "agent2_output",
    "agent3_feedback_output", "agent4_output", "agent5_output"
]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ----------------- Unified Button for All Agents ------------------
st.header("🚀 Run All Agents")

title = st.text_input("Project Title")
keywords = st.text_input("Keywords (comma-separated)")
app_id = st.text_input("📲 Enter Google Play App ID (e.g., com.todoist)")

if st.button("Run Full Workflow"):
    with st.spinner("Running Agent 1..."):
        agent1_output = run_marketplace_scraper(title, keywords)
        st.session_state.agent1_output = agent1_output
        st.markdown("### ✅ Agent 1 Output")
        st.markdown(agent1_output)

    with st.spinner("Running Agent 2..."):
        agent2_output = run_audience_detector(agent1_output)
        st.session_state.agent2_output = agent2_output
        st.markdown("### 🎯 Agent 2 Output")
        st.markdown(agent2_output)

    with st.spinner("Running Agent 3..."):
        feedback_output = run_feedback_synthesizer_live(app_id)
        st.session_state.agent3_feedback_output = feedback_output
        st.markdown("### 📊 Agent 3 Output")
        st.markdown(feedback_output)

    with st.spinner("Running Agent 4..."):
        personas = run_persona_generator(agent2_output, feedback_output)
        st.session_state.agent4_output = personas
        st.markdown("### 👤 Agent 4 Output")
        st.markdown(personas)

    with st.spinner("Running Agent 5..."):
        refined = run_persona_refiner(personas, feedback_output)
        st.session_state.agent5_output = refined
        st.markdown("### 🧪 Agent 5 Output")
        st.markdown(refined)

# ------------------ FOOTER --------------------
st.markdown("""
    <hr style="margin-top: 3rem;">
    <footer style='text-align: center; font-size: 0.9rem; margin-top: 1rem; color: gray;'>
        Built with ❤️ using Streamlit, LangChain, and Gemini | ©2025 Agentic Persona AI
    </footer>
""", unsafe_allow_html=True)
