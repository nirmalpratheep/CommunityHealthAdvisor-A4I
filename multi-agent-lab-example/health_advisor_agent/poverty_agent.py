# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import Dict, List

from google.adk import Agent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field
import requests


from .config import config


class PovertyLevelsOutput(BaseModel):
    """Output for the poverty levels tool."""

    poverty_levels: Dict[int, float] = Field(
        description="A dictionary mapping each zip code to its poverty level percentage."
    )


def get_poverty_levels(zipcodes: List[int]) -> str:
    """
    Gets the poverty level for a list of zip codes.

    Args:
        zipcodes: A list of zip codes to get poverty levels for.
    """
    api_key = os.getenv("CENSUS_API_KEY")
    if not api_key:
        return str(
            PovertyLevelsOutput(
                poverty_levels={
                    zipcode: -1.0 for zipcode in zipcodes
                }
            ).model_dump()
        )

    # Using ACS 5-Year Data Profiles (2022)
    # DP03_0119PE: Percent of people whose income in the past 12 months is below the poverty level
    base_url = "https://api.census.gov/data/2022/acs/acs5/profile"
    zip_str = ",".join([str(z) for z in zipcodes])
    params = {
        "get": "DP03_0119PE",
        "for": f"zip code tabulation area:{zip_str}",
        "key": api_key,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # The first row is the header, so we skip it
        results = {int(row[2]): float(row[0]) for row in data[1:] if row[0] is not None}
        return str(PovertyLevelsOutput(poverty_levels=results).model_dump())
    except (requests.RequestException, ValueError, IndexError):
        # Return empty results on API or parsing failure
        return str(PovertyLevelsOutput(poverty_levels={}).model_dump())


poverty_agent = Agent(
    model=config.root_agent_model,
    name="poverty_agent",
    instruction="You are an expert in socioeconomic data. Your task is to get the poverty levels for a given list of zip codes. If you receive a -1.0 value, it means the CENSUS_API_KEY is not set.",
    tools=[FunctionTool(get_poverty_levels)],
)
