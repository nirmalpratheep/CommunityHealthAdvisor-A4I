# callback_logging.py
import logging
from google.adk.runtime import callback_context

class CallbackLogger:
    """A simple logger to trace agent execution via callbacks."""
    def __init__(self, level=logging.INFO):
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s'
        )

    async def before_agent_callback(self, context: callback_context.CallbackContext):
        logging.info(f"AGENT '{context.agent_name}' received input: {context.invocation.new_message.parts.text}")

    async def before_tool_callback(self, context: callback_context.ToolContext):
        logging.info(f"AGENT '{context.agent_name}' is calling TOOL '{context.tool_name}' with args: {context.tool_args}")

    async def after_tool_callback(self, context: callback_context.ToolContext):
        # Log only a snippet of the response to avoid cluttering the console
        response_snippet = str(context.tool_response)[:200]
        logging.info(f"AGENT '{context.agent_name}' received response from TOOL '{context.tool_name}': {response_snippet}...")

    async def after_agent_callback(self, context: callback_context.CallbackContext):
        logging.info(f"AGENT '{context.agent_name}' produced final response.")