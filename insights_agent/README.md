# Community Health Advisor - `insights_agent`

This directory contains the `insights_agent`, a key component of the Community Health Advisor multi-agent system.

## Overall System Goal

The Community Health Advisor is a multi-agent system designed to dismantle information barriers and support data-driven health equity and crisis readiness. It aims to provide actionable intelligence to public health officials, community leaders, and healthcare providers.

## Role of the `insights_agent`

The `insights_agent` is the first step in the intelligence pipeline. Its primary responsibility is to take unstructured, raw information—such as field reports, community forum posts, or news articles—and transform it into structured, actionable insights that other agents can use to make recommendations or trigger alerts.

## Core Use Cases

The `insights_agent` is designed to identify signals related to several key public health challenges. The following are examples of the types of issues it can process:

1.  **Unequal access to healthcare facilities**: Identifying mentions of underserved populations and locations to help recommend mobile health unit routes or new clinic sites.
2.  **Environmental health risks**: Detecting correlations between pollution (air, water) or heat spikes and health complaints.
3.  **Preventable disease outbreaks**: Monitoring for early signals of disease clusters (e.g., flu, dengue) to alert health departments for rapid response.
4.  **High uninsured or low-income populations**: Helping match residents to nearby free/low-cost care providers.
5.  **Delayed crisis response**: Providing the initial analysis for real-time dashboards and alerts for emerging local crises.

## Agent Workflow

The `insights_agent` is a `SequentialAgent` that executes the following steps:

1.  **`data_structuring_agent`**:
    -   **Input**: Unstructured text (`unstructured_health_data`).
    -   **Action**: Uses an LLM to parse the text into a list of `HealthEvent` objects. Each `HealthEvent` maintains the crucial link between a specific `issue` (e.g., "flu outbreak") and its corresponding `locations` (e.g., ["90210", "downtown"]).
    -   **Output**: A structured `HealthAnalysis` object (`structured_analysis`) containing the list of health events.

2.  **`researcher_agent`**:
    -   **Input**: The `structured_analysis` object.
    -   **Action**: Iterates through each `HealthEvent` and performs targeted Google searches, combining the identified issue and location to find localized, contextual information.
    -   **Output**: A list of search results (`research_findings`).

3.  **`insights_creator_agent`**:
    -   **Input**: The `structured_analysis` and `research_findings`.
    -   **Action**: Synthesizes all available information into a final, machine-readable JSON object that conforms to the `ActionableInsight` schema.
    -   **Output**: An `ActionableInsight` object containing a summary, a categorized problem type, and a concrete recommended action. This structured output is designed to be consumed by other agents in the system.
