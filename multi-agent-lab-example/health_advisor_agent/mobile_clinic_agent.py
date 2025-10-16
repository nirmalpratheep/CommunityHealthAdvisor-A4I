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

from typing import Any, Dict, List

from google.adk import Agent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

from .config import config

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None


class DeploymentDetail(BaseModel):
    """Details for a single mobile clinic deployment."""

    deployment_date: str = Field(description="Date of the deployment.")
    address: str = Field(description="Address of the deployment.")
    zip_code: int = Field(description="Zip code of the deployment.")
    services_offered: List[str] = Field(description="List of services offered.")


class ClinicDeploymentsOutput(BaseModel):
    """Output for the mobile clinic deployments tool."""

    deployments: List[DeploymentDetail] = Field(
        description="List of mobile clinic deployments."
    )


def get_mobile_clinic_deployments(zipcodes: List[int]) -> str:
    """
    Gets details about mobile health clinic deployments from BigQuery for a list of zip codes.

    Args:
        zipcodes: A list of zip codes to search for clinic deployments.
    """
    if not bigquery:
        return "BigQuery client is not installed. Please install 'google-cloud-bigquery'."

    client = bigquery.Client()
    # NOTE: Replace `your-gcp-project.your_dataset.mobile_clinic_deployments`
    # with your actual BigQuery table.
    query = """
        SELECT deployment_date, address, zip_code, services_offered
        FROM `your-gcp-project.your_dataset.mobile_clinic_deployments`
        WHERE zip_code IN UNNEST(@zipcodes)
        ORDER BY deployment_date DESC
        LIMIT 10
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ArrayQueryParameter("zipcodes", "INT64", zipcodes)]
    )
    try:
        query_job = client.query(query, job_config=job_config)
        results = [dict(row) for row in query_job]
        return str(ClinicDeploymentsOutput(deployments=results).model_dump())
    except Exception as e:
        return f"An error occurred while querying BigQuery: {e}"


mobile_clinic_agent = Agent(
    model=config.root_agent_model,
    name="mobile_clinic_agent",
    instruction="You are a data specialist. Your task is to retrieve details about mobile health clinic deployments from a BigQuery database based on a list of zip codes.",
    tools=[FunctionTool(get_mobile_clinic_deployments)],
)