"""
AgentCore Handler - Alternative entry point for compatibility
"""

import json
import logging
import sys
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def process_analytics_query(user_input: str) -> str:
    """
    Process analytics query and return response
    """
    try:
        logger.info(f"Processing analytics query: '{user_input}'")
        
        # Process the analytics query
        response_text = f"Analytics Agent Response: I received your query '{user_input}'. This is a working analytics agent ready to process your data analysis requests!"
        
        logger.info(f"Generated response: {response_text}")
        return response_text
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return f"Error processing request: {str(e)}"

def lambda_handler(event: Dict[str, Any], context: Optional[Any] = None) -> str:
    """
    Lambda handler for compatibility
    """
    try:
        logger.info("=== AgentCore Lambda Handler Started ===")
        logger.info(f"Received event: {json.dumps(event, default=str, indent=2)}")
        
        user_input = "Hello World"
        
        if isinstance(event, str):
            user_input = event
        elif isinstance(event, dict):
            user_input = (
                event.get("inputText") or
                event.get("input") or 
                event.get("query") or
                event.get("message") or
                event.get("prompt") or
                event.get("payload") or
                str(event.get("body", "")) or
                "Hello World"
            )
        
        logger.info(f"Extracted user input: '{user_input}'")
        
        response = process_analytics_query(user_input)
        
        logger.info(f"Returning response: {response}")
        logger.info("=== AgentCore Lambda Handler Completed Successfully ===")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}", exc_info=True)
        error_message = f"Error processing request: {str(e)}"
        return error_message