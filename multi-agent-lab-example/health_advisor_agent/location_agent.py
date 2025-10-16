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

from typing import List, Optional

from google.adk import Agent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

from geopy.geocoders import Nominatim
import pgeocode
import requests

from .config import config


class NearestZipcodesOutput(BaseModel):
    """Output for the nearest zipcodes tool."""

    zipcodes: List[int] = Field(description="List of the 5 nearest zip codes.")


def _get_location_from_ip() -> Optional[str]:
    """Infers location from the user's public IP address."""
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        response.raise_for_status()
        data = response.json()
        return f"{data.get('city', '')}, {data.get('region', '')}"
    except requests.RequestException:
        return None


def get_nearest_zipcodes(
    location: Optional[str] = None, country_code: Optional[str] = "us"
) -> str:
    """
    Find the 5 nearest zip codes for a given location. If a location is not provided, it will be inferred.

    Args:
        location: The location to find the nearest zip codes for. If not provided, location is inferred from IP address.
        country_code: The two-letter country code (e.g., 'us', 'ca'). Defaults to 'us'.
    """
    try:
        if not location:
            location = _get_location_from_ip()

        # Geocode the location to get latitude and longitude
        geolocator = Nominatim(user_agent="community_health_advisor")
        geo_location = geolocator.geocode(location)

        if not geo_location:
            return str(NearestZipcodesOutput(zipcodes=[]).model_dump())

        # Use pgeocode to find nearest zip codes
        # pgeocode needs a country code.
        geo = pgeocode.Nominatim(country_code)
        
        # Query for locations within a radius (e.g., 20km) and take the top 5
        # The radius might need adjustment depending on population density.
        nearby_places = geo.query_location(geo_location.address, radius=20)
        
        # Extract unique postal codes and convert to int
        zipcodes = [int(z) for z in nearby_places["postal_code"].unique() if str(z).isdigit()]

        # If we found more than 5, just take the first 5.
        # The results from pgeocode are often sorted by distance.
        nearest_five = zipcodes[:5]

        return str(NearestZipcodesOutput(zipcodes=nearest_five).model_dump())
    except Exception as e:
        return str(NearestZipcodesOutput(zipcodes=[]).model_dump())


location_agent = Agent(
    model=config.root_agent_model,
    name="location_agent",
    instruction="""
      You are an expert in geolocation. Your task is to find the 5 nearest zip codes for a given location.
      First, determine the user's current location if not provided, then use the available tools to find the nearest zip codes.
    """,
    tools=[FunctionTool(get_nearest_zipcodes)],
)
