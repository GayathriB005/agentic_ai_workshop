# agent_3_feedback_synthesizer.py (Real-time version)

from google_play_scraper import reviews
from langchain_google_genai import ChatGoogleGenerativeAI

# Your Gemini API key
GEMINI_API_KEY = "AIzaSyBoAVE2Kps4It6LAxT11XmZVhCsluNLyRI"
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

def get_live_reviews(app_id: str, count: int = 30) -> str:
    review_data, _ = reviews(
        app_id,
        lang="en",
        country="us",
        count=count
    )
    joined_reviews = "\n".join([r["content"] for r in review_data if r["content"]])
    return joined_reviews

def run_feedback_synthesizer_live(app_id: str) -> str:
    reviews_text = get_live_reviews(app_id)

    prompt = f"""
Analyze the following user reviews from Google Play:

--- User Reviews ---
{reviews_text}

Summarize the following:
- Common user goals
- Frustrations or complaints
- Behavior signals (drop-offs, usage habits)
- Insights useful for improving the product
"""

    response = llm.invoke(prompt)
    return response.content
