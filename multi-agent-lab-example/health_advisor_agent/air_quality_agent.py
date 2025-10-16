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

from typing import Dict

from google.adk import Agent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field
import pgeocode

from .config import config

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None


class AirQualityOutput(BaseModel):
    """Output for the air quality tool."""

    aqi: int = Field(description="The most recent Air Quality Index (AQI) value.")
    reporting_date: str = Field(description="The date the AQI was reported.")
    defining_parameter: str = Field(
        description="The main pollutant determining the AQI value."
    )


def get_air_quality_by_zipcode(zipcode: int) -> str:
    """
    Gets the latest Air Quality Index (AQI) for a given zip code from the EPA public dataset in BigQuery.

    Args:
        zipcode: The zip code to get the air quality for.
    """
    if not bigquery:
        return "BigQuery client is not installed. Please install 'google-cloud-bigquery'."

    # Get lat/lon for the zip code
    geo = pgeocode.Nominatim("us")
    zip_info = geo.query_postal_code(str(zipcode))
    if zip_info.empty:
        return f"Could not find location for zip code: {zipcode}"

    lat, lon = zip_info.latitude, zip_info.longitude

    client = bigquery.Client()
    query = """
        WITH nearest_site AS (
            SELECT
                state_code, county_code, site_num,
                ST_DISTANCE(ST_GEOGPOINT(longitude, latitude), ST_GEOGPOINT(@lon, @lat)) as distance
            FROM `bigquery-public-data.epa_historical_air_quality.sites`
            ORDER BY distance
            LIMIT 1
        )
        SELECT
            t1.date_local,
            t1.aqi,
            t1.defining_parameter
        FROM `bigquery-public-data.epa_historical_air_quality.daily_aqi` AS t1
        JOIN nearest_site ON t1.state_code = nearest_site.state_code
                         AND t1.county_code = nearest_site.county_code
                         AND t1.site_num = nearest_site.site_num
        ORDER BY t1.date_local DESC
        LIMIT 1;
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("lon", "FLOAT64", lon),
            bigquery.ScalarQueryParameter("lat", "FLOAT64", lat),
        ]
    )
    try:
        query_job = client.query(query, job_config=job_config)
        results = list(query_job)
        if not results:
            return f"No AQI data found for the nearest station to zip code {zipcode}."
        row = results[0]
        output = AirQualityOutput(
            aqi=row.aqi,
            reporting_date=str(row.date_local),
            defining_parameter=row.defining_parameter,
        )
        return output.model_dump_json()
    except Exception as e:
        return f"An error occurred while querying BigQuery: {e}"


air_quality_agent = Agent(
    model=config.root_agent_model,
    name="air_quality_agent",
    instruction="You are an environmental data specialist. Your task is to retrieve the latest Air Quality Index (AQI) for a given zip code using a BigQuery public dataset.",
    tools=[FunctionTool(get_air_quality_by_zipcode)],
)