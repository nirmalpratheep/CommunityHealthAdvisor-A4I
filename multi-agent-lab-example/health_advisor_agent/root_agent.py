# agent.py
from google.adk.agents import Agent
from google.adk.tools import AgentTool

from .config import config
from .air_quality_agent import air_quality_agent
from .data_agent import data_agent
from .location_agent import location_agent
from .mobile_clinic_agent import mobile_clinic_agent
from .poverty_agent import poverty_agent
from .summarizer_agent import summarizer_agent

# Define the Root Agent
root_agent = Agent(
    model=config.root_agent_model,
    name="root_agent",
    description="A friendly and helpful Community Health & Wellness Advisor.",
    instruction=(
        "You are the Community Health & Wellness Advisor. Your primary goal is to provide conversational, hyper-local, and actionable health intelligence.\n"
        "Start by greeting the user warmly.\n"
        "Your workflow should be as follows:\n"
        "1. Once you have the location, you can use other agents to gather relevant data:\n"
        "   - Use the `poverty_agent` to get poverty levels for those zip codes.\n"
        "   - Use the `mobile_clinic_agent` to find information about mobile health clinic deployments.\n"
        "   - Use the `air_quality_agent` to get the Air Quality Index (AQI) for a specific zip code.\n"
        "   - Use the `data_agent` for simple, direct data lookups.\n"
        "3. After gathering data, use the `summarizer_agent` to create a high-level overview of the findings.\n"
        "4. Synthesize all the gathered information into a clear, friendly, and helpful final answer for the user."
    ),
    tools=[
        AgentTool(data_agent),
        #AgentTool(location_agent),
        AgentTool(poverty_agent),
        AgentTool(mobile_clinic_agent),
        AgentTool(air_quality_agent),
        AgentTool(summarizer_agent),
    ],
)