"""
AgentCore Runtime Interface
Implements AWS Lambda Runtime API for AgentCore compatibility
"""

import json
import logging
import os
import sys
import requests
import time
from typing import Dict, Any

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
    logger.info(f"Processing analytics query: {user_input}")
    
    response = f"Analytics Agent Response: I received your query '{user_input}'. This is a working analytics agent ready to process your data analysis requests!"
    
    logger.info(f"Generated response: {response}")
    return response

def lambda_handler(event: Dict[str, Any], context: Any = None) -> str:
    """
    Lambda handler function for AgentCore
    """
    try:
        logger.info("=== AgentCore Lambda Handler Started ===")
        logger.info(f"Received event: {json.dumps(event, default=str, indent=2)}")
        
        # Extract input text from various possible event structures
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
        
        # Process the analytics query
        response_text = process_analytics_query(user_input)
        
        logger.info(f"Returning response: {response_text}")
        logger.info("=== AgentCore Lambda Handler Completed Successfully ===")
        
        # Return plain text response as expected by AgentCore
        return response_text
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}", exc_info=True)
        error_message = f"Error processing request: {str(e)}"
        logger.error(f"Error response: {error_message}")
        return error_message

def runtime_loop():
    """
    AWS Lambda Runtime API loop for AgentCore
    """
    runtime_api = os.environ.get('AWS_LAMBDA_RUNTIME_API')
    
    if not runtime_api:
        logger.error("AWS_LAMBDA_RUNTIME_API environment variable not set")
        # Fallback to simple handler for testing
        test_event = {"inputText": "Test query"}
        result = lambda_handler(test_event)
        logger.info(f"Test result: {result}")
        return
    
    logger.info(f"Starting Lambda Runtime API loop with endpoint: {runtime_api}")
    
    while True:
        try:
            # Get next invocation
            response = requests.get(f"http://{runtime_api}/2018-06-01/runtime/invocation/next")
            
            if response.status_code != 200:
                logger.error(f"Failed to get next invocation: {response.status_code}")
                time.sleep(1)
                continue
            
            request_id = response.headers.get('Lambda-Runtime-Aws-Request-Id')
            event = response.json()
            
            logger.info(f"Processing request {request_id}")
            
            # Process the event
            result = lambda_handler(event)
            
            # Send response
            response_url = f"http://{runtime_api}/2018-06-01/runtime/invocation/{request_id}/response"
            requests.post(response_url, data=result)
            
            logger.info(f"Completed request {request_id}")
            
        except Exception as e:
            logger.error(f"Error in runtime loop: {str(e)}", exc_info=True)
            
            if 'request_id' in locals():
                error_url = f"http://{runtime_api}/2018-06-01/runtime/invocation/{request_id}/error"
                error_response = {
                    "errorMessage": str(e),
                    "errorType": type(e).__name__
                }
                requests.post(error_url, json=error_response)
            
            time.sleep(1)

if __name__ == '__main__':
    logger.info("Starting AgentCore Runtime Interface")
    runtime_loop()