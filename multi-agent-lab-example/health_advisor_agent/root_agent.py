# agent.py
from google.adk.agents import Agent

from .config import config
from .data_agent import data_agent
from .insights_agent import insights_agent
from .air_quality_agent import air_quality_agent
from .location_agent import location_agent
from .mobile_clinic_agent import mobile_clinic_agent
from .poverty_agent import poverty_agent

# Define the Root Agent
root_agent = Agent(
    model=config.root_agent_model,
    name="root_agent",
    description="A friendly and helpful Community Health & Wellness Advisor.",
    instruction=(
        "You are the Community Health & Wellness Advisor. Your primary goal is to provide conversational, hyper-local, and actionable health intelligence.\n"
        "Start by greeting the user warmly.\n"
        "Your workflow should be as follows:\n"
        "1. If the user provides a location or asks for information 'near me', use the `location_agent` to find the 5 nearest zip codes. The `location_agent` can infer the location if not provided.\n"
        "2. Once you have the zip codes, you can use other agents to gather relevant data:\n"
        "   - Use the `poverty_agent` to get poverty levels for those zip codes.\n"
        "   - Use the `mobile_clinic_agent` to find information about mobile health clinic deployments.\n"
        "   - Use the `air_quality_agent` to get the Air Quality Index (AQI) for a specific zip code.\n"
        "   - Use the `insights_agent` for data analysis, summarization, or finding 'top N' lists (e.g., 'highest poverty levels', 'most uninsured').\n"
        "   - Use the `data_agent` for simple, direct data lookups.\n"
        "3. Synthesize all the gathered information into a clear, friendly, and helpful final answer for the user."
    ),
    tools=[
        insights_agent,
        data_agent,
        location_agent,
        poverty_agent,
        mobile_clinic_agent,
        air_quality_agent,
    ],
)