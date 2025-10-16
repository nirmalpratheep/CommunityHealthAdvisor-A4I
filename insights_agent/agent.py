"""This module defines the `insights_agent` for health data analysis.

The `insights_agent` orchestrates a sequential workflow. It expects
to receive unstructured health data as a string in the session state under the
key 'unstructured_health_data'.
The workflow is designed to transform raw text into actionable intelligence for a larger health equity system.
1.  `data_structuring_agent`: Parses unstructured text to identify specific health issues (like 'Healthcare Access', 'Environmental Risk', 'Disease Outbreak') and affected zip codes.
2.  `researcher_agent`: Conducts targeted Google searches for the identified issue within the specified location to gather relevant context.
3.  `insights_creator_agent`: Synthesizes the structured data and research findings into a final, actionable JSON object. This output includes a human-readable summary, a categorized problem type, and a concrete recommended action for other agents or systems to use.
"""

import os
import sys
from typing import List

sys.path.append("..")
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search
from pydantic import BaseModel, Field

load_dotenv()


class HealthEvent(BaseModel):
    """Represents a single health issue and its specific location."""
    issue: str = Field(
        description="A single, specific health issue identified from the text, e.g., 'flu outbreak' or 'lack of clinics'."
    )
    locations: List[str] = Field(
        description="A list of one or more locations where this specific issue is occurring. Locations can be zip codes, neighborhoods, city districts, or general areas (e.g., 'downtown', 'the waterfront')."
    )

class HealthAnalysis(BaseModel):
    """A collection of health events found in the report."""
    health_events: List[HealthEvent] = Field(
        description="A list of health events, each linking a specific issue to its affected locations."
    )


class ActionableInsight(BaseModel):
    """
    Defines the structured output for the final insight, making it machine-readable
    and actionable for other agents in the system.
    """
    summary: str = Field(
        description="A concise, human-readable summary of the key insights."
    )
    problem_type: str = Field(
        description="A category for the issue, e.g., 'HEALTHCARE_ACCESS', 'ENVIRONMENTAL_RISK', 'DISEASE_OUTBREAK'."
    )
    recommended_action: str = Field(
        description="A concrete next step, e.g., 'Recommend mobile health unit deployment to zip code 90210'."
    )


data_structuring_agent = Agent(
    name="data_structuring_agent",
    model=os.getenv("MODEL"),
    description="Structures raw health data using an LLM.",
    instruction="""You are a data structuring specialist for a public health organization.
        Analyze the unstructured health data provided in the '{unstructured_health_data}' state variable.
        Your goal is to extract key health issues and link them to the specific locations mentioned in relation to them.
        A location can be a zip code, a neighborhood, a district, or a general area (e.g., "downtown", "Northside", "the industrial park").
        The issues can be wide-ranging.
        Examples of signals to look for include, but are not limited to:
        - Healthcare Access issues (e.g., underserved areas, uninsured populations, lack of clinics)
        - Environmental Risks (e.g., pollution, air/water quality, heatwaves)
        - Disease Outbreaks (e.g., flu clusters, infectious disease signals)
        - Emerging Crises (e.g., ER surges, public safety alerts)
        Your output MUST be a JSON object that conforms to the HealthAnalysis schema. For each distinct issue, create a HealthEvent object containing the issue and a list of all locations associated with it.
        Example output format:
        {
            "health_events": [
                {"issue": "flu outbreak", "locations": ["90210", "90211"]},
                {"issue": "air quality concerns", "locations": ["downtown", "the industrial park"]}
            ]
        }
        Respond ONLY with the JSON object.""",
    output_schema=HealthAnalysis,
    output_key="structured_analysis",
)

researcher_agent = Agent(
    name="researcher_agent",
    model=os.getenv("MODEL"),
    description="Performs a Google search on the identified health issue.",
    instruction="""You are a research assistant for a public health organization.
        Based on the structured analysis provided in the '{structured_analysis}' state variable,
        your task is to find relevant, localized context for each health event.
        Iterate through each event in 'structured_analysis.health_events'. For each event, perform a targeted Google search
        combining the 'issue' with each 'location' in its 'locations' list.
        For example, if an event is `{"issue": "flu outbreak", "locations": ["90210", "90211"]}`, you should search for "flu outbreak 90210" and "flu outbreak 90211".
        Your goal is to find recent news, official reports, or community discussions about this specific issue in that area.
        """,
    tools=[google_search],
    output_key="research_findings",
)

insights_creator_agent = Agent(
    name="insights_creator_agent",
    model=os.getenv("MODEL"),
    description="Generates actionable, structured insights from analyzed health data.",
    instruction="""You are a public health analyst creating actionable intelligence for a crisis response system.
        Your task is to synthesize the structured data and research findings into a final JSON object.
        This object must conform to the ActionableInsight schema.
        1.  **Summary**: Write a concise, human-readable summary of the problem, affected areas, and primary needs, incorporating the research findings.
        2.  **Problem Type**: Categorize the main issue into a clear, high-level category. Use your best judgment. Examples include:
            - 'HEALTHCARE_ACCESS' (for issues of unequal access, or related to uninsured/low-income populations)
            - 'ENVIRONMENTAL_RISK' (for issues related to pollution, air/water quality, or heat)
            - 'DISEASE_OUTBREAK' (for disease clusters and early warning signals)
            - 'EMERGING_CRISIS' (for urgent events like ER surges or public safety alerts)
            - 'GENERAL_HEALTH_CONCERN' (if it does not fit other categories but is still a public health issue)
        3.  **Recommended Action**: Propose a single, concrete, and actionable next step for a health organization. For example: 'Recommend deploying a mobile health unit to zip code 90210' or 'Alert local health department about a potential flu cluster in 33101'.

        Structured Data: {structured_analysis}
        Research Findings: {research_findings}
        """,
    output_schema=ActionableInsight,
)

insights_agent = SequentialAgent(
    name="health_insights_pipeline",
    sub_agents=[data_structuring_agent, researcher_agent, insights_creator_agent],
)