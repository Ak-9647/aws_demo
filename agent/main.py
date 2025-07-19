"""
Production Analytics Agent - Main Entry Point
Built with LangGraph for Amazon Bedrock AgentCore
"""

import json
import logging
from typing import Dict, Any
from langgraph import StateGraph, END
from langgraph.graph import Graph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState:
    """State management for the analytics agent"""
    def __init__(self):
        self.messages = []
        self.context = {}
        self.results = {}

def analytics_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main analytics processing handler
    """
    logger.info("Processing analytics request")
    
    # Extract user query
    user_query = state.get("input", "")
    
    # Simple response for now - will be enhanced with actual analytics
    response = {
        "message": f"Hello! I received your analytics query: '{user_query}'",
        "status": "success",
        "agent_version": "1.0.0"
    }
    
    return {"output": response}

def create_agent_graph() -> Graph:
    """
    Create the LangGraph workflow for the analytics agent
    """
    # Define the graph
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("analytics", analytics_handler)
    
    # Set entry point
    workflow.set_entry_point("analytics")
    
    # Add edges
    workflow.add_edge("analytics", END)
    
    # Compile the graph
    return workflow.compile()

# Initialize the agent graph
agent_graph = create_agent_graph()

def handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Lambda/AgentCore handler function
    """
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Process the request through the agent graph
        result = agent_graph.invoke({"input": event.get("query", "Hello World")})
        
        logger.info(f"Agent response: {result}")
        
        return {
            "statusCode": 200,
            "body": json.dumps(result["output"]),
            "headers": {
                "Content-Type": "application/json"
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "message": "Internal server error"
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }

if __name__ == "__main__":
    # Test the agent locally
    test_event = {"query": "Analyze sales data for Q4"}
    result = handler(test_event)
    print(json.dumps(result, indent=2))