import streamlit as st
import pandas as pd
import google.generativeai as genai

# -------------------- SETUP --------------------

# Replace this with your actual Gemini API key
GOOGLE_API_KEY = "AIzaSyArnGrJB1cpXWhXAT1IQwp7NIrSx_GaB_A"
genai.configure(api_key=GOOGLE_API_KEY)

# Load Gemini 2.0 Flash model
model = genai.GenerativeModel("models/gemini-1.5-flash")

# -------------------- HELPER FUNCTION --------------------

def analyze_kpis(startup_type, kpis):
    prompt = f"""
You are a KPI analysis assistant for startups.

The startup type is: {startup_type}
The founder gave these KPIs:
{kpis}

1. Tell whether each KPI is a vanity metric or impact metric.
2. Suggest better metrics for any vanity metric.
3. Show the result as a markdown table with these columns:
- Metric
- Type (Vanity/Impact)
- Recommendation

Only return the markdown table. Be short and clear.
"""
    response = model.generate_content(prompt)
    return response.text

# -------------------- STREAMLIT UI --------------------

st.title("📉 Anti-Vanity KPI Designer")
st.markdown("Helping founders focus on meaningful startup metrics, not just pretty numbers.")

startup_type = st.selectbox("Select your startup type:", ["SaaS", "Marketplace", "B2C App", "Other"])
st.markdown("### Paste your current KPIs below (one per line, like `Metric: Value`)")

kpi_input = st.text_area("Enter KPIs", height=200, placeholder="Example:\nInstagram Followers: 50,000\nMRR Growth Rate: 12%\nDAU/WAU: 0.3")

if st.button("🧠 Analyze KPIs"):
    if not kpi_input.strip():
        st.warning("Please enter some KPIs to analyze.")
    else:
        with st.spinner("Analyzing with Gemini 2.0..."):
            result = analyze_kpis(startup_type, kpi_input)
        st.markdown("### 🎯 KPI Assessment")
        st.markdown(result)
