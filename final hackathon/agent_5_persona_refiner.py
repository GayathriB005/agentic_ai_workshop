# agent_5_persona_refiner.py

from langchain_google_genai import ChatGoogleGenerativeAI

# 🔑 Gemini API Key
GEMINI_API_KEY = "AIzaSyBoAVE2Kps4It6LAxT11XmZVhCsluNLyRI"
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

def run_persona_refiner(personas: str, feedback_summary: str) -> str:
    """
    Refine and validate personas using actual behavior signals from user feedback.
    Adds realistic traits, validates motivations, fills gaps, and aligns to product usage.
    """
    prompt = f"""
You are a UX persona specialist.

Refine the following personas to make them more realistic, specific, and behaviorally grounded.
Use the real user feedback insights to validate motivations, frustrations, and product fit.

--- Personas (Drafts) ---
{personas}

--- User Behavior Summary ---
{feedback_summary}

For each persona:
- Improve name, age, and role realism
- Align goals with user intent from feedback
- Clarify blockers or usage friction
- Add 1-sentence product fit annotation

Output the revised personas in clean bullet-point format.
"""
    response = llm.invoke(prompt)
    return response.content
