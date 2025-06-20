# agent_1_market_scraper.py

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI

# 🔑 Replace your real keys here
GEMINI_API_KEY = "AIzaSyC4M7uDNCU3rDIklYS1efm3xCsWCw-eAs4"
TAVILY_API_KEY = "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"

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)
tavily = TavilySearchResults(tavily_api_key=TAVILY_API_KEY)  # ✅ Correct


def run_marketplace_scraper(project_title: str, keywords: str):
    query = f"{project_title} {keywords}"
    results = tavily.run(query)

    prompt = f"""
You are a marketplace research assistant. Analyze the following search results:

{results}

For the top 3 competitors, extract:
- App name
- Category
- Features
- Design elements
- Description

Output in a readable bullet-point format.
"""
    response = llm.invoke(prompt)
    return response.content
