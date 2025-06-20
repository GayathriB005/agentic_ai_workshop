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

# ----------------- Agent 1 ------------------
st.header("🔍 Agent 1: Marketplace Scraper")

title = st.text_input("Project Title", "StudyBuddy")
keywords = st.text_input("Keywords (comma-separated)", "student, focus, education")

if st.button("Run Agent 1"):
    with st.spinner("Scraping real competitors..."):
        agent1_output = run_marketplace_scraper(title, keywords)
        st.session_state.agent1_output = agent1_output
        st.markdown("### ✅ Extracted Competitor Summary")
        st.markdown(agent1_output)

# ----------------- Agent 2 ------------------
st.markdown("---")
st.header("🧬 Agent 2: Audience Pattern Detector")

if st.session_state.agent1_output:
    with st.expander("📦 Auto-filled Metadata from Agent 1"):
        st.code(st.session_state.agent1_output, language="markdown")

    if st.button("Run Agent 2"):
        with st.spinner("Analyzing audience patterns..."):
            agent2_output = run_audience_detector(st.session_state.agent1_output)
            st.session_state.agent2_output = agent2_output
            st.markdown("### 🎯 Inferred Target Audience")
            st.markdown(agent2_output)
else:
    st.info("Please run Agent 1 first to enable Agent 2.")

# ----------------- Agent 3 ------------------
st.markdown("---")
st.header("🗣️ Agent 3: User Feedback Synthesizer (Real-Time Google Play Reviews)")

app_id = st.text_input("📲 Enter Google Play App ID (e.g., com.todoist)", value="com.todoist")

if st.button("Run Agent 3"):
    with st.spinner("Scraping live user reviews..."):
        feedback_output = run_feedback_synthesizer_live(app_id)
        st.session_state.agent3_feedback_output = feedback_output
        st.markdown("### 📊 User Feedback Summary (Live)")
        st.markdown(feedback_output)

# ----------------- Agent 4 ------------------
st.markdown("---")
st.header("👤 Agent 4: Persona Generator")

if st.session_state.agent3_feedback_output:
    with st.expander("📄 Feedback Summary from Agent 3"):
        st.code(st.session_state.agent3_feedback_output, language="markdown")

    audience_input = (
        st.session_state.agent2_output
        if st.session_state.agent2_output
        else st.session_state.agent1_output
    )

    if st.button("Run Agent 4"):
        with st.spinner("Generating user personas..."):
            personas = run_persona_generator(
                audience_input,
                st.session_state.agent3_feedback_output
            )
            st.session_state.agent4_output = personas
            st.markdown("### 🧑‍💼 Generated Personas")
            st.markdown(personas)
else:
    st.info("Please run Agent 3 (and optionally Agent 2) to generate user personas.")

# ----------------- Agent 5 ------------------
st.markdown("---")
st.header("🧪 Agent 5: Persona Refiner & Validator")

if st.session_state.agent3_feedback_output and st.session_state.agent4_output:
    with st.expander("📄 Draft Personas from Agent 4"):
        st.code(st.session_state.agent4_output, language="markdown")

    if st.button("Run Agent 5"):
        with st.spinner("Refining and validating personas..."):
            refined = run_persona_refiner(
                st.session_state.agent4_output,
                st.session_state.agent3_feedback_output
            )
            st.session_state.agent5_output = refined
            st.markdown("### ✅ Finalized Personas (Ready for Presentation)")
            st.markdown(refined)
else:
    st.info("Please run Agent 3 and Agent 4 before running the Persona Refiner.")
