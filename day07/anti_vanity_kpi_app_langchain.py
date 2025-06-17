import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import io
import base64

# Initialize Streamlit
st.set_page_config(page_title="Anti-Vanity KPI Designer", layout="wide")
st.title("Anti-Vanity KPI Designer")
st.markdown("Enter your startup details and KPI benchmarks to generate a dashboard focusing on impactful metrics.")

# Initialize Gemini 2.0 Flash
api_key = os.getenv("AIzaSyBa-BdCpPsbwDW-bBCBzaxa_Lg-9T_NzoM")
if not api_key:
    st.error("Please set the GEMINI_API_KEY environment variable.")
    st.stop()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0.7)

# Define Tools
@tool
def collect_startup_context(business_model: str, current_kpis: str) -> dict:
    """Collects startup business model and current KPIs."""
    return {"business_model": business_model, "current_kpis": current_kpis.split(", ")}

@tool
def critique_kpis(kpis: list) -> dict:
    """Evaluates KPIs, flags vanity metrics, and identifies gaps."""
    vanity_metrics = ["followers", "downloads", "page_views"]
    critique = {"vanity": [], "impactful": [], "gaps": []}
    for kpi in kpis:
        if kpi.lower() in vanity_metrics:
            critique["vanity"].append(kpi)
        else:
            critique["impactful"].append(kpi)
    if not critique["impactful"]:
        critique["gaps"].append("No impact metrics found. Consider retention, LTV, or revenue-based KPIs.")
    return critique

@tool
def generate_impact_kpis(business_model: str, benchmark_docs: str) -> list:
    """Generates impact KPIs based on user-provided benchmark documents."""
    # Process benchmark documents to extract KPIs relevant to the business model
    kpis = []
    for line in benchmark_docs.split("\n"):
        if business_model.lower() in line.lower():
            kpi_part = line.split(": ")[1] if ": " in line else line
            kpis.append(kpi_part.strip())
    return kpis if kpis else ["No relevant KPIs found in provided benchmarks."]

@tool
def create_dashboard(vanity_kpis: list, impact_kpis: list) -> str:
    """Generates an HTML dashboard contrasting vanity and impact KPIs."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>KPI Dashboard</title>
        <style>
            body { font-family: Arial; }
            .container { display: flex; justify-content: space-around; }
            .box { padding: 20px; border: 1px solid #ccc; width: 45%; }
            .vanity { background-color: #ffe6e6; }
            .impact { background-color: #e6ffe6; }
        </style>
    </head>
    <body>
        <h1>Anti-Vanity KPI Dashboard</h1>
        <div class="container">
            <div class="box vanity">
                <h2>Vanity Metrics</h2>
                <ul>
    """
    for kpi in vanity_kpis:
        html += f"<li>{kpi}</li>"
    html += """
                </ul>
            </div>
            <div class="box impact">
                <h2>Impact Metrics</h2>
                <ul>
    """
    for kpi in impact_kpis:
        html += f"<li>{kpi}</li>"
    html += """
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# Define Agent Prompts
context_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Startup Context Agent. Collect and structure startup details."),
    MessagesPlaceholder(variable_name="messages"),
])

critique_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a KPI Critique Agent. Identify vanity metrics and strategic gaps in KPIs."),
    MessagesPlaceholder(variable_name="messages"),
])

generator_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an Impact KPI Generator Agent. Use provided benchmark documents to recommend impactful KPIs."),
    MessagesPlaceholder(variable_name="messages"),
])

visualization_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Metric Board Visualization Agent. Create a dashboard contrasting KPIs."),
    MessagesPlaceholder(variable_name="messages"),
])

# Create Agents
context_agent = create_tool_calling_agent(llm, [collect_startup_context], context_prompt)
context_executor = AgentExecutor(agent=context_agent, tools=[collect_startup_context], verbose=False)

critique_agent = create_tool_calling_agent(llm, [critique_kpis], critique_prompt)
critique_executor = AgentExecutor(agent=critique_agent, tools=[critique_kpis], verbose=False)

generator_agent = create_tool_calling_agent(llm, [generate_impact_kpis], generator_prompt)
generator_executor = AgentExecutor(agent=generator_agent, tools=[generate_impact_kpis], verbose=False)

visualization_agent = create_tool_calling_agent(llm, [create_dashboard], visualization_prompt)
visualization_executor = AgentExecutor(agent=visualization_agent, tools=[create_dashboard], verbose=False)

# Define State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    context: dict
    critique: dict
    impact_kpis: list
    dashboard: str
    benchmark_docs: str

# Define Workflow
workflow = StateGraph(AgentState)

def call_context_agent(state):
    result = context_executor.invoke({"messages": state["messages"]})
    return {"context": eval(result["output"]) if isinstance(result["output"], str) else result["output"]}

def call_critique_agent(state):
    result = critique_executor.invoke({"messages": [HumanMessage(content=str(state["context"]["current_kpis"]))]})
    return {"critique": eval(result["output"]) if isinstance(result["output"], str) else result["output"]}

def call_generator_agent(state):
    result = generator_executor.invoke({"messages": [HumanMessage(content=f"Business model: {state['context']['business_model']}, Benchmarks: {state['benchmark_docs']}")]})
    return {"impact_kpis": eval(result["output"]) if isinstance(result["output"], str) else result["output"]}

def call_visualization_agent(state):
    result = visualization_executor.invoke({"messages": [HumanMessage(content=f"Vanity: {state['critique']['vanity']}, Impact: {state['impact_kpis']}")]})
    return {"dashboard": result["output"]}

workflow.add_node("context", call_context_agent)
workflow.add_node("critique", call_critique_agent)
workflow.add_node("generator", call_generator_agent)
workflow.add_node("visualization", call_visualization_agent)

workflow.set_entry_point("context")
workflow.add_edge("context", "critique")
workflow.add_edge("critique", "generator")
workflow.add_edge("generator", "visualization")
workflow.add_edge("visualization", END)

# Compile Workflow
graph = workflow.compile()

# Streamlit UI
with st.form("kpi_form"):
    business_model = st.text_input("Startup Business Model (e.g., SaaS, Marketplace, B2C App)", value="SaaS")
    current_kpis = st.text_input("Current KPIs (comma-separated, e.g., followers, downloads, MRR)", value="followers, downloads, MRR, churn_rate")
    benchmark_docs = st.text_area(
        "KPI Benchmark Documents",
        placeholder="Paste benchmark data here, e.g., 'SaaS: LTV/CAC ratio > 3 is ideal. Churn rate < 5% monthly.'",
        value="SaaS: LTV/CAC ratio > 3 is ideal for investor confidence. Churn rate < 5% monthly indicates strong retention.\nMarketplace: GMV growth rate > 20% QoQ is a key impact metric.\nB2C App: DAU/WAU retention > 40% shows sticky user engagement."
    )
    submitted = st.form_submit_button("Generate KPI Dashboard")

if submitted:
    with st.spinner("Processing..."):
        # Run Workflow
        initial_state = {
            "messages": [HumanMessage(content=f"Business model: {business_model}, Current KPIs: {current_kpis}")],
            "benchmark_docs": benchmark_docs
        }
        result = graph.invoke(initial_state)

        # Display Results
        st.subheader("Analysis Results")
        st.write("**Startup Context**")
        st.json(result["context"])
        st.write("**KPI Critique**")
        st.json(result["critique"])
        st.write("**Recommended Impact KPIs**")
        st.write(result["impact_kpis"])

        # Display Dashboard
        st.subheader("KPI Dashboard")
        st.components.v1.html(result["dashboard"], height=400, scrolling=True)

        # Provide Download Option
        dashboard_bytes = result["dashboard"].encode()
        st.download_button(
            label="Download Dashboard HTML",
            data=dashboard_bytes,
            file_name="kpi_dashboard.html",
            mime="text/html"
        )

if not submitted:
    st.info("Fill in the form and click 'Generate KPI Dashboard' to see results.")