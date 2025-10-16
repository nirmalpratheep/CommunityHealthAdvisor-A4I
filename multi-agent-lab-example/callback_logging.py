"""
Simple callback logging utilities for ADK agents.
"""
import logging


def log_query_to_model(callback_context, llm_request):
    """
    Logs the query being sent to the model.
    
    Args:
        callback_context: The callback context from ADK
        llm_request: The request being sent to the LLM
    """
    logging.info(f"[Query to model] Agent: {callback_context.agent_name}")
    return None


def log_model_response(callback_context, llm_response):
    """
    Logs the response received from the model.
    
    Args:
        callback_context: The callback context from ADK
        llm_response: The response from the LLM
    """
    logging.info(f"[Model response] Agent: {callback_context.agent_name}")
    return None

