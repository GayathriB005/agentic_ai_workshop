# anti_vanity_kpi.py – Unified Multi-Agent App with RAG and File Uploader

import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from langchain.agents import Tool, initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.chains import RetrievalQA

# -------------------- CONFIG --------------------
os.environ["GOOGLE_API_KEY"] = "AIzaSyB_bK_R95v3A-bMa-g8zxyyowlgg1n_KDI"
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# -------------------- AGENT 1 --------------------
def get_context_agent():
    def startup_context(input_text: str) -> str:
        prompt = f"""
You are a Startup Context Agent.
Extract and structure this startup input:
1. Startup business model (e.g., SaaS, Marketplace, B2C App)
2. Currently tracked KPIs

Input:
{input_text}
"""
        return llm.invoke(prompt).content

    tool = Tool(name="Startup Context Agent", func=startup_context, description="Extracts startup model and KPIs.")
    return initialize_agent([tool], llm=llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# -------------------- AGENT 2 --------------------
def get_critique_agent():
    def kpi_critique(input_text: str) -> str:
        prompt = f"""
You are a KPI Critique Agent.
Given this startup context and list of KPIs:
- Identify vanity metrics (e.g., downloads, followers)
- Flag gaps in strategic tracking
- Suggest areas that need deeper, impactful KPIs

Input:
{input_text}
"""
        return llm.invoke(prompt).content

    tool = Tool(name="KPI Critique Agent", func=kpi_critique, description="Flags vanity KPIs and strategic gaps.")
    return initialize_agent([tool], llm=llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# -------------------- AGENT 3 (RAG) --------------------
def load_and_split_docs(file_path):
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_documents(docs)

def create_vector_store(docs):
    return FAISS.from_documents(docs, embedding)

def build_rag_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=False)

# -------------------- AGENT 4 --------------------
def run_visualization_agent():
    st.subheader("📈 KPI Visualization – Vanity vs Impact")

    data = {
        "KPI Type": ["Vanity", "Impact"],
        "Avg Founder Focus (1-10)": [9, 4],
        "Investor Preference (1-10)": [3, 10],
    }

    df = pd.DataFrame(data)

    fig, ax = plt.subplots()
    bar_width = 0.35
    index = range(len(df["KPI Type"]))
    ax.bar(index, df["Avg Founder Focus (1-10)"], bar_width, label="Founders")
    ax.bar([i + bar_width for i in index], df["Investor Preference (1-10)"], bar_width, label="Investors")

    ax.set_xlabel("KPI Type")
    ax.set_ylabel("Focus Score")
    ax.set_title("Vanity vs Impact KPI Focus")
    ax.set_xticks([i + bar_width/2 for i in index])
    ax.set_xticklabels(df["KPI Type"])
    ax.legend()

    st.pyplot(fig)
    st.success("✅ Visualization rendered successfully.")

# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="Anti-Vanity KPI Designer", layout="wide")
st.title("🧠 Anti-Vanity KPI Designer (All-in-One)")
st.markdown("Run your startup KPIs through 4 specialized AI agents to critique and enhance them.")

user_input = st.text_area("✍️ Describe your startup and current KPIs", height=200)
uploaded_file = st.file_uploader("📄 Upload your KPI Metrics PDF", type=["pdf"])

if st.button("🚀 Run Agents"):
    if not user_input.strip():
        st.error("Please enter a startup description first.")
    elif not uploaded_file:
        st.error("Please upload a KPI metrics PDF to continue.")
    else:
        with st.spinner("1️⃣ Running Startup Context Agent..."):
            context_agent = get_context_agent()
            context_out = context_agent.run(user_input)
            st.subheader("🧠 Context Agent Output")
            st.markdown(context_out)

        with st.spinner("2️⃣ Running KPI Critique Agent..."):
            critique_agent = get_critique_agent()
            critique_out = critique_agent.run(context_out)
            st.subheader("🔍 KPI Critique Agent Output")
            st.markdown(critique_out)

        with st.spinner("3️⃣ Running Impact KPI Generator (RAG)..."):
            with open("temp_kpi_metrics.pdf", "wb") as f:
                f.write(uploaded_file.read())
            documents = load_and_split_docs("temp_kpi_metrics.pdf")
            vectorstore = create_vector_store(documents)
            rag_chain = build_rag_chain(vectorstore)
            impact_out = rag_chain.run(f"Suggest 5 impactful KPIs for this startup: {critique_out}")
            st.subheader("📊 Impact KPI Generator Output")
            st.markdown(impact_out)

        with st.spinner("4️⃣ Visualizing KPI Comparison..."):
            run_visualization_agent()
