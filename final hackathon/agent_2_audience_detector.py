# agent_2_audience_detector.py

from langchain_google_genai import ChatGoogleGenerativeAI

# 🔑 Gemini API Key
GEMINI_API_KEY = "AIzaSyC4M7uDNCU3rDIklYS1efm3xCsWCw-eAs4"

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

def run_audience_detector(competitor_metadata: str) -> str:
    """
    Analyze competitor metadata to detect audience attributes:
    - Age group
    - Profession/role
    - Goals
    - Tone of content
    - UI/UX preferences
    """
    prompt = f"""
You are an audience analyst.

Based on this product metadata:
{competitor_metadata}

Infer the likely target audience attributes:
- Age group
- Occupation or role
- User goals
- Language or tone of the product
- Visual or UI traits that appeal to them

Give your answer in bullet points.
"""

    response = llm.invoke(prompt)
    return response.content
