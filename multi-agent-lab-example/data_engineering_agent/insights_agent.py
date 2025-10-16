# insights_agent.py
from google.adk.agents import Agent
from data_agent import data_agent  # Import the data_agent instance

# Define the Insights Agent
insights_agent = Agent(
    model="gemini-1.5-flash",
    name="insights_agent",
    description="A specialized agent that analyzes and summarizes community health data.",
    instruction=(
        "You are a public health data analyst. Your role is to take raw data and generate clear, concise summaries and comparisons. "
        "For example, if asked to find areas with high poverty, you should use the data_agent tool to query the relevant data, "
        "then formulate a human-readable response like 'The areas with the highest poverty rates are X, Y, and Z.' "
        "You must use the data_agent tool to acquire any data needed for your analysis."
    ),
    tools=[data_agent]
)
