# agent_4_persona_generator.py

from langchain_google_genai import ChatGoogleGenerativeAI

# 🔑 Gemini API Key
GEMINI_API_KEY = "AIzaSyCRMBljYAOiru3CHNIxZhHk6qE86FK5D_k"
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

def run_persona_generator(audience_summary: str, feedback_summary: str) -> str:
    """
    Generate 3 user personas using audience assumptions + user feedback.
    Each persona includes name, age, role, habits, goals, frustrations, and usage traits.
    """
    prompt = f"""
Based on the following audience profile and real user feedback:

--- Audience Summary ---
{audience_summary}

--- Feedback Summary ---
{feedback_summary}

Generate 3 realistic and distinct user personas with the following format:
- Name
- Age
- Occupation / Role
- Goals
- Habits
- Frustrations
- Typical App Usage Behavior

Structure each persona clearly. Keep it concise and practical for UX planning.
"""
    response = llm.invoke(prompt)
    return response.content
