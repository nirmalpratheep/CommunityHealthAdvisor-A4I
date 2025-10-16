"""This module defines the `insights_agent` for health data analysis.

The `insights_agent` orchestrates a two-step sequential workflow. It expects
to receive unstructured health data as a string in the session state under the
key 'unstructured_health_data'.

The workflow consists of two sub-agents:
1.  data_cleaner_agent: This agent takes the raw, unstructured data from the
    'unstructured_health_data' state variable. It uses the
    `structure_health_data_tool` to parse this data, extracting key information
    like potential health issues and affected zip codes. The structured output
    is then saved back into the session state under the key 'structured_analysis'.

2.  insights_creator_agent: This agent takes the structured data from the
    'structured_analysis' state variable and, following its instructions as a
    public health analyst, generates a concise, human-readable summary of the
    key insights.
"""

import os
import sys
import re
import logging

sys.path.append("..")
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
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
    identified_issue = "Not specified"
    if "access" in unstructured_data.lower() or "underserved" in unstructured_data.lower():
        identified_issue = "Potential Healthcare Access Issue"
    elif "outbreak" in unstructured_data.lower() or "cluster" in unstructured_data.lower():
        identified_issue = "Potential Disease Outbreak"
    elif "air quality" in unstructured_data.lower() or "water" in unstructured_data.lower():
        identified_issue = "Potential Environmental Health Risk"

    if not zip_codes and identified_issue == "Not specified":
        return {
            "status": "error",
            "message": "Could not extract any meaningful health data or locations from the input.",
        }

    return {
        "status": "success",
        "analysis": {
            "identified_issue": identified_issue,
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

insights_creator_agent = Agent(
    name="insights_creator_agent",
    model=os.getenv("MODEL"),
    description="Generates human-readable insights from structured data.",
    instruction="""You are a public health analyst. Your task is to interpret the
        following structured health equity data and provide a concise, human-readable
        summary of the key insights. Focus on the problem, the affected areas,
        and the primary needs identified in the data.
        Data: {structured_analysis}""",
)

insights_agent = SequentialAgent(
    name="health_insights_pipeline",
    sub_agents=[data_cleaner_agent, insights_creator_agent],
)