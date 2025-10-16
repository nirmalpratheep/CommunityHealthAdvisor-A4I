"""This module defines a simple agent for summarizing data."""

from google.adk.agents import Agent
from .config import config


summarizer_agent = Agent(
    model=config.root_agent_model,
    name="summarizer_agent",
    description="Summarizes data and provides key insights. Use this to get a high-level overview of data gathered from other tools.",
    instruction=(
        "You are an expert data analyst. Your task is to take the provided data "
        "and produce a concise, human-readable summary. Highlight the most "
        "important findings, trends, or key insights. Your output should be "
        "a clear and brief summary of the information provided."
    ),
)