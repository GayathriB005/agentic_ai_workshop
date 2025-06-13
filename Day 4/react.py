import streamlit as st
import google.generativeai as genai
from tavily import TavilyClient

# =================== API KEYS (HARDCODED) ===================
GENAI_API_KEY = "AIzaSyDigHqRh5QZQA1hB8zew5WcqgHqVNrcYoc"
TAVILY_API_KEY = "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"

# =================== CONFIGURATION ===================
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# =================== FUNCTION: Generate Questions ===================
def generate_questions(topic):
    prompt = f"""Generate 6 unique, diverse, and insightful research questions on the topic: "{topic}"."""
    response = model.generate_content(prompt)
    questions = [line.lstrip("-•1234567890. ").strip() for line in response.text.split("\n")]
    # Filter valid and short questions (Tavily limit = 400 characters)
    return [q for q in questions if q and len(q) <= 400]

# =================== FUNCTION: Search Web Answers ===================
def search_answers(question):
    safe_question = question[:400]  # Max limit for Tavily
    results = tavily.search(query=safe_question, search_depth="basic", max_results=3)
    return [
        {
            "title": res["title"],
            "content": res["content"][:200] + "..."  # Shorten for preview
        } for res in results.get("results", [])
    ]

# =================== FUNCTION: Build Final Report ===================
def compile_report(topic, qna):
    report = f"# Research Report on: {topic}\n\n"
    report += "## Introduction\nThis report was generated using Gemini 2.0 Flash and Tavily web search.\n\n"
    for idx, item in enumerate(qna, 1):
        report += f"## {idx}. {item['question']}\n"
        for source in item["answers"]:
            report += f"- **{source['title']}**: {source['content']}\n"
        report += "\n"
    report += "## Conclusion\nThis concludes the AI-assisted research.\n"
    return report

# =================== STREAMLIT APP ===================
st.set_page_config(page_title="Web Research Agent", page_icon="🧠")
st.title("🔍 Web Research Agent (Gemini 2.0 Flash + Tavily)")

topic = st.text_input("Enter a topic to research:")

if st.button("Generate Report") and topic.strip():
    with st.spinner("🤖 Generating research questions..."):
        questions = generate_questions(topic)

    if questions:
        st.subheader("📌 Research Questions")
        for q in questions:
            st.markdown(f"- {q}")

        qna = []
        with st.spinner("🌐 Searching the web..."):
            for q in questions:
                answers = search_answers(q)
                qna.append({"question": q, "answers": answers})

        report = compile_report(topic, qna)

        st.subheader("📝 Final Report")
        st.markdown(report)
        st.download_button("📥 Download Report", data=report, file_name="research_report.md", mime="text/markdown")
    else:
        st.error("⚠️ No valid questions were generated. Try a different topic.")
