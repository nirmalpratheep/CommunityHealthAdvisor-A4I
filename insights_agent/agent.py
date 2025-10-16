"""This module defines the `insights_agent` for health data analysis.

The `insights_agent` orchestrates a three-step sequential workflow. It expects
to receive unstructured health data as a string in the session state under the
key 'unstructured_health_data'.

The workflow consists of three sub-agents:
1.  data_cleaner_agent: This agent takes the raw, unstructured data from the
    'unstructured_health_data' state variable. It uses the
    `structure_health_data_tool` to parse this data, extracting key information
    like potential health issues and affected zip codes. The structured output
    is then saved back into the session state under the key 'structured_analysis'.

2.  researcher_agent: This agent takes the 'identified_issues' from the
    'structured_analysis' and uses the `google_search` tool to find additional
    context for each issue. The findings are saved to the 'research_findings'
    state variable.

3.  insights_creator_agent: This agent synthesizes information from both the
    'structured_analysis' and 'research_findings' state variables to generate a
    comprehensive, human-readable summary of the key health insights.
"""

import os
import sys
import re
import logging

sys.path.append("..")
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search
load_dotenv()


def structure_health_data_tool(unstructured_data: str) -> dict:
    """
    Parses and structures unstructured health report text into a dictionary.
    Extracts potential health issues and affected zip codes using regex and keyword matching.
    """
    logging.info("--- Tool: Structuring unstructured health data ---")

    # Use regex to find all 5-digit numbers, assuming they are zip codes.
    zip_codes = re.findall(r"\b\d{5}\b", unstructured_data)

    # Identify potential issues based on keywords.
    identified_issues = []
    if "access" in unstructured_data.lower() or "underserved" in unstructured_data.lower():
        identified_issues.append("Potential Healthcare Access Issue")
    if "outbreak" in unstructured_data.lower() or "cluster" in unstructured_data.lower():
        identified_issues.append("Potential Disease Outbreak")
    if "air quality" in unstructured_data.lower() or "water" in unstructured_data.lower():
        identified_issues.append("Potential Environmental Health Risk")

    if not zip_codes and not identified_issues:
        return {
            "status": "error",
            "message": "Could not extract any meaningful health data or locations from the input.",
        }

    return {
        "status": "success",
        "analysis": {
            "identified_issues": identified_issues if identified_issues else ["Not specified"],
            "affected_locations": list(set(zip_codes)),
        },
    }


data_cleaner_agent = Agent(
    name="data_cleaner_agent",
    model=os.getenv("MODEL"),
    description="Cleans and structures raw health data using a tool.",
    instruction="""Given unstructured health data in the '{unstructured_health_data}' state variable,
        use the 'structure_health_data_tool' to process it into a structured format.""",
    tools=[structure_health_data_tool],
    output_key="structured_analysis",
)

researcher_agent = Agent(
    name="researcher_agent",
    model=os.getenv("MODEL"),
    description="Performs a Google search on the identified health issue.",
    instruction="""You are a research assistant. For each issue in the 'identified_issues'
        list from the 'structured_analysis' in the session state, perform a
        Google search to find more context or recent news about it.""",
    tools=[google_search],
    output_key="research_findings",
)

insights_creator_agent = Agent(
    name="insights_creator_agent",
    model=os.getenv("MODEL"),
    description="Generates human-readable insights from structured data.",
    instruction="""You are a public health analyst. Your task is to interpret the
        following structured health equity data and provide a concise,
        human-readable summary of the key insights. Use the research findings to add more context.
        Focus on the problem, the affected areas, and the primary needs identified.

        Structured Data: {structured_analysis}
        Research Findings: {research_findings}
        """,
)

insights_agent = SequentialAgent(
    name="health_insights_pipeline",
    sub_agents=[data_cleaner_agent, researcher_agent, insights_creator_agent],
)