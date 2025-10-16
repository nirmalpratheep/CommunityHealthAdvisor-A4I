# insights_agent.py
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from .data_agent import data_agent
from .config import config

# Define the Insights Agent
insights_agent = Agent(
    model=config.root_agent_model,
    name="insights_agent",
    description="A specialized agent that analyzes and summarizes community health data.",
    instruction=(
        "You are a public health data analyst. Your role is to take raw data and generate clear, concise summaries and comparisons. "
        "For example, if asked to find areas with high poverty, you should use the data_agent tool to query the relevant data, "
        "then formulate a human-readable response like 'The areas with the highest poverty rates are X, Y, and Z.' "
        "You must use the data_agent tool to acquire any data needed for your analysis."
    ),
    tools=[AgentTool(data_agent)]
)
