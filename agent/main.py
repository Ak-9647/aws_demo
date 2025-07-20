"""
Production Analytics Agent - HTTP Server for AgentCore
Built for Amazon Bedrock AgentCore Runtime
"""

import json
import logging
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional

# Configure logging for CloudWatch
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
        
        # Import analytics engine
        from analytics_engine import AnalyticsEngine
        
        # Initialize analytics engine
        engine = AnalyticsEngine()
        
        # Analyze the query
        result = engine.analyze_query(user_input)
        
        if result["success"]:
            # Format the response
            response_parts = []
            response_parts.append(f"# Analytics Results\n")
            response_parts.append(result["analysis"])
            
            # Add data summary if available
            if result.get("data_summary"):
                response_parts.append(f"\n## Data Summary")
                for key, value in result["data_summary"].items():
                    response_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
            
            # Add recommendations if available
            if result.get("recommendations"):
                response_parts.append(f"\n## Recommendations")
                for i, rec in enumerate(result["recommendations"], 1):
                    response_parts.append(f"{i}. {rec}")
            
            # Add visualization info if available
            if result.get("visualizations"):
                response_parts.append(f"\n## Visualizations Generated")
                for i, viz in enumerate(result["visualizations"], 1):
                    response_parts.append(f"{i}. **{viz.get('title', 'Chart')}**: {viz.get('description', 'Data visualization')}")
                    if viz.get('chart_image'):
                        response_parts.append(f"   📊 Chart image generated successfully")
                    if viz.get('data'):
                        response_parts.append(f"   📈 Data points: {len(viz['data'])}")
            
            response_text = "\n".join(response_parts)
        else:
            response_text = f"Error analyzing query: {result.get('error', 'Unknown error')}"
        
        logger.info(f"Generated response length: {len(response_text)} characters")
        return response_text
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return f"Error processing request: {str(e)}"

class AgentHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for AgentCore
    """
    
    def do_GET(self):
        """Handle GET requests"""
        logger.info(f"GET request: {self.path}")
        
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return
        
        # Parse query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        user_input = query_params.get('query', ['Hello World'])[0]
        response = process_analytics_query(user_input)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def do_POST(self):
        """Handle POST requests"""
        logger.info(f"POST request: {self.path}")
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            logger.info(f"Received POST data: {post_data}")
            
            # Try to parse as JSON
            try:
                data = json.loads(post_data.decode('utf-8'))
                user_input = (
                    data.get("inputText") or
                    data.get("input") or 
                    data.get("query") or
                    data.get("message") or
                    data.get("prompt") or
                    data.get("payload") or
                    str(data.get("body", "")) or
                    "Hello World"
                )
            except json.JSONDecodeError:
                # Treat as plain text
                user_input = post_data.decode('utf-8') or "Hello World"
            
            response = process_analytics_query(user_input)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error handling POST request: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            error_msg = f"Error processing request: {str(e)}"
            self.wfile.write(error_msg.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"HTTP: {format % args}")

def start_server():
    """Start the HTTP server"""
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"Starting AgentCore HTTP Server on port {port}")
    
    server = HTTPServer(('0.0.0.0', port), AgentHandler)
    
    logger.info(f"AgentCore HTTP Server running on http://0.0.0.0:{port}")
    logger.info("Health check available at /health")
    logger.info("Ready to process analytics queries!")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        server.server_close()

# Legacy Lambda handler for compatibility
def lambda_handler(event: Dict[str, Any], context: Optional[Any] = None) -> str:
    """
    Legacy Lambda handler for compatibility
    """
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
    
    return process_analytics_query(user_input)

if __name__ == "__main__":
    logger.info("=== Starting Production Analytics Agent ===")
    start_server()