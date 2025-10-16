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


class HealthAnalysis(BaseModel):
    """Defines the structured output for health data analysis."""
    identified_issues: List[str] = Field(
        description="A list of potential health issues identified from the text."
    )
    affected_locations: List[str] = Field(
        description="A list of zip codes mentioned in the report."
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
        Your goal is to extract key health issues and any mentioned zip codes. The issues can be wide-ranging.
        Examples of signals to look for include, but are not limited to:
        - Healthcare Access issues (e.g., underserved areas, uninsured populations, lack of clinics)
        - Environmental Risks (e.g., pollution, air/water quality, heatwaves)
        - Disease Outbreaks (e.g., flu clusters, infectious disease signals)
        - Emerging Crises (e.g., ER surges, public safety alerts)
        Your output MUST be a JSON object that conforms to the following schema:
        {
            "identified_issues": ["issue1", "issue2"],
            "affected_locations": ["zip1", "zip2"]
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
        your task is to find relevant, localized context.
        For each issue in 'structured_analysis.identified_issues', perform a Google search.
        If 'structured_analysis.affected_locations' is not empty, combine the issue with the primary location to get localized results.
        If no locations are available, search for the issue more broadly.
        For example, if the issue is 'Disease Outbreak' and the location is '90210', search for 'Disease Outbreak 90210'.
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